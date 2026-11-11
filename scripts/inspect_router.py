#!/usr/bin/env python3
"""Identify a GL-MT6000 over an existing trusted, key-authenticated SSH route.

No configuration writes, passwords, topology export, or package installation.
Requires Python 3.10+ locally and standard BusyBox/ubus tools on the router.
"""
import argparse
import ipaddress
import json
from pathlib import Path
import re
import subprocess
import sys
import threading

TOOLS = frozenset(("uci", "ubus", "ip", "fw3", "fw4", "iptables", "nft", "jsonfilter", "sysupgrade", "wg", "tc", "logread"))
MAX_CAPTURE_BYTES = 16384
SSH_TIMEOUT = 40
READ_ONLY_SCRIPT = """set -eu
printf 'FLINT2_BOARD\\n'
ubus call system board
printf '\\nFLINT2_GL_VERSION\\n'
if [ -r /etc/glversion ]; then head -n 1 /etc/glversion; fi
printf '\\nFLINT2_TOOLS\\n'
for tool in uci ubus ip fw3 fw4 iptables nft jsonfilter sysupgrade wg tc logread; do
    if command -v "$tool" >/dev/null 2>&1; then printf '%s\\n' "$tool"; fi
done
printf 'FLINT2_END\\n'
"""


def ssh_command(host, *, user="root", port=22, identity=None):
    """Build an argument list; never interpolate a destination into shell code."""
    if not isinstance(host, str) or not host or host != host.strip():
        raise ValueError("Supply an explicit router IP address or hostname")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        if len(host) > 253 or any(not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", part) for part in host.split(".")):
            raise ValueError("Invalid router hostname; pass the user and port separately")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]{0,31}", user):
        raise ValueError("Invalid SSH username")
    if not isinstance(port, int) or not 1 <= port <= 65535:
        raise ValueError("SSH port must be between 1 and 65535")
    command = ["ssh", "-T", "-o", "StrictHostKeyChecking=yes", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "-o", "ConnectionAttempts=1", "-o", "ServerAliveInterval=5", "-o", "ServerAliveCountMax=2", "-p", str(port)]
    if identity is not None:
        key = Path(identity).expanduser()
        if not key.is_file():
            raise ValueError("The explicitly selected SSH identity file does not exist")
        command.extend(["-o", "IdentitiesOnly=yes", "-i", str(key.resolve())])
    return command + [user + "@" + host, "sh", "-s"]


def parse_inventory(output):
    """Omit all raw fields except the identification allowlist."""
    if len(output) > 16384:
        raise ValueError("Unexpectedly large inventory; no raw output was retained")
    pattern = r"\AFLINT2_BOARD\n(.*?)\nFLINT2_GL_VERSION\n(.*?)\nFLINT2_TOOLS\n(.*?)FLINT2_END\n?\Z"
    match = re.fullmatch(pattern, output.replace("\r\n", "\n"), re.S)
    if not match:
        raise ValueError("Incomplete or unexpected inventory response")
    try:
        board = json.loads(match[1])
    except (ValueError, TypeError) as error:
        raise ValueError("Invalid board identification response") from error
    if not isinstance(board, dict):
        raise ValueError("Board response must be an object")
    if "GL-MT6000" not in str(board.get("model", "")).upper() or not re.search(r"(?:^|[, _-])(?:gl-)?mt6000$", str(board.get("board_name", "")), re.I):
        raise ValueError("Hardware is not an identified GL-MT6000; stop this workflow")
    version = match[2].strip()
    if not re.fullmatch(r"4\.\d+(?:\.\d+)?(?:[-+._A-Za-z0-9]*)", version):
        raise ValueError("GL.iNet 4.x firmware identity is missing or unrecognized")
    def public_value(value):
        if not isinstance(value, str) or len(value) > 160 or not re.fullmatch(r"[A-Za-z0-9 .,/_+():-]*", value):
            raise ValueError("Unexpected identification field; no raw output was retained")
        return value
    release = board.get("release", {})
    if not isinstance(release, dict):
        raise ValueError("Invalid firmware release metadata")
    tool_names = match[3].split()
    if any(name not in TOOLS for name in tool_names):
        raise ValueError("Unexpected tool inventory response")
    return {
        "schema_version": 1,
        "model": public_value(board["model"]),
        "board_name": public_value(board["board_name"]),
        "kernel": public_value(board.get("kernel", "")),
        "gl_version": version,
        "release": {key: public_value(release[key]) for key in ("distribution", "version", "revision", "target") if key in release},
        "tools": sorted(set(tool_names)),
        "scope": "read-only identification; no network topology or credentials",
    }


def run_ssh(command):
    """Drain both pipes with fixed caps; kill only this owned child on failure."""
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    output = bytearray()
    overflow = threading.Event()

    def drain(stream, retain):
        count = 0
        while True:
            block = stream.read(4096)
            if not block:
                return
            count += len(block)
            if count > MAX_CAPTURE_BYTES:
                overflow.set()
                try:
                    process.kill()
                except OSError:
                    pass
                return
            if retain:
                output.extend(block)

    readers = [threading.Thread(target=drain, args=(process.stdout, True), daemon=True), threading.Thread(target=drain, args=(process.stderr, False), daemon=True)]
    for reader in readers:
        reader.start()
    try:
        try:
            process.stdin.write(READ_ONLY_SCRIPT.encode("utf-8"))
            process.stdin.close()
        except BrokenPipeError:
            pass
        process.wait(timeout=SSH_TIMEOUT)
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=5)
        for reader in readers:
            reader.join(timeout=1)
        # A custom SSH proxy can retain inherited pipes. Do not block closing a
        # pipe that a daemon reader still owns; the short-lived CLI exits cleanly.
        if not any(reader.is_alive() for reader in readers):
            process.stdout.close()
            process.stderr.close()
        if not process.stdin.closed:
            try:
                process.stdin.close()
            except BrokenPipeError:
                pass
    if overflow.is_set():
        raise RuntimeError("SSH inspection exceeded the output limit; raw output was discarded")
    if any(reader.is_alive() for reader in readers):
        raise RuntimeError("SSH inspection output did not close; check the selected SSH route")
    return process.returncode, output.decode("utf-8")


def inspect(host, *, user="root", port=22, identity=None):
    command = ssh_command(host, user=user, port=port, identity=identity)
    try:
        returncode, output = run_ssh(command)
    except (OSError, subprocess.TimeoutExpired, UnicodeError) as error:
        raise RuntimeError("SSH inspection failed: check the trusted SSH route, key authentication, and router reachability") from error
    if returncode:
        raise RuntimeError(f"SSH inspection failed (exit {returncode}); verify host trust and authentication interactively. Raw remote output is omitted.")
    return parse_inventory(output)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", required=True, help="Explicit router IP or hostname; never defaults to a network target")
    parser.add_argument("--user", default="root")
    parser.add_argument("--port", type=int, default=22)
    parser.add_argument("--identity", help="Existing private-key file; never a password")
    parser.add_argument("--dry-run", action="store_true", help="Print argv and the fixed read-only script; do not connect")
    args = parser.parse_args(argv)
    try:
        if args.dry_run:
            result = {"argv": ssh_command(args.host, user=args.user, port=args.port, identity=args.identity), "remote_script": READ_ONLY_SCRIPT}
        else:
            result = inspect(args.host, user=args.user, port=args.port, identity=args.identity)
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

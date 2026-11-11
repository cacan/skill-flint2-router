"""Offline tests for SSH boundaries and output privacy."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import shlex
import shutil
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load_helper():
    spec = importlib.util.spec_from_file_location("inspect_router", ROOT / "scripts" / "inspect_router.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class InspectionTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((ROOT / "scripts" / "inspect_router.py").is_file(), "Inspection helper is not implemented")
        self.helper = load_helper()

    def test_rejects_destination_injection(self):
        for host in ["-oProxyCommand=evil", "root@router", "router;reboot", "router\nother", "$(id)", "", "https://router", "router:22"]:
            with self.subTest(host=host), self.assertRaises(ValueError):
                self.helper.ssh_command(host)

    def test_preserves_ssh_host_trust(self):
        for host in ["192.0.2.1", "router.example", "router", "2001:db8::1"]:
            with self.subTest(host=host):
                command = self.helper.ssh_command(host, port=2222)
                self.assertIn("root@" + host, command)
                self.assertEqual(command[-2:], ["sh", "-s"])
                self.assertIn("StrictHostKeyChecking=yes", command)
                self.assertIn("BatchMode=yes", command)

    def test_rejects_bad_user_port_and_identity(self):
        for kwargs in [{"user": "root;id"}, {"user": "-root"}, {"port": 0}, {"port": 65536}, {"identity": "missing-key-file"}]:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.helper.ssh_command("192.0.2.1", **kwargs)

    def sample_output(self, model="GL-MT6000", board_name="glinet,gl-mt6000"):
        board = {"model": model, "board_name": board_name, "kernel": "5.4.0", "hostname": "PRIVATE-HOST", "serial": "PRIVATE-SERIAL", "password": "PRIVATE-PASSWORD", "release": {"distribution": "OpenWrt", "version": "21.02-SNAPSHOT", "revision": "r-test", "target": "mediatek/filogic", "description": "PRIVATE-DESCRIPTION"}}
        return "FLINT2_BOARD\n" + json.dumps(board) + "\nFLINT2_GL_VERSION\n4.9.1\nFLINT2_TOOLS\nuci\nubus\nip\niptables\nFLINT2_END\n"

    def test_output_omits_unrequested_sensitive_fields(self):
        result = self.helper.parse_inventory(self.sample_output())
        encoded = json.dumps(result)
        self.assertNotIn("PRIVATE", encoded)
        self.assertNotIn("description", encoded)
        self.assertEqual(result["model"], "GL-MT6000")
        self.assertEqual(result["gl_version"], "4.9.1")
        self.assertEqual(result["release"]["target"], "mediatek/filogic")
        self.assertEqual(result["tools"], ["ip", "iptables", "ubus", "uci"])
        self.assertEqual(result["scope"], "read-only identification; no network topology or credentials")

    def test_unsupported_hardware_or_missing_gl_version_is_rejected(self):
        for output in [self.sample_output("GL-MT3000", "glinet,gl-mt3000"), self.sample_output().replace("4.9.1", ""), self.sample_output().replace("FLINT2_END", "")]:
            with self.subTest(output=output[:30]), self.assertRaises(ValueError):
                self.helper.parse_inventory(output)

    def test_failure_does_not_echo_remote_stderr(self):
        program = "import sys;sys.stderr.write('PRIVATE-TOKEN');sys.exit(255)"
        with patch.object(self.helper, "ssh_command", return_value=[sys.executable, "-c", program]):
            with self.assertRaisesRegex(RuntimeError, "SSH inspection failed") as error:
                self.helper.inspect("192.0.2.1")
            self.assertNotIn("PRIVATE", str(error.exception))

    def test_success_is_parsed_at_transport_boundary(self):
        program = "import sys;assert sys.stdin.read()==" + repr(self.helper.READ_ONLY_SCRIPT) + ";sys.stdout.write(" + repr(self.sample_output()) + ")"
        with patch.object(self.helper, "ssh_command", return_value=[sys.executable, "-c", program]):
            self.assertEqual(self.helper.inspect("192.0.2.1")["gl_version"], "4.9.1")

    def test_timeout_terminates_the_owned_child(self):
        program = "import time;time.sleep(30)"
        with patch.object(self.helper, "SSH_TIMEOUT", 0.1), patch.object(self.helper, "ssh_command", return_value=[sys.executable, "-c", program]):
            with self.assertRaisesRegex(RuntimeError, "SSH inspection failed"):
                self.helper.inspect("192.0.2.1")

    def test_oversized_stderr_is_rejected_even_on_success(self):
        program = "import sys;sys.stdout.write(" + repr(self.sample_output()) + ");sys.stdout.flush();sys.stderr.write('x'*1000000)"
        with patch.object(self.helper, "ssh_command", return_value=[sys.executable, "-c", program]):
            with self.assertRaisesRegex(RuntimeError, "output limit"):
                self.helper.inspect("192.0.2.1")

    def test_remote_board_command_failure_is_not_masked(self):
        shell = shutil.which("sh") or ("C:/Program Files/Git/bin/bash.exe" if Path("C:/Program Files/Git/bin/bash.exe").is_file() else None)
        if not shell:
            self.skipTest("A POSIX shell is needed for the remote-script fixture")
        board = self.sample_output().split("FLINT2_BOARD\n", 1)[1].split("\nFLINT2_GL_VERSION", 1)[0]
        fixture = "ubus() { printf '%s' " + shlex.quote(board) + "; return 7; }\n" + self.helper.READ_ONLY_SCRIPT
        result = subprocess.run([shell, "-c", fixture], capture_output=True, timeout=5, shell=False)
        self.assertEqual(result.returncode, 7, "A failed producer must not become a successful inspection")


if __name__ == "__main__":
    unittest.main()

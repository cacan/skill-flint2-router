#!/usr/bin/env python3
"""Discover official GL.iNet 4.x interface pages and write a metadata-only candidate.

Public HTTPS requests go only to docs.gl-inet.com. No router access or LLM calls.
Existing output files are never overwritten. Requires Python 3.10+.
"""
import argparse
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import time
from urllib.parse import unquote, urljoin, urlsplit, urlunsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener
from urllib.robotparser import RobotFileParser
from xml.etree import ElementTree

BASE = "https://docs.gl-inet.com"
ROOT = "/router/en/4/"
PREFIX = ROOT + "interface_guide/"
SEED = BASE + PREFIX
SITEMAP = BASE + ROOT + "sitemap.xml"
USER_AGENT = "flint2-skill-docs/1.0 (+public-documentation-catalog)"
MAX_BYTES = 2 * 1024 * 1024
EXTRAS = tuple(BASE + ROOT + path for path in ("user_guide/gl-mt6000/", "tutorials/ssh_log_in_to_the_router/", "features_update/firmware_v4.9/", "features_update/firmware_v4.10/", "features_update/firmware_v4.11/"))


def validate_url(url):
    parsed = urlsplit(url)
    decoded_path = unquote(parsed.path)
    if parsed.scheme != "https" or parsed.netloc != "docs.gl-inet.com" or parsed.query or parsed.fragment or not (parsed.path.startswith(ROOT) or parsed.path == "/robots.txt") or any(part in (".", "..") for part in decoded_path.split("/")) or "\\" in decoded_path:
        raise ValueError("URL outside the approved official HTTPS documentation scope")
    return url


class SafeRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_url(newurl)
        # A redirect can change robots applicability and content provenance.
        # Require explicit canonical-source review instead of fetching it here.
        raise ValueError("Documentation redirect requires review of the canonical URL")


def fetch_bytes(url):
    validate_url(url)
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xml,text/plain"})
    with build_opener(SafeRedirect()).open(request, timeout=25) as response:
        validate_url(response.geturl())
        if response.status != 200:
            raise ValueError("Documentation fetch requires a complete HTTP 200 response")
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("Documentation response exceeds the 2 MiB limit")
    return data


class ArticleParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_article = False
        self.in_heading = False
        self.has_article = False
        self.heading = []
        self.text = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "article":
            self.in_article = self.has_article = True
        if tag == "a" and values.get("href"):
            self.links.append(values["href"])
        if self.in_article and tag == "h1":
            self.in_heading = True

    def handle_endtag(self, tag):
        if tag == "article":
            self.in_article = False
        if tag == "h1":
            self.in_heading = False

    def handle_data(self, data):
        if self.in_article:
            self.text.append(data)
        if self.in_heading:
            self.heading.append(data)


def interface_links(links, current):
    result = set()
    for link in links:
        parsed = urlsplit(urljoin(current, link))
        if parsed.scheme != "https" or parsed.netloc != "docs.gl-inet.com" or not parsed.path.startswith(PREFIX):
            continue
        clean = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))
        validate_url(clean)
        result.add(clean)
    return result


def crawl(*, fetch=fetch_bytes, extra_urls=EXTRAS, delay=0.15, max_pages=200):
    robots = RobotFileParser()
    robots.parse(fetch(BASE + "/robots.txt").decode("utf-8").splitlines())
    if not robots.can_fetch(USER_AGENT, SEED):
        raise ValueError("robots.txt disallows this documentation crawl")
    if not robots.can_fetch(USER_AGENT, SITEMAP):
        raise ValueError("robots.txt disallows the sitemap")
    xml = fetch(SITEMAP)
    if len(xml) > MAX_BYTES or b"<!DOCTYPE" in xml.upper() or b"<!ENTITY" in xml.upper():
        raise ValueError("Unsupported sitemap input")
    tree = ElementTree.fromstring(xml)
    links = [element.text for element in tree.iter() if element.tag.endswith("}loc") or element.tag == "loc"]
    pending = interface_links([link for link in links if link], SEED) | {SEED}
    pending.update(validate_url(url) for url in extra_urls)
    records, seen, errors = [], set(), []
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    server_delay = max(robots.crawl_delay(USER_AGENT) or 0, robots.crawl_delay("*") or 0, delay)
    if server_delay > 30:
        raise ValueError("robots.txt requires a longer crawl delay; use manual retrieval")
    while pending - seen:
        if len(pending | seen) > max_pages:
            raise RuntimeError("Documentation page limit exceeded; candidate was not saved")
        url = sorted(pending - seen)[0]
        seen.add(url)
        if not robots.can_fetch(USER_AGENT, url):
            raise ValueError("robots.txt disallows a discovered documentation URL")
        if server_delay:
            time.sleep(server_delay)
        try:
            body = fetch(url)
            if len(body) > MAX_BYTES:
                raise ValueError("response too large")
            parser = ArticleParser()
            parser.feed(body.decode("utf-8"))
            title = " ".join(" ".join(parser.heading).replace("¶", "").split())
            if not parser.has_article or not title:
                raise ValueError("response is not a documentation article")
            text = " ".join(parser.text)
            records.append({"url": url, "title": title, "fetched_at": timestamp, "status": 200, "body_sha256": hashlib.sha256(body).hexdigest(), "version_mentions": sorted(set(re.findall(r"\b[vV]?4\.\d+(?:\.\d+)?\b", text)))})
            pending.update(interface_links(parser.links, url))
        except Exception:
            # Preserve completeness without printing remote bodies or exception payloads.
            errors.append(url)
    if errors:
        raise RuntimeError(f"Documentation crawl incomplete: {len(errors)} page(s) failed; no candidate was saved")
    return {"schema_version": 1, "complete": True, "fetched_at": timestamp, "scope": SEED, "discovery": [SITEMAP, SEED], "version_note": "Version mentions are search hints, not firmware compatibility guarantees.", "records": sorted(records, key=lambda record: record["url"])}


def write_snapshot(snapshot, destination):
    if not snapshot.get("complete"):
        raise ValueError("Refusing to save an incomplete candidate")
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(snapshot, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New candidate JSON path, preferably under .local/")
    args = parser.parse_args(argv)
    try:
        if args.output.exists():
            raise FileExistsError("Candidate output already exists; select a new path")
        snapshot = crawl()
        write_snapshot(snapshot, args.output)
        print(f"Saved {len(snapshot['records'])} official documentation records to {args.output}")
        return 0
    except (OSError, ValueError, RuntimeError, ElementTree.ParseError) as error:
        print(f"Refresh failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

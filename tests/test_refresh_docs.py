"""Offline crawler tests; all HTTP responses are synthetic."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import URLError
from urllib.request import Request

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://docs.gl-inet.com"
SEED = BASE + "/router/en/4/interface_guide/"
OTHER = SEED + "dns_v4.11/"
OLD = SEED + "dns/"


def load_helper():
    spec = importlib.util.spec_from_file_location("refresh_docs", ROOT / "scripts" / "refresh_docs.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RefreshTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((ROOT / "scripts" / "refresh_docs.py").is_file(), "Documentation helper is not implemented")
        self.helper = load_helper()

    def fixtures(self):
        sitemap = '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>' + SEED + '</loc></url><url><loc>' + OTHER + '</loc></url></urlset>'
        return {
            BASE + "/robots.txt": b"User-agent: *\nAllow: /\n",
            self.helper.SITEMAP: sitemap.encode(),
            SEED: b'<html><article><h1>Interface Guide</h1><a href="dns/#old">DNS</a><a href="https://example.org/foreign">Other</a></article></html>',
            OTHER: b'<html><article><h1>DNS v4.11</h1><p>Introduced in v4.11</p><a href="../dns/">Older</a></article></html>',
            OLD: b'<html><article><h1>DNS</h1><p>v4.10 and earlier</p><a href="#top">Top</a></article></html>',
        }

    def test_discovers_sitemap_and_linked_variants_without_duplicates(self):
        fixtures, calls = self.fixtures(), []
        def fetch(url):
            calls.append(url)
            return fixtures[url]
        result = self.helper.crawl(fetch=fetch, extra_urls=(), delay=0)
        self.assertEqual({r["url"] for r in result["records"]}, {SEED, OTHER, OLD})
        self.assertEqual(len(calls), 5)
        self.assertTrue(result["complete"])
        self.assertEqual(result["schema_version"], 1)
        old = next(r for r in result["records"] if r["url"] == OLD)
        self.assertEqual(old["version_mentions"], ["v4.10"])
        self.assertEqual(len(old["body_sha256"]), 64)
        self.assertNotIn("body", old)

    def test_robots_disallow_stops_before_page_requests(self):
        fixtures, seen = self.fixtures(), []
        fixtures[BASE + "/robots.txt"] = b"User-agent: *\nDisallow: /router/\n"
        def fetch(url):
            seen.append(url)
            return fixtures[url]
        with self.assertRaisesRegex(ValueError, "robots"):
            self.helper.crawl(fetch=fetch, extra_urls=(), delay=0)
        self.assertEqual(seen, [BASE + "/robots.txt"])

    def test_missing_page_fails_instead_of_claiming_complete(self):
        fixtures = self.fixtures()
        def fetch(url):
            if url == OTHER:
                raise URLError("unavailable")
            return fixtures[url]
        with self.assertRaisesRegex(RuntimeError, "incomplete"):
            self.helper.crawl(fetch=fetch, extra_urls=(), delay=0)

    def test_foreign_redirects_and_non_https_urls_are_rejected(self):
        for url in ["https://example.org/router/en/4/interface_guide/", "http://docs.gl-inet.com/router/en/4/interface_guide/", BASE + "/router/en/3/", BASE + "/router/en/4/interface_guide/../other/"]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                self.helper.validate_url(url)
        with self.assertRaises(ValueError):
            self.helper.SafeRedirect().redirect_request(None, None, 302, "", {}, "https://example.org/collect")

    def test_page_limit_and_non_document_html_fail(self):
        fixtures = self.fixtures()
        with self.assertRaisesRegex(RuntimeError, "limit"):
            self.helper.crawl(fetch=lambda u: fixtures[u], extra_urls=(), delay=0, max_pages=2)
        fixtures[OTHER] = b"<html><h1>Access denied</h1></html>"
        with self.assertRaisesRegex(RuntimeError, "incomplete"):
            self.helper.crawl(fetch=lambda u: fixtures[u], extra_urls=(), delay=0)

    def test_snapshot_write_is_exclusive(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "candidate.json"
            self.helper.write_snapshot({"complete": True}, dest)
            with self.assertRaises(FileExistsError):
                self.helper.write_snapshot({"complete": True, "changed": True}, dest)
            self.assertNotIn("changed", dest.read_text())

    def test_redirect_requires_reviewed_canonical_url(self):
        with self.assertRaisesRegex(ValueError, "redirect"):
            self.helper.SafeRedirect().redirect_request(Request(SEED), None, 302, "Moved", {}, OLD)

    def test_partial_http_response_is_not_a_successful_page(self):
        response = MagicMock()
        response.status = 206
        response.geturl.return_value = SEED
        response.read.return_value = b"<article><h1>Partial document</h1></article>"
        opener = MagicMock()
        opener.open.return_value.__enter__.return_value = response
        with patch.object(self.helper, "build_opener", return_value=opener):
            with self.assertRaisesRegex(ValueError, "HTTP 200"):
                self.helper.fetch_bytes(SEED)

    def test_transport_response_limit_is_enforced(self):
        response = MagicMock()
        response.status = 200
        response.geturl.return_value = SEED
        response.read.return_value = b"x" * (self.helper.MAX_BYTES + 1)
        opener = MagicMock()
        opener.open.return_value.__enter__.return_value = response
        with patch.object(self.helper, "build_opener", return_value=opener):
            with self.assertRaisesRegex(ValueError, "2 MiB"):
                self.helper.fetch_bytes(SEED)
        response.read.assert_called_once_with(self.helper.MAX_BYTES + 1)


if __name__ == "__main__":
    unittest.main()

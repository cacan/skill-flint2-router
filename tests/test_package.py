"""Public-package integrity checks without external dependencies or network."""
import ast
from datetime import date
import json
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]


def heading_ids(text):
    return {re.sub(r"[^\w\- ]", "", line.lower()).replace(" ", "-") for line in re.findall(r"^#{1,6}\s+(.+?)\s*$", text, re.M)}


class PackageTests(unittest.TestCase):
    def test_skill_identity_and_concise_entrypoint(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)[1]
        self.assertIn("name: skill-flint2-router", frontmatter)
        self.assertIn("GL-MT6000", frontmatter)
        self.assertLess(len(text.split()), 850)

    def test_markdown_and_html_local_links_resolve(self):
        paths = list(ROOT.glob("*.md")) + list((ROOT / "references").glob("*.md")) + list((ROOT / "repository-docs").rglob("*.md"))
        for path in paths:
            text = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.S)
            links = re.findall(r"\]\(([^)\s]+)\)", text) + re.findall(r'(?:href|src)="([^"]+)"', text)
            for target in links:
                parsed = urlsplit(target)
                if parsed.scheme or target.startswith("//"):
                    continue
                resolved = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
                with self.subTest(source=str(path.relative_to(ROOT)), link=target):
                    self.assertTrue(resolved.is_relative_to(ROOT), "Local link escapes the package")
                    self.assertTrue(resolved.is_file(), "Missing linked file")
                    if parsed.fragment and resolved.suffix == ".md":
                        self.assertIn(parsed.fragment, heading_ids(resolved.read_text(encoding="utf-8")))

    def test_catalog_is_complete_unique_and_provenance_bearing(self):
        catalog = json.loads((ROOT / "references" / "official-docs.json").read_text(encoding="utf-8"))
        self.assertTrue(catalog["complete"])
        self.assertEqual(catalog["schema_version"], 1)
        records = catalog["records"]
        self.assertEqual(len(records), len({record["url"] for record in records}))
        self.assertGreaterEqual(len(records), 87)
        self.assertGreaterEqual(sum("/interface_guide/" in record["url"] for record in records), 82)
        for record in records:
            self.assertTrue(record["url"].startswith("https://docs.gl-inet.com/router/en/4/"))
            self.assertEqual(record["status"], 200)
            self.assertRegex(record["body_sha256"], r"^[a-f0-9]{64}$")
            self.assertTrue(record["title"])
            when = record.get("fetched_on", record.get("fetched_at", "")[:10])
            self.assertLessEqual(date.fromisoformat(when), date.today())
            self.assertNotIn("body", record)

    def test_banner_is_accessible_self_contained_svg(self):
        svg = ElementTree.parse(ROOT / "assets" / "banner.svg").getroot()
        ns = {"s": "http://www.w3.org/2000/svg"}
        self.assertIsNotNone(svg.find("s:title", ns))
        self.assertIsNotNone(svg.find("s:desc", ns))
        self.assertEqual(svg.attrib["role"], "img")
        for node in svg.iter():
            self.assertNotIn(node.tag.split("}")[-1], ["script", "foreignObject", "image"])
            self.assertFalse(any(key.lower().startswith("on") for key in node.attrib))

    def test_python_sources_parse_and_no_router_binaries_are_packaged(self):
        for path in list((ROOT / "scripts").glob("*.py")) + list((ROOT / "tests").glob("*.py")):
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for path in ROOT.rglob("*"):
            if any(part in (".git", ".local", "__pycache__") for part in path.relative_to(ROOT).parts):
                continue
            self.assertNotIn(path.suffix.lower(), [".bin", ".pem", ".key", ".tgz"], str(path))


if __name__ == "__main__":
    unittest.main()

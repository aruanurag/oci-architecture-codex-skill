#!/usr/bin/env python3
"""Regression tests for finalized OCI draw.io rendering."""

from __future__ import annotations

import html
import json
import re
import tempfile
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

from render_oci_drawio import read_drawio_page_models, render_spec_to_file, validate_drawio_file

SKILL_DIR = Path(__file__).resolve().parents[1]
EXAMPLE_SPECS = SKILL_DIR / "assets" / "examples" / "specs"


class RenderDrawioTests(unittest.TestCase):
    def render_example(self, name: str) -> tuple[Path, list[dict[str, object]], dict[str, object]]:
        spec_path = EXAMPLE_SPECS / f"{name}.json"
        temp_dir = Path(tempfile.mkdtemp(prefix="oci-drawio-test-"))
        output_path = temp_dir / f"{name}.drawio"
        report_path = temp_dir / f"{name}.report.json"

        report = render_spec_to_file(spec_path, output_path, report_path)
        validation = validate_drawio_file(output_path)
        return output_path, report, validation

    def plain_values(self, output_path: Path) -> list[str]:
        values: list[str] = []
        for _, page_model in read_drawio_page_models(output_path):
            for cell in page_model.iterfind(".//mxCell"):
                raw = cell.attrib.get("value")
                if not raw:
                    continue
                plain = html.unescape(raw).replace("\xa0", " ")
                plain = re.sub(r"<br\s*/?>", " ", plain, flags=re.IGNORECASE)
                plain = re.sub(r"<[^>]+>", " ", plain)
                plain = " ".join(plain.split())
                if plain:
                    values.append(plain)
        return values

    def test_bundled_examples_default_to_single_physical_page(self) -> None:
        for spec_path in sorted(EXAMPLE_SPECS.glob("*.json")):
            spec = json.loads(spec_path.read_text())
            self.assertEqual(len(spec["pages"]), 1, spec_path.name)
            self.assertEqual(spec["pages"][0]["page_type"], "physical", spec_path.name)

    def test_physical_examples_include_vcns_and_public_private_subnets(self) -> None:
        cidr_pattern = re.compile(r"\b\d+\.\d+\.\d+\.\d+/\d+\b")

        for name in [
            "event-driven-payments-platform",
            "multi-region-oke-saas",
            "mushop-oke-ecommerce",
            "oke-genai-rag",
            "oke-multidatabase-modern-app",
        ]:
            output_path, _, validation = self.render_example(name)
            self.assertFalse(validation["issues"], name)

            values = self.plain_values(output_path)
            joined = " | ".join(values)
            public_subnets = [value for value in values if "Public" in value and cidr_pattern.search(value)]
            private_subnets = [value for value in values if "Private" in value and cidr_pattern.search(value)]

            self.assertIn("VCN", joined, name)
            self.assertTrue(public_subnets, f"{name} is missing a labeled public subnet with a CIDR.")
            self.assertTrue(private_subnets, f"{name} is missing a labeled private subnet with a CIDR.")

    def test_multi_region_oke_saas_renders_cleanly(self) -> None:
        output_path, report, validation = self.render_example("multi-region-oke-saas")

        self.assertEqual(validation["page_count"], 1)
        self.assertEqual([page["name"] for page in validation["pages"]], ["Physical - Multi-Region OKE SaaS"])
        self.assertFalse(validation["issues"])
        self.assertGreater(validation["pages"][0]["cell_count"], 110)
        self.assertTrue(
            any(row.get("icon_title") == "Physical - Special Connectors - Remote Peering - Horizontal" for row in report)
        )

        page_xml = "".join(ET.tostring(page_model, encoding="unicode") for _, page_model in read_drawio_page_models(output_path))
        self.assertIn("Primary ATP", page_xml)
        self.assertIn("Remote Peering", page_xml)

    def test_oke_genai_rag_uses_toolkit_icons(self) -> None:
        output_path, report, validation = self.render_example("oke-genai-rag")

        self.assertEqual(validation["page_count"], 1)
        self.assertFalse(validation["issues"])
        self.assertTrue(any(row.get("icon_title") == "Analytics and AI - OCI Generative AI" for row in report))
        self.assertTrue(any(row.get("icon_title") == "Analytics and AI - OCI Language" for row in report))
        self.assertTrue(any(row.get("icon_title") == "Analytics and AI - Document Understanding" for row in report))
        self.assertTrue(any(row.get("icon_title") == "Database - OCI Database with PostgreSQL" for row in report))
        self.assertTrue(any(row.get("source") == "toolkit-v24.2-icons-page" for row in report))

        page_xml = "".join(ET.tostring(page_model, encoding="unicode") for _, page_model in read_drawio_page_models(output_path))
        self.assertIn("OCI Generative AI", page_xml)
        self.assertIn("OCI PostgreSQL", page_xml)
        self.assertIn("Document Understanding", page_xml)

    def test_external_labels_hide_internal_snippet_text(self) -> None:
        temp_dir = Path(tempfile.mkdtemp(prefix="oci-drawio-test-"))
        spec_path = temp_dir / "external-labels.json"
        output_path = temp_dir / "external-labels.drawio"
        report_path = temp_dir / "external-labels.report.json"

        spec_path.write_text(
            json.dumps(
                {
                    "title": "External Labels",
                    "pages": [
                        {
                            "name": "Physical - External Labels",
                            "page_type": "physical",
                            "width": 400,
                            "height": 240,
                            "elements": [
                                {
                                    "id": "dns",
                                    "query": "DNS",
                                    "x": 120,
                                    "y": 40,
                                    "w": 90,
                                    "h": 90,
                                    "external_label": "Global DNS",
                                }
                            ],
                        }
                    ],
                }
            )
        )

        render_spec_to_file(spec_path, output_path, report_path)
        values = self.plain_values(output_path)

        self.assertIn("Global DNS", values)
        self.assertNotIn("DNS", values)

    def test_mushop_example_renders_with_reference_components(self) -> None:
        output_path, report, validation = self.render_example("mushop-oke-ecommerce")

        self.assertEqual(validation["page_count"], 1)
        self.assertEqual([page["name"] for page in validation["pages"]], ["Physical - MuShop E-Commerce on OKE"])
        self.assertFalse(validation["issues"])
        self.assertGreater(validation["pages"][0]["cell_count"], 100)
        self.assertTrue(any(row.get("icon_title") == "Identity and Security - User Group" for row in report))
        self.assertTrue(
            any(row.get("icon_title") == "Database - Autonomous Transaction Processing ATP" for row in report)
        )
        self.assertTrue(any(row.get("icon_title") == "Compute - Virtual Machine VM" for row in report))

        page_xml = "".join(ET.tostring(page_model, encoding="unicode") for _, page_model in read_drawio_page_models(output_path))
        self.assertIn("OCI Kubernetes Engine (OKE)", page_xml)
        self.assertIn("OCI Object", page_xml)

    def test_oke_multidatabase_modern_app_matches_reference_pattern(self) -> None:
        output_path, report, validation = self.render_example("oke-multidatabase-modern-app")

        self.assertEqual(validation["page_count"], 1)
        self.assertEqual(
            [page["name"] for page in validation["pages"]],
            ["Physical - OKE Multi-Database Modern App"],
        )
        self.assertFalse(validation["issues"])
        self.assertGreater(validation["pages"][0]["cell_count"], 90)
        self.assertTrue(
            any(
                row.get("element_id") == "cache"
                and row.get("resolution") == "placeholder"
                and row.get("placeholder_shape") == "cylinder"
                for row in report
            )
        )
        self.assertTrue(any(row.get("icon_title") == "Database - OCI Database with PostgreSQL" for row in report))
        self.assertTrue(any(row.get("icon_title") == "Database - OpenSearch" for row in report))
        self.assertTrue(any(row.get("icon_title") == "Networking - Customer Premises Equipment CPE" for row in report))
        self.assertTrue(any(row.get("source") == "toolkit-v24.2-icons-page" for row in report))
        self.assertTrue(
            any(
                row.get("element_id") == "internet-browser"
                and row.get("resolution") == "placeholder"
                for row in report
            )
        )

        values = self.plain_values(output_path)
        self.assertIn("OCI Cache with Valkey", values)
        self.assertIn("OCI Search with OpenSearch", values)
        self.assertIn("FastConnect", values)


if __name__ == "__main__":
    unittest.main()

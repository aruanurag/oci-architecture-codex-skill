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

from render_oci_drawio import read_drawio_page_models, render_spec_to_file, review_render_report, validate_drawio_file

SKILL_DIR = Path(__file__).resolve().parents[1]
EXAMPLE_SPECS = SKILL_DIR / "assets" / "examples" / "specs"


def build_clarification_gate(
    *,
    availability: str = "Single-region deployment decisions are either simplified for this renderer test or not materially under test.",
    database: str = "No database choice is required for this renderer test unless the specific fixture says otherwise.",
    subnet_scope: str = "Regional subnet scope is assumed unless the fixture explicitly requires AD-specific framing.",
    icon_resolution: str = "Use a direct OCI icon first, then the closest honest official fallback, then a clearly labeled placeholder.",
) -> dict[str, object]:
    return {
        "status": "satisfied",
        "notes": "Renderer test fixture clarification gate.",
        "decisions": [
            {
                "topic": "availability",
                "question": "Should this test represent HA, DR, or neither?",
                "recommended_option": "Keep the fixture as simple as possible unless the test explicitly requires HA or DR semantics.",
                "selected_option": availability,
                "resolution_source": "not_applicable",
                "rationale": "The guardrail exists to exercise renderer behavior rather than architecture discovery.",
            },
            {
                "topic": "database",
                "question": "Which database type should appear in this test?",
                "recommended_option": "If no database behavior is under test, record that no database choice is in scope.",
                "selected_option": database,
                "resolution_source": "not_applicable",
                "rationale": "The clarification gate must still record the database decision explicitly.",
            },
            {
                "topic": "subnet_scope",
                "question": "Should subnet framing be regional or AD-specific?",
                "recommended_option": "Use regional subnets unless the test explicitly requires AD-specific subnet framing.",
                "selected_option": subnet_scope,
                "resolution_source": "recommendation_accepted",
                "rationale": "Regional subnets are the default OCI assumption for these renderer fixtures.",
            },
            {
                "topic": "icon_resolution",
                "question": "If a direct icon is missing, what should this test use?",
                "recommended_option": "Use a direct OCI icon first, then the closest honest official fallback, then a clearly labeled placeholder.",
                "selected_option": icon_resolution,
                "resolution_source": "recommendation_accepted",
                "rationale": "The renderer should always have an explicit icon-resolution rule before rendering.",
            },
        ],
    }


class RenderDrawioTests(unittest.TestCase):
    def render_example(self, name: str) -> tuple[Path, list[dict[str, object]], dict[str, object]]:
        spec_path = EXAMPLE_SPECS / f"{name}.json"
        temp_dir = Path(tempfile.mkdtemp(prefix="oci-drawio-test-"))
        output_path = temp_dir / f"{name}.drawio"
        report_path = temp_dir / f"{name}.report.json"

        report = render_spec_to_file(spec_path, output_path, report_path)
        validation = validate_drawio_file(output_path)
        return output_path, report, validation

    def render_temp_spec(self, name: str, spec: dict[str, object]) -> tuple[Path, list[dict[str, object]], dict[str, object]]:
        temp_dir = Path(tempfile.mkdtemp(prefix="oci-drawio-test-"))
        spec_path = temp_dir / f"{name}.json"
        output_path = temp_dir / f"{name}.drawio"
        report_path = temp_dir / f"{name}.report.json"

        spec = dict(spec)
        spec.setdefault("clarification_gate", build_clarification_gate())
        spec_path.write_text(json.dumps(spec))
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
        quality = review_render_report(report)

        self.assertEqual(validation["page_count"], 1)
        self.assertEqual([page["name"] for page in validation["pages"]], ["Physical - Multi-Region OKE SaaS"])
        self.assertFalse(validation["issues"])
        self.assertFalse(quality["issues"])
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
        output_path, _, _ = self.render_temp_spec(
            "external-labels",
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
            },
        )
        values = self.plain_values(output_path)

        self.assertIn("Global DNS", values)
        self.assertNotIn("DNS", values)

    def test_missing_clarification_gate_is_rejected(self) -> None:
        temp_dir = Path(tempfile.mkdtemp(prefix="oci-drawio-test-"))
        spec_path = temp_dir / "missing-clarification-gate.json"
        output_path = temp_dir / "missing-clarification-gate.drawio"
        report_path = temp_dir / "missing-clarification-gate.report.json"

        spec_path.write_text(
            json.dumps(
                {
                    "title": "Missing Clarification Gate",
                    "pages": [
                        {
                            "name": "Physical - Missing Clarification Gate",
                            "page_type": "physical",
                            "width": 400,
                            "height": 240,
                            "elements": [],
                        }
                    ],
                }
            )
        )

        with self.assertRaisesRegex(ValueError, "clarification_gate"):
            render_spec_to_file(spec_path, output_path, report_path)

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

    def test_missing_icon_dimensions_normalize_to_common_size(self) -> None:
        _, report, validation = self.render_temp_spec(
            "normalized-icon-sizing",
            {
                "title": "Normalized Icon Sizing",
                "pages": [
                    {
                        "name": "Physical - Normalized Icon Sizing",
                        "page_type": "physical",
                        "width": 640,
                        "height": 240,
                        "elements": [
                            {"id": "dns", "query": "DNS", "x": 40, "y": 60},
                            {"id": "waf", "query": "WAF", "x": 180, "y": 60},
                            {"id": "vm", "query": "virtual machine", "x": 320, "y": 60},
                        ],
                    }
                ],
            },
        )

        self.assertFalse(validation["issues"])
        quality = review_render_report(report)
        self.assertFalse(quality["issues"])

        icons = {row["element_id"]: row for row in report if row.get("kind") == "library" and row.get("element_id")}
        self.assertEqual({row["size_mode"] for row in icons.values()}, {"normalized-default"})
        for icon in icons.values():
            self.assertAlmostEqual(max(float(icon["w"]), float(icon["h"])), 90.0, places=2)

    def test_quality_review_flags_stretched_icons(self) -> None:
        _, report, validation = self.render_temp_spec(
            "stretched-icon",
            {
                "title": "Stretched Icon",
                "pages": [
                    {
                        "name": "Physical - Stretched Icon",
                        "page_type": "physical",
                        "width": 420,
                        "height": 220,
                        "elements": [
                            {"id": "dns", "query": "DNS", "x": 40, "y": 60, "w": 150, "h": 50},
                            {"id": "waf", "query": "WAF", "x": 240, "y": 60, "w": 90, "h": 90},
                        ],
                    }
                ],
            },
        )

        self.assertFalse(validation["issues"])
        quality = review_render_report(report)
        self.assertIn("icon-aspect-distorted", {issue["code"] for issue in quality["issues"]})

    def test_quality_review_flags_diagonal_edge_segments(self) -> None:
        _, report, validation = self.render_temp_spec(
            "diagonal-edge",
            {
                "title": "Diagonal Edge",
                "pages": [
                    {
                        "name": "Physical - Diagonal Edge",
                        "page_type": "physical",
                        "width": 540,
                        "height": 360,
                        "elements": [
                            {"id": "waf", "query": "WAF", "x": 40, "y": 40, "w": 90, "h": 90},
                            {"id": "oke", "query": "OKE", "x": 280, "y": 220, "w": 90, "h": 90},
                            {
                                "type": "edge",
                                "id": "bad-route",
                                "source": "waf",
                                "target": "oke",
                                "source_anchor": "right",
                                "target_anchor": "left",
                                "waypoints": [{"x": 200, "y": 160}],
                            },
                        ],
                    }
                ],
            },
        )

        self.assertFalse(validation["issues"])
        quality = review_render_report(report)
        codes = {issue["code"] for issue in quality["issues"]}
        self.assertIn("edge-diagonal-segment", codes)

    def test_quality_review_accepts_clean_orthogonal_edge(self) -> None:
        _, report, validation = self.render_temp_spec(
            "clean-edge",
            {
                "title": "Clean Edge",
                "pages": [
                    {
                        "name": "Physical - Clean Edge",
                        "page_type": "physical",
                        "width": 540,
                        "height": 260,
                        "elements": [
                            {"id": "dns", "query": "DNS", "x": 40, "y": 60, "w": 90, "h": 90},
                            {"id": "lb", "query": "load balancer", "x": 280, "y": 60, "w": 90, "h": 90},
                            {
                                "type": "edge",
                                "id": "clean-route",
                                "source": "dns",
                                "target": "lb",
                                "source_anchor": "right",
                                "target_anchor": "left",
                                "waypoints": [{"x": 200, "y": 105}],
                            },
                        ],
                    }
                ],
            },
        )

        self.assertFalse(validation["issues"])
        quality = review_render_report(report)
        self.assertFalse(quality["issues"])

    def test_quality_review_flags_child_icon_outside_parent_boundary(self) -> None:
        _, report, validation = self.render_temp_spec(
            "child-outside-parent-boundary",
            {
                "title": "Child Outside Parent Boundary",
                "pages": [
                    {
                        "name": "Physical - Child Outside Parent Boundary",
                        "page_type": "physical",
                        "width": 520,
                        "height": 300,
                        "elements": [
                            {
                                "id": "app-subnet",
                                "query": "subnet",
                                "x": 40,
                                "y": 50,
                                "w": 300,
                                "h": 180,
                                "value": "<b>Private App Subnet</b><br/><font color=\"#312d2a\">10.0.1.0/24</font>",
                            },
                            {
                                "id": "app-vm",
                                "query": "virtual machine",
                                "parent": "app-subnet",
                                "x": 250,
                                "y": 55,
                                "w": 90,
                                "h": 90,
                                "external_label": "App VM",
                            },
                        ],
                    }
                ],
            },
        )

        self.assertFalse(validation["issues"])
        quality = review_render_report(report)
        self.assertIn("child-outside-parent-boundary", {issue["code"] for issue in quality["issues"]})

    def test_quality_review_flags_child_container_center_outside_parent(self) -> None:
        _, report, validation = self.render_temp_spec(
            "child-center-outside-parent",
            {
                "title": "Child Center Outside Parent",
                "pages": [
                    {
                        "name": "Physical - Child Center Outside Parent",
                        "page_type": "physical",
                        "width": 620,
                        "height": 320,
                        "elements": [
                            {
                                "id": "app-subnet",
                                "query": "subnet",
                                "x": 60,
                                "y": 60,
                                "w": 320,
                                "h": 190,
                                "value": "<b>Private App Subnet</b><br/><font color=\"#312d2a\">10.0.2.0/24</font>",
                            },
                            {
                                "id": "app-cluster-box",
                                "type": "shape",
                                "shape": "rounded-rectangle",
                                "parent": "app-subnet",
                                "x": 260,
                                "y": 35,
                                "w": 180,
                                "h": 140,
                                "label": "App container",
                            },
                        ],
                    }
                ],
            },
        )

        self.assertFalse(validation["issues"])
        quality = review_render_report(report)
        codes = {issue["code"] for issue in quality["issues"]}
        self.assertIn("child-center-outside-parent", codes)
        self.assertIn("child-outside-parent-boundary", codes)

    def test_quality_review_accepts_child_nodes_centered_within_parent_bounds(self) -> None:
        _, report, validation = self.render_temp_spec(
            "child-contained-in-parent",
            {
                "title": "Child Contained In Parent",
                "pages": [
                    {
                        "name": "Physical - Child Contained In Parent",
                        "page_type": "physical",
                        "width": 620,
                        "height": 320,
                        "elements": [
                            {
                                "id": "app-subnet",
                                "query": "subnet",
                                "x": 60,
                                "y": 60,
                                "w": 320,
                                "h": 190,
                                "value": "<b>Private App Subnet</b><br/><font color=\"#312d2a\">10.0.3.0/24</font>",
                            },
                            {
                                "id": "app-vm",
                                "query": "virtual machine",
                                "parent": "app-subnet",
                                "x": 115,
                                "y": 50,
                                "w": 90,
                                "h": 90,
                                "external_label": "App VM",
                            },
                            {
                                "id": "app-cluster-box",
                                "type": "shape",
                                "shape": "rounded-rectangle",
                                "parent": "app-subnet",
                                "x": 70,
                                "y": 30,
                                "w": 180,
                                "h": 140,
                                "label": "App container",
                            },
                        ],
                    }
                ],
            },
        )

        self.assertFalse(validation["issues"])
        quality = review_render_report(report)
        codes = {issue["code"] for issue in quality["issues"]}
        self.assertNotIn("child-center-outside-parent", codes)
        self.assertNotIn("child-outside-parent-boundary", codes)

    def test_hidden_boundary_anchors_are_reported_as_routing_primitives(self) -> None:
        _, report, validation = self.render_temp_spec(
            "boundary-anchor-routing",
            {
                "title": "Boundary Anchor Routing",
                "pages": [
                    {
                        "name": "Physical - Boundary Anchor Routing",
                        "page_type": "physical",
                        "width": 900,
                        "height": 320,
                        "elements": [
                            {
                                "id": "app-subnet",
                                "query": "subnet",
                                "x": 80,
                                "y": 70,
                                "w": 280,
                                "h": 180,
                                "value": "<b>Private App Subnet</b><br/><font color=\"#312d2a\">10.0.1.0/24</font>",
                            },
                            {
                                "id": "data-subnet",
                                "query": "subnet",
                                "x": 540,
                                "y": 70,
                                "w": 280,
                                "h": 180,
                                "value": "<b>Private Data Subnet</b><br/><font color=\"#312d2a\">10.0.2.0/24</font>",
                            },
                            {
                                "id": "app-vm",
                                "query": "virtual machine",
                                "x": 155,
                                "y": 115,
                                "w": 90,
                                "h": 90,
                                "external_label": "App VM",
                            },
                            {
                                "id": "adb",
                                "query": "ADB",
                                "x": 620,
                                "y": 115,
                                "w": 100,
                                "h": 90,
                                "external_label": "ADB",
                            },
                            {
                                "id": "app-subnet-egress-anchor",
                                "type": "shape",
                                "shape": "rounded-rectangle",
                                "x": 359,
                                "y": 159,
                                "w": 2,
                                "h": 2,
                                "label": "",
                                "style": "rounded=0;arcSize=0;fillColor=none;strokeColor=none;dashed=0;",
                            },
                            {
                                "id": "data-subnet-entry-anchor",
                                "type": "shape",
                                "shape": "rounded-rectangle",
                                "x": 539,
                                "y": 159,
                                "w": 2,
                                "h": 2,
                                "label": "",
                                "style": "rounded=0;arcSize=0;fillColor=none;strokeColor=none;dashed=0;",
                            },
                            {
                                "type": "edge",
                                "id": "app-to-egress-anchor",
                                "source": "app-vm",
                                "target": "app-subnet-egress-anchor",
                                "source_anchor": "right",
                                "target_anchor": "left",
                                "waypoints": [{"x": 320, "y": 160}],
                                "style": "endArrow=none;",
                            },
                            {
                                "type": "edge",
                                "id": "anchor-bridge",
                                "source": "app-subnet-egress-anchor",
                                "target": "data-subnet-entry-anchor",
                                "source_anchor": "right",
                                "target_anchor": "left",
                                "waypoints": [{"x": 450, "y": 160}],
                                "style": "endArrow=none;",
                            },
                            {
                                "type": "edge",
                                "id": "entry-anchor-to-adb",
                                "source": "data-subnet-entry-anchor",
                                "target": "adb",
                                "source_anchor": "right",
                                "target_anchor": "left",
                                "waypoints": [{"x": 590, "y": 160}],
                            },
                        ],
                    }
                ],
            },
        )

        self.assertFalse(validation["issues"])
        quality = review_render_report(report)
        self.assertFalse(quality["issues"])

        anchors = {
            row["element_id"]: row
            for row in report
            if row.get("element_id") in {"app-subnet-egress-anchor", "data-subnet-entry-anchor"}
        }
        self.assertEqual(set(anchors), {"app-subnet-egress-anchor", "data-subnet-entry-anchor"})
        self.assertEqual({row["role"] for row in anchors.values()}, {"anchor"})
        self.assertEqual({row["resolution"] for row in anchors.values()}, {"anchor"})
        self.assertFalse(any(row.get("resolution") == "placeholder" for row in anchors.values()))
        self.assertTrue(any(row.get("element_id") == "anchor-bridge" and row.get("kind") == "edge" for row in report))


if __name__ == "__main__":
    unittest.main()

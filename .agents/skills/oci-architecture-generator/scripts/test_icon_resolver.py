#!/usr/bin/env python3
"""Basic regression tests for OCI icon resolution."""

from __future__ import annotations

import unittest

from resolve_oci_icon import resolve_icon


class ResolveIconTests(unittest.TestCase):
    def test_oke_alias(self) -> None:
        result = resolve_icon("OKE", page="physical")
        self.assertEqual(result["resolution"], "alias")
        self.assertEqual(result["icon_title"], "Developer Services - Container Engine for Kubernetes")

    def test_adw_direct_or_alias(self) -> None:
        result = resolve_icon("Autonomous Data Warehouse", page="physical")
        self.assertIn(result["resolution"], {"direct", "alias"})
        self.assertEqual(result["icon_title"], "Database - Autonomous Data Warehouse ADW")

    def test_postgresql_toolkit_supplement(self) -> None:
        result = resolve_icon("postgresql", page="physical")
        self.assertEqual(result["resolution"], "alias")
        self.assertEqual(result["icon_title"], "Database - OCI Database with PostgreSQL")

    def test_redis_falls_back_to_placeholder_cylinder(self) -> None:
        result = resolve_icon("redis", page="physical")
        self.assertEqual(result["resolution"], "placeholder")
        self.assertEqual(result["icon_title"], None)
        self.assertEqual(result["placeholder_shape"], "cylinder")

    def test_browser_no_longer_claims_direct_icon(self) -> None:
        result = resolve_icon("browser", page="physical")
        self.assertEqual(result["resolution"], "placeholder")
        self.assertEqual(result["icon_title"], None)

    def test_fastconnect_connector(self) -> None:
        result = resolve_icon("fastconnect", page="physical")
        self.assertEqual(result["resolution"], "alias")
        self.assertEqual(result["icon_title"], "Physical - Special Connectors - FastConnect - Horizontal")

    def test_customer_premises_equipment_alias(self) -> None:
        result = resolve_icon("customer premises equipment", page="physical")
        self.assertEqual(result["resolution"], "alias")
        self.assertEqual(result["icon_title"], "Networking - Customer Premises Equipment CPE")

    def test_route_table_security_list(self) -> None:
        result = resolve_icon("route table and security list", page="physical")
        self.assertIn(result["resolution"], {"direct", "alias"})
        self.assertEqual(result["icon_title"], "Networking - Route Table and Security List")

    def test_logical_generic_third_party(self) -> None:
        result = resolve_icon("External SaaS CRM", page="logical")
        self.assertEqual(result["resolution"], "generic")
        self.assertEqual(result["icon_title"], "Logical - Components -3rd Party Non- OCI")

    def test_physical_vcn_grouping(self) -> None:
        result = resolve_icon("VCN", page="physical")
        self.assertEqual(result["resolution"], "alias")
        self.assertEqual(result["icon_title"], "Physical - Grouping - VCN")

    def test_physical_placeholder(self) -> None:
        result = resolve_icon("Jenkins Controller", page="physical")
        self.assertEqual(result["resolution"], "placeholder")
        self.assertEqual(result["placeholder_shape"], "rounded-rectangle")

    def test_network_security_placeholder_prefers_hexagon(self) -> None:
        result = resolve_icon("third-party firewall appliance", page="physical")
        self.assertEqual(result["resolution"], "placeholder")
        self.assertEqual(result["placeholder_shape"], "hexagon")


if __name__ == "__main__":
    unittest.main()

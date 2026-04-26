#!/usr/bin/env python3
"""Smoke tests for the PowerPoint reference catalog and selector."""

from __future__ import annotations

from build_powerpoint_reference_catalog import build_catalog, default_paths
from select_reference_architecture import rank_references, select_reference_bundle


def main() -> None:
    pptx_path, _, _ = default_paths()
    catalog = build_catalog(pptx_path)

    assert any(entry["slide_number"] == 32 for entry in catalog), catalog
    assert any(entry["slide_number"] == 27 for entry in catalog), catalog

    ranked = rank_references("HA OKE app with load balancer and autonomous database")
    assert ranked, ranked
    assert ranked[0]["slide_number"] == 32, ranked[:3]

    ranked = rank_references("GitOps with Argo CD on OKE using GitHub, a load balancer, and private worker nodes")
    assert ranked[0]["slide_number"] == 32, ranked[:3]

    ranked = rank_references(
        "WebLogic on OKE marketplace with Jenkins, bastion, public load balancer, private load balancer, and file storage"
    )
    assert ranked[0]["slide_number"] == 32, ranked[:3]

    ranked = rank_references(
        "secure and scalable LLM platform on OCI with Generative AI, OKE, AI database, and Object Storage"
    )
    assert ranked[0]["slide_number"] == 32, ranked[:3]

    bundle = select_reference_bundle(
        "cloud native DICOM store on OCI with Orthanc, PostgreSQL, OKE, API Gateway, FastConnect, and a hospital on premises"
    )
    assert bundle["primary"] is not None, bundle
    assert bundle["primary"]["slide_number"] == 32, bundle
    assert any(item["slide_number"] == 31 for item in bundle["supplemental"]), bundle

    bundle = select_reference_bundle(
        "cross-region disaster recovery for Exadata Database Service on Oracle Database at Azure with AKS and Data Guard"
    )
    assert bundle["primary"] is not None, bundle
    assert bundle["primary"]["slide_number"] == 31, bundle
    assert any(item["slide_number"] == 29 for item in bundle["supplemental"]), bundle

    print("PowerPoint reference catalog tests passed.")


if __name__ == "__main__":
    main()

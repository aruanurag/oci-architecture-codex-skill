#!/usr/bin/env python3
"""Select the closest Oracle PowerPoint reference layout for a new OCI architecture request."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from build_powerpoint_catalog import normalize, tokenize
from build_powerpoint_reference_catalog import build_catalog, default_paths as reference_default_paths

STOPWORDS = {
    "a",
    "an",
    "and",
    "app",
    "application",
    "architecture",
    "cloud",
    "diagram",
    "for",
    "oci",
    "of",
    "on",
    "or",
    "the",
    "this",
    "to",
    "use",
    "using",
    "with",
}

FOCUS_TAG_WEIGHTS = {
    "oke": 28,
    "three-tier": 24,
    "ha": 20,
    "cross-cloud": 20,
    "genai": 18,
    "gitops": 18,
    "argocd": 18,
    "dicom": 18,
    "weblogic": 18,
    "dual-ad": 18,
    "blank": 16,
    "canvas": 16,
    "mixed-boundary": 14,
    "network": 14,
    "compute": 14,
    "database": 14,
    "kubernetes": 14,
    "postgresql": 12,
    "opensearch": 12,
    "redis": 10,
    "internet": 10,
    "on-premises": 10,
}

PAGE_TYPE_WEIGHTS = {
    "physical": 12,
    "logical": 12,
}

ORIENTATION_WEIGHTS = {
    "landscape": 4,
    "portrait": 6,
}

REFERENCE_HINTS = {
    29: {
        "keywords": {
            "admin",
            "backup",
            "bastion",
            "data",
            "database",
            "exadata",
            "guard",
            "primary",
            "replica",
            "shared",
            "standby",
            "storage",
            "vault",
        },
        "traits": {"database-heavy", "ha"},
    },
    31: {
        "add_tags": {"cross-cloud"},
        "keywords": {
            "azure",
            "cross-cloud",
            "drg",
            "fastconnect",
            "hospital",
            "hybrid",
            "medical",
            "multicloud",
            "third-party",
            "transit",
            "vnet",
        },
        "traits": {"hybrid", "mixed-boundary"},
    },
    32: {
        "add_tags": {"argocd", "dicom", "genai", "gitops", "postgresql", "redis", "opensearch", "weblogic"},
        "keywords": {
            "api",
            "argocd",
            "cache",
            "dicom",
            "gitops",
            "gpu",
            "jenkins",
            "llm",
            "marketplace",
            "object",
            "oke",
            "opensearch",
            "orthanc",
            "pacs",
            "postgresql",
            "rag",
            "redis",
            "registry",
            "search",
            "valkey",
            "vector",
            "weblogic",
            "wls",
        },
        "traits": {"application-platform", "modern-app"},
    },
}


@dataclass
class QueryProfile:
    text: str
    normalized: str
    tokens: set[str]
    tags: set[str]
    page_type: str
    orientation: str | None


def significant_tokens(text: str) -> set[str]:
    return {token for token in tokenize(text) if token not in STOPWORDS and len(token) > 1}


def load_reference_catalog(catalog_path: Path | None = None) -> list[dict[str, Any]]:
    pptx_path, default_json, _ = reference_default_paths()
    catalog_path = catalog_path or default_json
    if catalog_path.exists():
        return json.loads(catalog_path.read_text())
    return build_catalog(pptx_path)


def enrich_reference(reference: dict[str, Any]) -> tuple[set[str], set[str], set[str]]:
    hint = REFERENCE_HINTS.get(reference.get("slide_number"), {})
    reference_tags = set(reference.get("tags", []))
    reference_tags |= {normalize(tag).replace(" ", "-") for tag in hint.get("add_tags", set()) if normalize(tag)}
    reference_tokens = set(reference.get("tokens", []))
    reference_tokens |= significant_tokens(" ".join(hint.get("keywords", [])))
    reference_traits = set(reference.get("traits", []))
    reference_traits |= {normalize(trait).replace(" ", "-") for trait in hint.get("traits", set()) if normalize(trait)}
    return reference_tags, reference_tokens, reference_traits


def build_query_profile(query: str) -> QueryProfile:
    normalized = normalize(query)
    tokens = significant_tokens(query)
    tags = set(tokens)

    if "kubernetes" in tokens or "k8s" in tokens:
        tags.update({"kubernetes", "oke"})
        tokens.add("oke")
    if "oke" in tokens:
        tags.update({"kubernetes", "oke"})
    if {"argo", "cd"} <= tokens or "argocd" in tokens or "gitops" in tokens:
        tokens.update({"argocd", "gitops", "oke"})
        tags.update({"argocd", "gitops", "kubernetes", "oke"})
    if "weblogic" in tokens or "wls" in tokens:
        tokens.update({"weblogic", "wls", "oke"})
        tags.update({"weblogic", "kubernetes", "oke"})
    if "marketplace" in tokens:
        tokens.add("oke")
        tags.update({"kubernetes", "oke"})
    if {"dicom", "orthanc", "pacs", "vna"} & tokens or "dicomweb" in tokens:
        tokens.update({"dicom", "medical", "imaging", "oke"})
        tags.update({"dicom", "kubernetes", "mixed-boundary", "oke"})
    if "genai" in tokens or "llm" in tokens or "rag" in tokens or ("generative" in tokens and "ai" in tokens):
        tokens.update({"genai", "llm", "oke"})
        tags.update({"genai", "kubernetes", "oke"})
    if {"three", "tier"} <= tokens or "3" in tokens and "tier" in tokens:
        tags.add("three-tier")
    if "multi" in tokens and "tier" in tokens:
        tags.add("three-tier")
    if "ha" in tokens or ("high" in tokens and "availability" in tokens):
        tags.add("ha")
    if "internet" in tokens:
        tags.add("internet")
    if "on" in tokens and "premises" in tokens:
        tags.add("on-premises")
    if "on-premises" in normalized:
        tags.add("on-premises")
    if "fastconnect" in tokens or "drg" in tokens:
        tags.add("mixed-boundary")
    if "azure" in tokens or "aks" in tokens or "multicloud" in tokens:
        tokens.update({"azure", "cross-cloud"})
        tags.update({"cross-cloud", "mixed-boundary"})
    if "blank" in tokens or "baseline" in tokens:
        tags.update({"blank", "canvas"})
    if "subnet" in tokens or "vcn" in tokens or "gateway" in tokens:
        tags.add("network")
    if "compute" in tokens or "vm" in tokens or "instance" in tokens:
        tags.add("compute")
    if "database" in tokens or "adb" in tokens or "postgres" in tokens or "mysql" in tokens:
        tags.add("database")
    if "postgres" in tokens or "postgresql" in tokens:
        tokens.update({"postgres", "postgresql"})
        tags.update({"database", "postgresql"})
    if "redis" in tokens or "valkey" in tokens:
        tokens.update({"redis", "valkey"})
        tags.update({"database", "redis"})
    if "opensearch" in tokens:
        tags.update({"database", "opensearch"})
    if {"postgres", "redis", "opensearch"} <= tokens or {"postgresql", "redis", "opensearch"} <= tokens:
        tags.update({"three-tier", "kubernetes", "oke"})

    page_type = "logical" if "logical" in tokens else "physical"
    orientation = None
    if "portrait" in tokens:
        orientation = "portrait"
    elif "landscape" in tokens:
        orientation = "landscape"

    return QueryProfile(
        text=query,
        normalized=normalized,
        tokens=tokens,
        tags=tags,
        page_type=page_type,
        orientation=orientation,
    )


def score_reference(reference: dict[str, Any], query: str | QueryProfile) -> dict[str, Any]:
    profile = query if isinstance(query, QueryProfile) else build_query_profile(query)

    reference_tags, reference_tokens, reference_traits = enrich_reference(reference)

    matched_tags = sorted(profile.tags & reference_tags)
    matched_tokens = sorted(profile.tokens & reference_tokens)
    tag_score = sum(FOCUS_TAG_WEIGHTS.get(tag, 3) for tag in matched_tags)
    token_score = min(len(matched_tokens) * 3, 24)

    page_type_score = PAGE_TYPE_WEIGHTS.get(reference.get("page_type", ""), 0) if reference.get("page_type") == profile.page_type else -8
    orientation_score = 0
    if profile.orientation:
        orientation_score = ORIENTATION_WEIGHTS.get(reference.get("orientation", ""), 0) if reference.get("orientation") == profile.orientation else -4
    elif reference.get("orientation") == "landscape":
        orientation_score = 2
    elif reference.get("orientation") == "portrait":
        orientation_score = -6

    trait_score = 0
    if "oke" in profile.tags and "oke" in reference_traits:
        trait_score += 12
    if "network" in profile.tags and "network" in reference_traits:
        trait_score += 8
    if "ha" in profile.tags and "ha" in reference_traits:
        trait_score += 10
    if "cross-cloud" in profile.tags and {"hybrid", "mixed-boundary"} & reference_traits:
        trait_score += 12
    if {"genai", "argocd", "gitops", "weblogic", "dicom"} & profile.tags and "application-platform" in reference_traits:
        trait_score += 6
    if "canvas" in reference_traits and not matched_tags:
        trait_score += 2

    score = tag_score + token_score + page_type_score + orientation_score + trait_score
    return {
        **reference,
        "score": score,
        "matched_tags": matched_tags,
        "matched_tokens": matched_tokens,
        "score_breakdown": {
            "tags": tag_score,
            "tokens": token_score,
            "page_type": page_type_score,
            "orientation": orientation_score,
            "traits": trait_score,
        },
    }


def rank_references(query: str, catalog_path: Path | None = None) -> list[dict[str, Any]]:
    profile = build_query_profile(query)
    catalog = load_reference_catalog(catalog_path)
    ranked = [score_reference(reference, profile) for reference in catalog]
    return sorted(ranked, key=lambda item: (-item["score"], item["slide_number"], item["title"]))


def select_reference_bundle(query: str, catalog_path: Path | None = None) -> dict[str, Any]:
    ranked = rank_references(query, catalog_path)
    primary = ranked[0] if ranked else None
    if primary is None:
        return {"primary": None, "supplemental": [], "uncovered_tags": []}

    covered_tags = set(primary["matched_tags"])
    supplemental: list[dict[str, Any]] = []
    for candidate in ranked[1:]:
        new_tag_coverage = sorted(tag for tag in candidate["matched_tags"] if tag not in covered_tags)
        if not new_tag_coverage:
            continue
        enriched = dict(candidate)
        enriched["new_tag_coverage"] = new_tag_coverage
        supplemental.append(enriched)
        covered_tags.update(new_tag_coverage)
        if len(supplemental) >= 3:
            break

    uncovered_tags = sorted(build_query_profile(query).tags - covered_tags)
    return {
        "primary": primary,
        "supplemental": supplemental,
        "uncovered_tags": uncovered_tags,
    }


def print_ranked_item(index: int, item: dict[str, Any]) -> None:
    print(f"{index}. {item['title']} (slide {item['slide_number']}, score {item['score']})")
    print(f"   page type: {item['page_type']} | orientation: {item['orientation']}")
    if item.get("matched_tags"):
        print(f"   matched tags: {', '.join(item['matched_tags'])}")
    if item.get("matched_tokens"):
        print(f"   matched tokens: {', '.join(item['matched_tokens'][:10])}")
    print(f"   layout notes: {item['layout_notes']}")
    if item.get("sample_labels"):
        print(f"   sample labels: {', '.join(item['sample_labels'][:8])}")


def main() -> None:
    _, default_json, _ = reference_default_paths()

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", help="Architecture description to match against the bundled PowerPoint references.")
    parser.add_argument("--top", type=int, default=5, help="How many matches to print.")
    parser.add_argument("--catalog-path", type=Path, default=default_json, help="PowerPoint reference catalog path.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of human-readable text.")
    parser.add_argument("--bundle", action="store_true", help="Recommend one primary PowerPoint baseline plus supporting slides.")
    parser.add_argument("--catalog", action="store_true", help="Print the discovered PowerPoint reference catalog.")
    args = parser.parse_args()

    if args.catalog:
        print(json.dumps(load_reference_catalog(args.catalog_path), indent=2))
        return

    if not args.query:
        raise SystemExit("--query is required unless --catalog is used.")

    if args.bundle:
        bundle = select_reference_bundle(args.query, args.catalog_path)
        if args.json:
            print(json.dumps(bundle, indent=2))
            return
        print("Primary PowerPoint baseline:")
        if bundle["primary"] is not None:
            print_ranked_item(1, bundle["primary"])
        if bundle["supplemental"]:
            print("")
            print("Supporting PowerPoint baselines:")
            for index, item in enumerate(bundle["supplemental"], start=1):
                print_ranked_item(index, item)
                if item.get("new_tag_coverage"):
                    print(f"   coverage gain: {', '.join(item['new_tag_coverage'])}")
                if index != len(bundle["supplemental"]):
                    print("")
        if bundle["uncovered_tags"]:
            print("")
            print(f"Uncovered query tags: {', '.join(bundle['uncovered_tags'])}")
        return

    ranked = rank_references(args.query, args.catalog_path)[: max(args.top, 1)]
    if args.json:
        print(json.dumps(ranked, indent=2))
        return

    for index, item in enumerate(ranked, start=1):
        print_ranked_item(index, item)


if __name__ == "__main__":
    main()

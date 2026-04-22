#!/usr/bin/env python3
"""Render OCI architecture JSON specs into finalized draw.io files."""

from __future__ import annotations

import argparse
import base64
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import html
import json
import re
from pathlib import Path
from typing import Any
import urllib.parse
import xml.etree.ElementTree as ET
import zlib

from build_icon_catalog import SUPPLEMENTAL_ICONS, normalize, tokenize
from resolve_oci_icon import resolve_icon

DEFAULT_PAGE_WIDTH = 1600
DEFAULT_PAGE_HEIGHT = 900

TEXT_STYLE = (
    "whiteSpace=wrap;html=1;strokeColor=none;fillColor=none;align=center;"
    "verticalAlign=middle;fontFamily=Oracle Sans;fontSize=11;fontColor=#312D2A;"
)

PLACEHOLDER_STYLES = {
    "rounded-rectangle": (
        "rounded=1;whiteSpace=wrap;html=1;arcSize=10;fillColor=#FCFBFA;"
        "strokeColor=#9E9892;fontColor=#312D2A;fontFamily=Oracle Sans;"
        "fontSize=11;dashed=1;dashPattern=4 4;"
    ),
    "cylinder": (
        "shape=cylinder;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;"
        "fillColor=#FCFBFA;strokeColor=#9E9892;fontColor=#312D2A;"
        "fontFamily=Oracle Sans;fontSize=11;dashed=1;dashPattern=4 4;"
    ),
    "hexagon": (
        "shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;"
        "fillColor=#FCFBFA;strokeColor=#9E9892;fontColor=#312D2A;"
        "fontFamily=Oracle Sans;fontSize=11;dashed=1;dashPattern=4 4;"
    ),
    "cloud": (
        "shape=cloud;whiteSpace=wrap;html=1;fillColor=#FCFBFA;strokeColor=#9E9892;"
        "fontColor=#312D2A;fontFamily=Oracle Sans;fontSize=11;dashed=1;"
        "dashPattern=4 4;"
    ),
    "ellipse": (
        "ellipse;whiteSpace=wrap;html=1;fillColor=#FCFBFA;strokeColor=#9E9892;"
        "fontColor=#312D2A;fontFamily=Oracle Sans;fontSize=11;dashed=1;"
        "dashPattern=4 4;"
    ),
}

CONNECTOR_STYLES = {
    "physical": (
        "endArrow=open;html=1;startArrow=none;startFill=0;endFill=0;rounded=0;"
        "fontFamily=Oracle Sans;fontSize=10.5;fontColor=#312D2A;"
        "labelBackgroundColor=none;strokeColor=#312D2A;"
        "edgeStyle=orthogonalEdgeStyle;orthogonalLoop=1;jettySize=auto;"
        "jumpStyle=gap;jumpSize=6;endSize=6;elbow=vertical;"
    ),
    "logical-dataflow": (
        "endArrow=open;html=1;startArrow=none;startFill=0;endFill=0;rounded=0;"
        "fontFamily=Oracle Sans;fontSize=10.5;fontColor=#312D2A;"
        "labelBackgroundColor=none;strokeColor=#312D2A;"
        "edgeStyle=orthogonalEdgeStyle;orthogonalLoop=1;jettySize=auto;"
        "jumpStyle=gap;jumpSize=6;endSize=6;elbow=vertical;"
    ),
    "logical-user": (
        "endArrow=open;html=1;startArrow=none;startFill=0;endFill=0;rounded=0;"
        "fontFamily=Oracle Sans;fontSize=10.5;fontColor=#312D2A;"
        "labelBackgroundColor=none;strokeColor=#312D2A;"
        "edgeStyle=orthogonalEdgeStyle;orthogonalLoop=1;jettySize=auto;"
        "jumpStyle=gap;jumpSize=6;dashed=1;endSize=6;elbow=vertical;"
    ),
}

CONNECTOR_KEY_ALIASES = {
    "physical": "physical",
    "physical connector": "physical",
    "logical": "logical-dataflow",
    "logical dataflow": "logical-dataflow",
    "logical-dataflow": "logical-dataflow",
    "dataflow": "logical-dataflow",
    "logical user": "logical-user",
    "logical-user": "logical-user",
    "logical user interaction": "logical-user",
    "user interaction": "logical-user",
    "user": "logical-user",
}

ANCHOR_POINTS = {
    "left": ("0", "0.5"),
    "right": ("1", "0.5"),
    "top": ("0.5", "0"),
    "bottom": ("0.5", "1"),
}

VCN_LIKE_TITLES = {
    "Physical - Grouping - VCN",
    "Physical - Grouping - Subnet",
}

HORIZONTAL_SPECIAL_CONNECTOR_TITLES = {
    "Physical - Special Connectors - FastConnect - Horizontal",
    "Physical - Special Connectors - Remote Peering - Horizontal",
}


@dataclass
class Snippet:
    title: str
    source: str
    cells: list[ET.Element]
    root_ids: list[str]
    text_cell_ids: list[str]
    width: float
    height: float


@dataclass
class ToolkitIndex:
    cells: list[ET.Element]
    by_id: dict[str, ET.Element]
    children: dict[str, list[str]]
    positions: dict[str, tuple[float, float]]
    root_ids: list[str]
    texts_by_root: dict[str, list[str]]


def parse_number(value: str | None, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    return float(value)


def format_number(value: float) -> str:
    rounded = round(value, 2)
    if abs(rounded - round(rounded)) < 1e-9:
        return str(int(round(rounded)))
    return f"{rounded:.2f}".rstrip("0").rstrip(".")


def strip_html(value: str) -> str:
    cleaned = html.unescape(value or "").replace("\xa0", " ")
    cleaned = re.sub(r"<br\s*/?>", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    return " ".join(cleaned.split())


def text_to_html(value: str) -> str:
    return html.escape(value).replace("\n", "<br>")


def append_style(style: str, additions: dict[str, str] | str | None = None) -> str:
    if not additions:
        return style

    if isinstance(additions, str):
        extra = additions.strip().strip(";")
    else:
        extra = ";".join(f"{key}={value}" for key, value in additions.items() if value is not None)
    if not extra:
        return style
    if style and not style.endswith(";"):
        style += ";"
    return style + extra + ";"


def encode_diagram(xml_text: str) -> str:
    encoded = urllib.parse.quote(xml_text, safe="~()*!.'")
    compressor = zlib.compressobj(level=9, wbits=-15)
    compressed = compressor.compress(encoded.encode("utf-8")) + compressor.flush()
    return base64.b64encode(compressed).decode("ascii")


def decode_diagram(payload: str) -> str:
    text = (payload or "").strip()
    if text.startswith("<mxGraphModel"):
        return text
    return urllib.parse.unquote(zlib.decompress(base64.b64decode(text), -15).decode("utf-8"))


def flatten_graph_cells(graph_root: ET.Element) -> list[ET.Element]:
    cells: list[ET.Element] = []
    for child in graph_root:
        if child.tag == "mxCell":
            cells.append(deepcopy(child))
            continue

        nested = child.find("mxCell")
        if nested is None:
            continue

        merged = ET.Element("mxCell")
        for key, value in nested.attrib.items():
            merged.set(key, value)

        if "id" not in merged.attrib and child.attrib.get("id"):
            merged.set("id", child.attrib["id"])

        if "value" not in merged.attrib:
            if child.attrib.get("value") is not None:
                merged.set("value", child.attrib["value"])
            elif child.attrib.get("label") is not None:
                merged.set("value", child.attrib["label"])

        for grandchild in nested:
            merged.append(deepcopy(grandchild))

        cells.append(merged)

    return cells


def build_cell_indexes(cells: list[ET.Element]) -> tuple[dict[str, ET.Element], dict[str, list[str]]]:
    by_id: dict[str, ET.Element] = {}
    children: dict[str, list[str]] = {}

    for cell in cells:
        cell_id = cell.attrib.get("id")
        if not cell_id:
            raise ValueError("Encountered a cell without an id.")
        by_id[cell_id] = cell
        parent = cell.attrib.get("parent")
        if parent:
            children.setdefault(parent, []).append(cell_id)

    return by_id, children


def build_absolute_positions(by_id: dict[str, ET.Element]) -> dict[str, tuple[float, float]]:
    cache: dict[str, tuple[float, float]] = {}

    def resolve(cell_id: str) -> tuple[float, float]:
        if cell_id in cache:
            return cache[cell_id]

        cell = by_id[cell_id]
        geometry = cell.find("mxGeometry")
        x = parse_number(geometry.attrib.get("x")) if geometry is not None else 0.0
        y = parse_number(geometry.attrib.get("y")) if geometry is not None else 0.0
        parent = cell.attrib.get("parent")

        if parent and parent in by_id and parent not in {"0", "1"}:
            parent_x, parent_y = resolve(parent)
            x += parent_x
            y += parent_y

        cache[cell_id] = (x, y)
        return cache[cell_id]

    for cell_id in by_id:
        resolve(cell_id)

    return cache


def collect_descendant_ids(root_id: str, children: dict[str, list[str]]) -> list[str]:
    ordered: list[str] = []
    stack = list(reversed(children.get(root_id, [])))

    while stack:
        current = stack.pop()
        ordered.append(current)
        stack.extend(reversed(children.get(current, [])))

    return ordered


def cell_bbox(cell_id: str, by_id: dict[str, ET.Element], positions: dict[str, tuple[float, float]]) -> tuple[float, float, float, float]:
    cell = by_id[cell_id]
    geometry = cell.find("mxGeometry")
    x, y = positions[cell_id]
    width = parse_number(geometry.attrib.get("width")) if geometry is not None else 0.0
    height = parse_number(geometry.attrib.get("height")) if geometry is not None else 0.0
    return x, y, x + width, y + height


def build_snippet(title: str, source: str, cells: list[ET.Element], root_ids: list[str]) -> Snippet:
    by_id, children = build_cell_indexes(cells)
    positions = build_absolute_positions(by_id)

    selected_ids: list[str] = []
    for root_id in root_ids:
        selected_ids.append(root_id)
        selected_ids.extend(collect_descendant_ids(root_id, children))

    selected_set = set(selected_ids)
    ordered_cells = [deepcopy(cell) for cell in cells if cell.attrib["id"] in selected_set]
    ordered_by_id = {cell.attrib["id"]: cell for cell in ordered_cells}

    min_x = float("inf")
    min_y = float("inf")
    max_x = 0.0
    max_y = 0.0

    for cell_id in selected_ids:
        x1, y1, x2, y2 = cell_bbox(cell_id, by_id, positions)
        min_x = min(min_x, x1)
        min_y = min(min_y, y1)
        max_x = max(max_x, x2)
        max_y = max(max_y, y2)

    if min_x == float("inf"):
        min_x = 0.0
        min_y = 0.0

    for root_id in root_ids:
        geometry = ordered_by_id[root_id].find("mxGeometry")
        if geometry is None:
            continue
        new_x = parse_number(geometry.attrib.get("x")) - min_x
        new_y = parse_number(geometry.attrib.get("y")) - min_y
        geometry.set("x", format_number(new_x))
        geometry.set("y", format_number(new_y))

    text_rows: list[tuple[float, float, str]] = []
    for cell_id in selected_ids:
        value = ordered_by_id[cell_id].attrib.get("value", "")
        plain = strip_html(value)
        if not plain:
            continue
        abs_x, abs_y = positions[cell_id]
        text_rows.append((abs_y - min_y, abs_x - min_x, cell_id))

    text_rows.sort()
    width = max(max_x - min_x, 1.0)
    height = max(max_y - min_y, 1.0)

    return Snippet(
        title=title,
        source=source,
        cells=ordered_cells,
        root_ids=list(root_ids),
        text_cell_ids=[cell_id for _, _, cell_id in text_rows],
        width=width,
        height=height,
    )


def parse_library_snippets(library_path: Path) -> dict[str, Snippet]:
    content = library_path.read_text()
    match = re.search(r"<mxlibrary>(.*)</mxlibrary>", content, re.DOTALL)
    if not match:
        raise ValueError(f"Could not find <mxlibrary> payload in {library_path}")

    snippets: dict[str, Snippet] = {}
    for raw_item in json.loads(match.group(1)):
        title = " ".join(html.unescape(raw_item.get("title", "")).replace("\xa0", " ").split())
        encoded_xml = raw_item.get("xml")
        if not title or not encoded_xml:
            continue
        xml_text = decode_diagram(encoded_xml)
        model = ET.fromstring(xml_text)
        cells = flatten_graph_cells(model.find("root"))
        root_ids = [cell.attrib["id"] for cell in cells if cell.attrib.get("parent") == "1"]
        snippets[title] = build_snippet(title, "oci-library.xml", cells, root_ids)

    return snippets


def build_toolkit_index(toolkit_path: Path) -> ToolkitIndex:
    mxfile = ET.fromstring(toolkit_path.read_text())
    icons_page = None
    for diagram in mxfile.findall("diagram"):
        if diagram.attrib.get("name") == "Icons":
            icons_page = diagram
            break

    if icons_page is None:
        raise ValueError(f"Could not find Icons page in {toolkit_path}")

    model = ET.fromstring(decode_diagram(icons_page.text or ""))
    cells = flatten_graph_cells(model.find("root"))
    by_id, children = build_cell_indexes(cells)
    positions = build_absolute_positions(by_id)
    root_ids = [cell_id for cell_id, cell in by_id.items() if cell.attrib.get("parent") == "1"]
    texts_by_root: dict[str, list[str]] = {}

    for root_id in root_ids:
        text_rows: list[tuple[float, float, str]] = []
        for cell_id in [root_id, *collect_descendant_ids(root_id, children)]:
            plain = strip_html(by_id[cell_id].attrib.get("value", ""))
            if not plain:
                continue
            abs_x, abs_y = positions[cell_id]
            text_rows.append((abs_y, abs_x, plain))
        text_rows.sort()
        texts_by_root[root_id] = [plain for _, _, plain in text_rows]

    return ToolkitIndex(
        cells=cells,
        by_id=by_id,
        children=children,
        positions=positions,
        root_ids=root_ids,
        texts_by_root=texts_by_root,
    )


def score_toolkit_candidate(target_name: str, texts: list[str]) -> float:
    if not texts:
        return 0.0

    target_norm = normalize(target_name)
    target_tokens = set(tokenize(target_name))
    best = 0.0
    candidates: list[str] = [" ".join(texts), *texts]

    if len(texts) > 2:
        for start in range(len(texts)):
            for end in range(start + 2, len(texts) + 1):
                candidates.append(" ".join(texts[start:end]))

    seen: set[str] = set()
    for candidate in candidates:
        candidate_norm = normalize(candidate)
        if not candidate_norm or candidate_norm in seen:
            continue
        seen.add(candidate_norm)
        candidate_tokens = set(tokenize(candidate))

        if candidate_norm == target_norm:
            return 1.0

        if candidate_norm in target_norm or target_norm in candidate_norm:
            best = max(best, 0.95)

        overlap = len(candidate_tokens & target_tokens)
        if overlap:
            ratio = overlap / max(len(target_tokens), 1)
            if candidate_tokens <= target_tokens or target_tokens <= candidate_tokens:
                ratio += 0.1
            best = max(best, min(ratio, 0.89))

    return best


class SnippetCatalog:
    def __init__(self, skill_dir: Path) -> None:
        self.skill_dir = skill_dir
        self.library_path = skill_dir / "assets" / "drawio" / "oci-library.xml"
        self.toolkit_path = skill_dir / "assets" / "drawio" / "oci-architecture-toolkit-v24.2.drawio"
        self.library_snippets = parse_library_snippets(self.library_path)
        self.toolkit_index: ToolkitIndex | None = None
        self.toolkit_cache: dict[str, Snippet] = {}
        self.toolkit_titles = {entry["title"] for entry in SUPPLEMENTAL_ICONS}

    def get(self, title: str) -> Snippet:
        if title in self.library_snippets:
            return self.library_snippets[title]
        if title in self.toolkit_cache:
            return self.toolkit_cache[title]
        if title not in self.toolkit_titles:
            raise KeyError(f"Icon title not found in bundled OCI assets: {title}")

        snippet = self._extract_toolkit_snippet(title)
        self.toolkit_cache[title] = snippet
        return snippet

    def _extract_toolkit_snippet(self, title: str) -> Snippet:
        if self.toolkit_index is None:
            self.toolkit_index = build_toolkit_index(self.toolkit_path)

        assert self.toolkit_index is not None
        target_name = title.split(" - ", 1)[1] if " - " in title else title
        best_root_id = None
        best_score = 0.0
        best_area = float("inf")

        for root_id in self.toolkit_index.root_ids:
            texts = self.toolkit_index.texts_by_root.get(root_id, [])
            score = score_toolkit_candidate(target_name, texts)
            if score <= 0:
                continue
            x1, y1, x2, y2 = cell_bbox(root_id, self.toolkit_index.by_id, self.toolkit_index.positions)
            area = max(x2 - x1, 1.0) * max(y2 - y1, 1.0)
            if score > best_score or (abs(score - best_score) < 1e-9 and area < best_area):
                best_root_id = root_id
                best_score = score
                best_area = area

        if best_root_id is None or best_score < 0.6:
            raise KeyError(
                f"Could not locate a toolkit snippet for '{title}'. "
                f"Best score was {round(best_score, 3)}."
            )

        return build_snippet(
            title=title,
            source="toolkit-v24.2-icons-page",
            cells=self.toolkit_index.cells,
            root_ids=[best_root_id],
        )


def new_graph_model(width: float, height: float) -> ET.Element:
    model = ET.Element(
        "mxGraphModel",
        {
            "dx": format_number(width),
            "dy": format_number(height),
            "grid": "1",
            "gridSize": "10",
            "guides": "1",
            "tooltips": "1",
            "connect": "1",
            "arrows": "1",
            "fold": "1",
            "page": "1",
            "pageScale": "1",
            "pageWidth": format_number(width),
            "pageHeight": format_number(height),
            "math": "0",
            "shadow": "0",
        },
    )
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})
    return model


class DrawioRenderer:
    def __init__(self, catalog: SnippetCatalog) -> None:
        self.catalog = catalog
        self._next_id = 2

    def _new_id(self) -> str:
        value = f"cell-{self._next_id}"
        self._next_id += 1
        return value

    def render_spec(self, spec: dict[str, Any]) -> tuple[ET.Element, list[dict[str, Any]]]:
        self._next_id = 2
        created = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        mxfile = ET.Element(
            "mxfile",
            {
                "host": "app.diagrams.net",
                "modified": created,
                "agent": "Codex OCI architecture renderer",
                "version": "24.2.5",
                "type": "device",
            },
        )

        report: list[dict[str, Any]] = []
        pages = spec.get("pages", [])
        for index, page in enumerate(pages, start=1):
            diagram, page_report = self.render_page(page, index)
            mxfile.append(diagram)
            report.extend(page_report)

        return mxfile, report

    def render_page(self, page: dict[str, Any], page_number: int) -> tuple[ET.Element, list[dict[str, Any]]]:
        width = float(page.get("width", DEFAULT_PAGE_WIDTH))
        height = float(page.get("height", DEFAULT_PAGE_HEIGHT))
        page_type = str(page.get("page_type", "physical"))
        page_name = str(page.get("name", f"Page {page_number}"))
        model = new_graph_model(width, height)
        root = model.find("root")
        assert root is not None

        placed: dict[str, dict[str, Any]] = {}
        report: list[dict[str, Any]] = []

        elements = page.get("elements", [])
        node_elements = [element for element in elements if self._element_kind(element) != "edge"]
        edge_elements = [element for element in elements if self._element_kind(element) == "edge"]

        for element in node_elements:
            record = self._render_non_edge(root, element, page_type, placed)
            record["page"] = page_name
            report.append(record)

        for element in edge_elements:
            record = self._render_edge(root, element, page_type, placed)
            record["page"] = page_name
            report.append(record)

        diagram = ET.Element("diagram", {"id": f"page-{page_number}", "name": page_name})
        diagram.text = encode_diagram(ET.tostring(model, encoding="unicode"))
        return diagram, report

    def _element_kind(self, element: dict[str, Any]) -> str:
        kind = str(element.get("type", "")).strip().lower()
        if kind:
            if kind in {"library", "icon", "container", "service"}:
                return "library"
            if kind in {"shape", "placeholder"}:
                return "shape"
            if kind == "text":
                return "text"
            if kind == "edge":
                return "edge"
            return kind

        if "source" in element and "target" in element:
            return "edge"
        if element.get("shape") or element.get("placeholder_shape"):
            return "shape"
        if element.get("text") and not element.get("query") and not element.get("icon_title"):
            return "text"
        return "library"

    def _resolve_position(self, element: dict[str, Any], placed: dict[str, dict[str, Any]]) -> tuple[float, float]:
        x = float(element.get("x", 0))
        y = float(element.get("y", 0))
        parent_ref = element.get("parent")
        if parent_ref:
            if parent_ref not in placed:
                raise KeyError(f"Parent reference '{parent_ref}' was used before it was placed.")
            x += placed[parent_ref]["x"]
            y += placed[parent_ref]["y"]
        return x, y

    def _render_non_edge(
        self,
        root: ET.Element,
        element: dict[str, Any],
        page_type: str,
        placed: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        kind = self._element_kind(element)
        if kind == "text":
            return self._render_text(root, element, placed)
        if kind == "shape":
            return self._render_shape(root, element, placed, resolution="placeholder")
        return self._render_library(root, element, page_type, placed)

    def _render_text(self, root: ET.Element, element: dict[str, Any], placed: dict[str, dict[str, Any]]) -> dict[str, Any]:
        x, y = self._resolve_position(element, placed)
        width = float(element.get("w", element.get("width", 120)))
        height = float(element.get("h", element.get("height", 20)))
        text = str(element.get("text", element.get("label", element.get("value", ""))))
        style = append_style(TEXT_STYLE, element.get("style"))
        value = text if element.get("html") else text_to_html(text)

        cell_id = self._new_id()
        cell = ET.Element(
            "mxCell",
            {
                "id": cell_id,
                "value": value,
                "style": style,
                "vertex": "1",
                "parent": "1",
            },
        )
        ET.SubElement(
            cell,
            "mxGeometry",
            {
                "x": format_number(x),
                "y": format_number(y),
                "width": format_number(width),
                "height": format_number(height),
                "as": "geometry",
            },
        )
        root.append(cell)

        if element.get("id"):
            placed[str(element["id"])] = {
                "x": x,
                "y": y,
                "w": width,
                "h": height,
                "cell_id": cell_id,
            }

        return {
            "element_id": element.get("id"),
            "kind": "text",
            "resolution": "text",
            "icon_title": None,
            "source": None,
            "query": None,
        }

    def _render_shape(
        self,
        root: ET.Element,
        element: dict[str, Any],
        placed: dict[str, dict[str, Any]],
        resolution: str,
        query: str | None = None,
    ) -> dict[str, Any]:
        x, y = self._resolve_position(element, placed)
        width = float(element.get("w", element.get("width", 110)))
        height = float(element.get("h", element.get("height", 70)))
        shape_name = str(element.get("shape", element.get("placeholder_shape", "rounded-rectangle")))
        style = PLACEHOLDER_STYLES.get(shape_name)
        if style is None:
            raise KeyError(f"Unsupported placeholder shape: {shape_name}")
        style = append_style(style, element.get("style"))
        label = str(element.get("label", element.get("value", element.get("text", ""))))

        cell_id = self._new_id()
        cell = ET.Element(
            "mxCell",
            {
                "id": cell_id,
                "value": text_to_html(label),
                "style": style,
                "vertex": "1",
                "parent": "1",
            },
        )
        ET.SubElement(
            cell,
            "mxGeometry",
            {
                "x": format_number(x),
                "y": format_number(y),
                "width": format_number(width),
                "height": format_number(height),
                "as": "geometry",
            },
        )
        root.append(cell)

        if element.get("id"):
            placed[str(element["id"])] = {
                "x": x,
                "y": y,
                "w": width,
                "h": height,
                "cell_id": cell_id,
            }

        return {
            "element_id": element.get("id"),
            "kind": "shape",
            "resolution": resolution,
            "icon_title": None,
            "source": None,
            "query": query,
            "placeholder_shape": shape_name,
        }

    def _render_library(
        self,
        root: ET.Element,
        element: dict[str, Any],
        page_type: str,
        placed: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        query = element.get("query")
        icon_title = element.get("icon_title") or element.get("title")
        source = "explicit"
        resolution = "direct"

        if not icon_title and not query:
            raise ValueError("Library elements must provide either 'query' or 'icon_title'.")

        if not icon_title:
            result = resolve_icon(str(query), page=str(element.get("page", page_type)))
            resolution = result["resolution"]
            source = result.get("source")
            if resolution == "placeholder":
                placeholder_label = str(element.get("label", result.get("label_template", f"PLACEHOLDER: {query}")))
                placeholder_element = dict(element)
                placeholder_element["placeholder_shape"] = result["placeholder_shape"]
                placeholder_element["label"] = placeholder_label
                record = self._render_shape(root, placeholder_element, placed, resolution="placeholder", query=str(query))
                record["closest_official_icon"] = result.get("closest_official_icon")
                return record
            icon_title = result["icon_title"]

        snippet = self.catalog.get(str(icon_title))
        x, y = self._resolve_position(element, placed)
        width = float(element.get("w", element.get("width", snippet.width)))
        height = float(element.get("h", element.get("height", snippet.height)))

        if str(icon_title) in VCN_LIKE_TITLES:
            primary_cell_id = self._place_vcn_like_snippet(root, snippet, x, y, width, height, element)
        elif str(icon_title) in HORIZONTAL_SPECIAL_CONNECTOR_TITLES:
            primary_cell_id = self._place_horizontal_special_connector(root, snippet, x, y, width, height, element)
        else:
            primary_cell_id = self._place_generic_snippet(root, snippet, x, y, width, height, element)

        if element.get("external_label"):
            self._render_text(
                root,
                {
                    "x": x,
                    "y": y + height + float(element.get("external_label_offset", 6)),
                    "w": width,
                    "h": float(element.get("external_label_height", 20)),
                    "text": str(element["external_label"]),
                },
                placed,
            )

        if element.get("id"):
            placed[str(element["id"])] = {
                "x": x,
                "y": y,
                "w": width,
                "h": height,
                "cell_id": primary_cell_id,
            }

        return {
            "element_id": element.get("id"),
            "kind": "library",
            "resolution": resolution,
            "icon_title": icon_title,
            "source": source if source != "explicit" else snippet.source,
            "query": query,
        }

    def _instantiate_snippet(
        self,
        snippet: Snippet,
    ) -> tuple[dict[str, str], dict[str, ET.Element], list[ET.Element]]:
        id_map: dict[str, str] = {}
        originals = {cell.attrib["id"]: cell for cell in snippet.cells}
        clones: list[ET.Element] = []

        for cell in snippet.cells:
            id_map[cell.attrib["id"]] = self._new_id()

        for cell in snippet.cells:
            clone = deepcopy(cell)
            old_id = cell.attrib["id"]
            clone.set("id", id_map[old_id])

            parent = cell.attrib.get("parent")
            if parent in id_map:
                clone.set("parent", id_map[parent])
            elif parent:
                clone.set("parent", parent)

            for ref in ("source", "target"):
                target = cell.attrib.get(ref)
                if target in id_map:
                    clone.set(ref, id_map[target])

            clones.append(clone)

        return id_map, originals, clones

    def _scale_geometry(
        self,
        original: ET.Element,
        clone: ET.Element,
        scale_x: float,
        scale_y: float,
        translate_x: float = 0.0,
        translate_y: float = 0.0,
        is_root: bool = False,
    ) -> None:
        original_geo = original.find("mxGeometry")
        clone_geo = clone.find("mxGeometry")
        if original_geo is None or clone_geo is None:
            return

        def assign(attr: str, factor: float, translation: float) -> None:
            if attr in original_geo.attrib:
                value = parse_number(original_geo.attrib[attr]) * factor + translation
                clone_geo.set(attr, format_number(value))
            elif translation:
                clone_geo.set(attr, format_number(translation))

        assign("x", scale_x, translate_x if is_root else 0.0)
        assign("y", scale_y, translate_y if is_root else 0.0)
        if "width" in original_geo.attrib:
            clone_geo.set("width", format_number(parse_number(original_geo.attrib["width"]) * scale_x))
        if "height" in original_geo.attrib:
            clone_geo.set("height", format_number(parse_number(original_geo.attrib["height"]) * scale_y))

        for index, original_child in enumerate(list(original_geo)):
            if index >= len(clone_geo):
                break
            clone_child = clone_geo[index]
            if clone_child.tag == "mxPoint":
                if "x" in original_child.attrib:
                    value = parse_number(original_child.attrib["x"]) * scale_x + (translate_x if is_root else 0.0)
                    clone_child.set("x", format_number(value))
                if "y" in original_child.attrib:
                    value = parse_number(original_child.attrib["y"]) * scale_y + (translate_y if is_root else 0.0)
                    clone_child.set("y", format_number(value))
            elif clone_child.tag == "Array":
                for point_index, original_point in enumerate(list(original_child)):
                    if point_index >= len(clone_child):
                        break
                    clone_point = clone_child[point_index]
                    if "x" in original_point.attrib:
                        value = parse_number(original_point.attrib["x"]) * scale_x
                        clone_point.set("x", format_number(value))
                    if "y" in original_point.attrib:
                        value = parse_number(original_point.attrib["y"]) * scale_y
                        clone_point.set("y", format_number(value))

    def _apply_text_overrides(
        self,
        snippet: Snippet,
        originals: dict[str, ET.Element],
        clones_by_old_id: dict[str, ET.Element],
        element: dict[str, Any],
    ) -> bool:
        if element.get("text_values"):
            values = list(element["text_values"])
            for cell_id, value in zip(snippet.text_cell_ids, values):
                clones_by_old_id[cell_id].set("value", str(value))
            return True

        if element.get("value") is not None and snippet.text_cell_ids:
            clones_by_old_id[snippet.text_cell_ids[0]].set("value", str(element["value"]))
            return True

        if element.get("label") is not None and len(snippet.text_cell_ids) == 1 and element.get("label_mode") != "external":
            clones_by_old_id[snippet.text_cell_ids[0]].set("value", text_to_html(str(element["label"])))
            return True

        hide_internal_label = element.get("hide_internal_label")
        if hide_internal_label is None:
            hide_internal_label = bool(element.get("external_label")) and not bool(element.get("preserve_internal_label"))
        if hide_internal_label and snippet.text_cell_ids:
            for cell_id in snippet.text_cell_ids:
                clones_by_old_id[cell_id].set("value", "")
            return True

        return False

    def _append_clones(
        self,
        root: ET.Element,
        clones: list[ET.Element],
    ) -> None:
        for clone in clones:
            root.append(clone)

    def _primary_root_id(self, snippet: Snippet, id_map: dict[str, str]) -> str:
        return id_map[snippet.root_ids[0]]

    def _place_generic_snippet(
        self,
        root: ET.Element,
        snippet: Snippet,
        x: float,
        y: float,
        width: float,
        height: float,
        element: dict[str, Any],
    ) -> str:
        id_map, originals, clones = self._instantiate_snippet(snippet)
        clones_by_old_id = {original_id: clone for original_id, clone in zip(originals, clones)}
        scale_x = width / snippet.width
        scale_y = height / snippet.height

        for old_id, original in originals.items():
            self._scale_geometry(
                original,
                clones_by_old_id[old_id],
                scale_x,
                scale_y,
                translate_x=x,
                translate_y=y,
                is_root=old_id in snippet.root_ids,
            )

        self._apply_text_overrides(snippet, originals, clones_by_old_id, element)
        self._append_clones(root, clones)
        return self._primary_root_id(snippet, id_map)

    def _place_vcn_like_snippet(
        self,
        root: ET.Element,
        snippet: Snippet,
        x: float,
        y: float,
        width: float,
        height: float,
        element: dict[str, Any],
    ) -> str:
        id_map, originals, clones = self._instantiate_snippet(snippet)
        clones_by_old_id = {original_id: clone for original_id, clone in zip(originals, clones)}
        delta_width = width - snippet.width

        text_ids = set(snippet.text_cell_ids)

        for old_id, original in originals.items():
            clone = clones_by_old_id[old_id]
            original_geo = original.find("mxGeometry")
            clone_geo = clone.find("mxGeometry")
            if original_geo is None or clone_geo is None:
                continue

            if old_id in snippet.root_ids:
                clone_geo.set("x", format_number(x))
                clone_geo.set("y", format_number(y))
                clone_geo.set("width", format_number(width))
                clone_geo.set("height", format_number(height))
                continue

            old_x = parse_number(original_geo.attrib.get("x"))
            old_y = parse_number(original_geo.attrib.get("y"))
            old_width = parse_number(original_geo.attrib.get("width"))
            old_height = parse_number(original_geo.attrib.get("height"))

            if old_id in text_ids:
                clone_geo.set("x", format_number(old_x))
                clone_geo.set("y", format_number(old_y))
                clone_geo.set("width", format_number(width))
                clone_geo.set("height", format_number(max(height - old_y, old_height)))
            elif "shape=image" in original.attrib.get("style", ""):
                clone_geo.set("x", format_number(old_x + delta_width))
                clone_geo.set("y", format_number(old_y))
                clone_geo.set("width", format_number(old_width))
                clone_geo.set("height", format_number(old_height))
            else:
                self._scale_geometry(
                    original,
                    clone,
                    width / snippet.width,
                    height / snippet.height,
                    is_root=False,
                )

        self._apply_text_overrides(snippet, originals, clones_by_old_id, element)
        self._append_clones(root, clones)
        return self._primary_root_id(snippet, id_map)

    def _place_horizontal_special_connector(
        self,
        root: ET.Element,
        snippet: Snippet,
        x: float,
        y: float,
        width: float,
        height: float,
        element: dict[str, Any],
    ) -> str:
        id_map, originals, clones = self._instantiate_snippet(snippet)
        clones_by_old_id = {original_id: clone for original_id, clone in zip(originals, clones)}
        scale_y = height / snippet.height
        delta_width = width - snippet.width

        for old_id, original in originals.items():
            clone = clones_by_old_id[old_id]
            original_geo = original.find("mxGeometry")
            clone_geo = clone.find("mxGeometry")
            if original_geo is None or clone_geo is None:
                continue

            if old_id in snippet.root_ids:
                clone_geo.set("x", format_number(x))
                clone_geo.set("y", format_number(y))
                clone_geo.set("width", format_number(width))
                clone_geo.set("height", format_number(height))
                continue

            old_x = parse_number(original_geo.attrib.get("x"))
            old_y = parse_number(original_geo.attrib.get("y"))
            old_width = parse_number(original_geo.attrib.get("width"))
            old_height = parse_number(original_geo.attrib.get("height"))

            if original.attrib.get("edge") == "1":
                self._scale_geometry(original, clone, 1.0, scale_y, is_root=False)
                for point in clone_geo.findall("mxPoint"):
                    if point.attrib.get("as") == "sourcePoint":
                        point.set("x", format_number(width))
                    if "y" in point.attrib:
                        point.set("y", format_number(parse_number(point.attrib["y"]) * scale_y))
            elif strip_html(original.attrib.get("value", "")):
                clone_geo.set("x", format_number(max((width - old_width) / 2, 0)))
                clone_geo.set("y", format_number(old_y * scale_y))
                clone_geo.set("width", format_number(old_width))
                clone_geo.set("height", format_number(old_height * scale_y))
            elif "shape=image" in original.attrib.get("style", ""):
                clone_geo.set("x", format_number(old_x + max(delta_width, 0)))
                clone_geo.set("y", format_number(old_y * scale_y))
                clone_geo.set("width", format_number(old_width))
                clone_geo.set("height", format_number(old_height * scale_y))
            else:
                self._scale_geometry(original, clone, width / snippet.width, scale_y, is_root=False)

        self._apply_text_overrides(snippet, originals, clones_by_old_id, element)
        self._append_clones(root, clones)
        return self._primary_root_id(snippet, id_map)

    def _render_edge(
        self,
        root: ET.Element,
        element: dict[str, Any],
        page_type: str,
        placed: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        source_ref = str(element["source"])
        target_ref = str(element["target"])
        if source_ref not in placed:
            raise KeyError(f"Edge source '{source_ref}' is not a placed element.")
        if target_ref not in placed:
            raise KeyError(f"Edge target '{target_ref}' is not a placed element.")

        connector_key = self._normalize_connector_key(element.get("connector"), page_type)
        style = CONNECTOR_STYLES[connector_key]

        source_anchor = element.get("source_anchor")
        target_anchor = element.get("target_anchor")
        additions: dict[str, str] = {}

        if source_anchor in ANCHOR_POINTS:
            additions.update(
                {
                    "exitX": ANCHOR_POINTS[str(source_anchor)][0],
                    "exitY": ANCHOR_POINTS[str(source_anchor)][1],
                    "exitDx": "0",
                    "exitDy": "0",
                }
            )
        if target_anchor in ANCHOR_POINTS:
            additions.update(
                {
                    "entryX": ANCHOR_POINTS[str(target_anchor)][0],
                    "entryY": ANCHOR_POINTS[str(target_anchor)][1],
                    "entryDx": "0",
                    "entryDy": "0",
                }
            )

        style = append_style(style, additions)
        style = append_style(style, element.get("style"))

        cell_id = self._new_id()
        edge = ET.Element(
            "mxCell",
            {
                "id": cell_id,
                "value": text_to_html(str(element.get("label", ""))),
                "style": style,
                "edge": "1",
                "parent": "1",
                "source": placed[source_ref]["cell_id"],
                "target": placed[target_ref]["cell_id"],
            },
        )

        geometry = ET.SubElement(edge, "mxGeometry", {"relative": "1", "as": "geometry"})
        if element.get("waypoints"):
            array = ET.SubElement(geometry, "Array", {"as": "points"})
            for waypoint in element["waypoints"]:
                if isinstance(waypoint, dict):
                    point_x = float(waypoint["x"])
                    point_y = float(waypoint["y"])
                else:
                    point_x = float(waypoint[0])
                    point_y = float(waypoint[1])
                ET.SubElement(
                    array,
                    "mxPoint",
                    {"x": format_number(point_x), "y": format_number(point_y)},
                )

        root.append(edge)

        return {
            "element_id": element.get("id"),
            "kind": "edge",
            "resolution": connector_key,
            "icon_title": None,
            "source": None,
            "query": None,
        }

    def _normalize_connector_key(self, connector: Any, page_type: str) -> str:
        if connector is None:
            return "physical" if page_type == "physical" else "logical-dataflow"
        normalized = normalize(str(connector))
        key = CONNECTOR_KEY_ALIASES.get(normalized)
        if key is None:
            raise KeyError(f"Unsupported connector style: {connector}")
        return key


def render_spec_to_file(spec_path: Path, output_path: Path, report_path: Path | None = None) -> list[dict[str, Any]]:
    spec = json.loads(spec_path.read_text())
    skill_dir = Path(__file__).resolve().parents[1]
    renderer = DrawioRenderer(SnippetCatalog(skill_dir))
    mxfile, report = renderer.render_spec(spec)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(ET.tostring(mxfile, encoding="unicode"))

    if report_path is not None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + "\n")

    return report


def read_drawio_page_models(drawio_path: Path) -> list[tuple[str, ET.Element]]:
    mxfile = ET.fromstring(drawio_path.read_text())
    pages: list[tuple[str, ET.Element]] = []
    for diagram in mxfile.findall("diagram"):
        page_name = diagram.attrib.get("name", "")
        model = ET.fromstring(decode_diagram(diagram.text or ""))
        pages.append((page_name, model))
    return pages


def validate_drawio_file(drawio_path: Path) -> dict[str, Any]:
    issues: list[str] = []
    pages: list[dict[str, Any]] = []

    for page_name, model in read_drawio_page_models(drawio_path):
        graph_root = model.find("root")
        if graph_root is None:
            issues.append(f"Page '{page_name}' is missing <root>.")
            continue

        cells = flatten_graph_cells(graph_root)
        ids = [cell.attrib.get("id", "") for cell in cells]
        id_set = set(ids)

        if "0" not in id_set or "1" not in id_set:
            issues.append(f"Page '{page_name}' is missing base ids 0/1.")

        if len(ids) != len(id_set):
            issues.append(f"Page '{page_name}' contains duplicate cell ids.")

        for cell in cells:
            cell_id = cell.attrib.get("id", "")
            parent = cell.attrib.get("parent")
            if parent and parent not in id_set and parent != "0":
                issues.append(f"Page '{page_name}' cell '{cell_id}' has unknown parent '{parent}'.")
            for ref in ("source", "target"):
                target = cell.attrib.get(ref)
                if target and target not in id_set:
                    issues.append(f"Page '{page_name}' cell '{cell_id}' has unknown {ref} '{target}'.")

        pages.append({"name": page_name, "cell_count": len(cells)})

    return {"page_count": len(pages), "pages": pages, "issues": issues}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True, help="Path to the JSON diagram spec.")
    parser.add_argument("--output", type=Path, required=True, help="Output .drawio file path.")
    parser.add_argument("--report-out", type=Path, help="Optional JSON report path.")
    args = parser.parse_args()

    report = render_spec_to_file(args.spec, args.output, args.report_out)
    physical = sum(1 for row in report if row["kind"] == "library" and row["resolution"] in {"direct", "alias", "closest"})
    placeholders = sum(1 for row in report if row.get("resolution") == "placeholder")
    print(f"Rendered {len({row['page'] for row in report})} page(s) to {args.output}")
    print(f"Official OCI elements: {physical}")
    print(f"Placeholders: {placeholders}")
    if args.report_out:
        print(f"Report: {args.report_out}")


if __name__ == "__main__":
    main()

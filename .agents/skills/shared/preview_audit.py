#!/usr/bin/env python3
"""Review OCI architecture preview images for visual regressions."""

from __future__ import annotations

import argparse
import json
import math
import struct
import zlib
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SUPPORTED_COLOR_TYPES = {2, 6}
ICON_FOREGROUND_THRESHOLD = 0.012
ICON_VISIBILITY_WARNING_THRESHOLD = 0.02
PAGE_FOREGROUND_WARNING_THRESHOLD = 0.0075
TEXT_CARD_RATIO_THRESHOLD = 1.5
TEXT_EDGE_PADDING = 3.0


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))


def quantize_channel(value: int, step: int = 24) -> int:
    return int(clamp(round(value / step) * step, 0, 255))


def quantize_rgb(pixel: tuple[int, int, int, int]) -> tuple[int, int, int]:
    return (
        quantize_channel(pixel[0]),
        quantize_channel(pixel[1]),
        quantize_channel(pixel[2]),
    )


def color_distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    return math.sqrt(
        ((a[0] - b[0]) ** 2) +
        ((a[1] - b[1]) ** 2) +
        ((a[2] - b[2]) ** 2)
    )


def luminance(pixel: tuple[int, int, int, int]) -> float:
    return (0.2126 * pixel[0]) + (0.7152 * pixel[1]) + (0.0722 * pixel[2])


def saturation(pixel: tuple[int, int, int, int]) -> int:
    return max(pixel[0], pixel[1], pixel[2]) - min(pixel[0], pixel[1], pixel[2])


class SimplePNG:
    def __init__(self, width: int, height: int, channels: int, rows: list[bytearray]) -> None:
        self.width = width
        self.height = height
        self.channels = channels
        self.rows = rows

    @classmethod
    def load(cls, path: Path) -> "SimplePNG":
        data = path.read_bytes()
        if not data.startswith(PNG_SIGNATURE):
            raise ValueError(f"{path} is not a PNG file.")

        offset = len(PNG_SIGNATURE)
        width = height = bit_depth = color_type = None
        idat_chunks: list[bytes] = []

        while offset < len(data):
            if offset + 8 > len(data):
                raise ValueError("Unexpected end of PNG while reading chunk header.")
            length = struct.unpack(">I", data[offset:offset + 4])[0]
            chunk_type = data[offset + 4:offset + 8]
            chunk_start = offset + 8
            chunk_end = chunk_start + length
            crc_end = chunk_end + 4
            if crc_end > len(data):
                raise ValueError("Unexpected end of PNG while reading chunk body.")

            chunk_data = data[chunk_start:chunk_end]
            if chunk_type == b"IHDR":
                width, height, bit_depth, color_type, compression, png_filter, interlace = struct.unpack(
                    ">IIBBBBB", chunk_data
                )
                if bit_depth != 8:
                    raise ValueError(f"Unsupported PNG bit depth: {bit_depth}.")
                if color_type not in SUPPORTED_COLOR_TYPES:
                    raise ValueError(f"Unsupported PNG color type: {color_type}.")
                if compression != 0 or png_filter != 0 or interlace != 0:
                    raise ValueError("Unsupported PNG compression, filter, or interlace mode.")
            elif chunk_type == b"IDAT":
                idat_chunks.append(chunk_data)
            elif chunk_type == b"IEND":
                break
            offset = crc_end

        if width is None or height is None or color_type is None:
            raise ValueError("PNG is missing IHDR.")
        if not idat_chunks:
            raise ValueError("PNG is missing IDAT data.")

        channels = 3 if color_type == 2 else 4
        stride = width * channels
        raw = zlib.decompress(b"".join(idat_chunks))
        rows: list[bytearray] = []
        cursor = 0
        previous = bytearray(stride)

        for _ in range(height):
            if cursor >= len(raw):
                raise ValueError("PNG scanline data is truncated.")
            filter_type = raw[cursor]
            cursor += 1
            row = bytearray(raw[cursor:cursor + stride])
            cursor += stride
            if len(row) != stride:
                raise ValueError("PNG scanline data is truncated.")

            reconstructed = bytearray(stride)
            if filter_type == 0:
                reconstructed[:] = row
            elif filter_type == 1:
                for index in range(stride):
                    left = reconstructed[index - channels] if index >= channels else 0
                    reconstructed[index] = (row[index] + left) & 0xFF
            elif filter_type == 2:
                for index in range(stride):
                    reconstructed[index] = (row[index] + previous[index]) & 0xFF
            elif filter_type == 3:
                for index in range(stride):
                    left = reconstructed[index - channels] if index >= channels else 0
                    up = previous[index]
                    reconstructed[index] = (row[index] + ((left + up) // 2)) & 0xFF
            elif filter_type == 4:
                for index in range(stride):
                    left = reconstructed[index - channels] if index >= channels else 0
                    up = previous[index]
                    up_left = previous[index - channels] if index >= channels else 0
                    predictor = paeth_predictor(left, up, up_left)
                    reconstructed[index] = (row[index] + predictor) & 0xFF
            else:
                raise ValueError(f"Unsupported PNG filter type: {filter_type}.")

            rows.append(reconstructed)
            previous = reconstructed

        return cls(width=width, height=height, channels=channels, rows=rows)

    def pixel(self, x: int, y: int) -> tuple[int, int, int, int]:
        row = self.rows[y]
        start = x * self.channels
        if self.channels == 3:
            return row[start], row[start + 1], row[start + 2], 255
        return row[start], row[start + 1], row[start + 2], row[start + 3]

    def sample_bbox(self, bbox: dict[str, float], scale_x: float, scale_y: float, max_samples: int = 2600) -> dict[str, Any]:
        x0 = int(clamp(math.floor(bbox["x"] * scale_x), 0, self.width - 1))
        y0 = int(clamp(math.floor(bbox["y"] * scale_y), 0, self.height - 1))
        x1 = int(clamp(math.ceil((bbox["x"] + bbox["w"]) * scale_x), x0 + 1, self.width))
        y1 = int(clamp(math.ceil((bbox["y"] + bbox["h"]) * scale_y), y0 + 1, self.height))

        pixel_area = max((x1 - x0) * (y1 - y0), 1)
        step = max(1, int(math.sqrt(pixel_area / max_samples)))
        samples: list[tuple[int, int, int, int]] = []
        for y in range(y0, y1, step):
            for x in range(x0, x1, step):
                samples.append(self.pixel(x, y))

        return summarize_samples(samples)

    def sample_page(self, max_samples: int = 15000) -> dict[str, Any]:
        pixel_area = max(self.width * self.height, 1)
        step = max(1, int(math.sqrt(pixel_area / max_samples)))
        samples: list[tuple[int, int, int, int]] = []
        for y in range(0, self.height, step):
            for x in range(0, self.width, step):
                samples.append(self.pixel(x, y))
        return summarize_samples(samples)


def paeth_predictor(left: int, up: int, up_left: int) -> int:
    prediction = left + up - up_left
    left_distance = abs(prediction - left)
    up_distance = abs(prediction - up)
    up_left_distance = abs(prediction - up_left)
    if left_distance <= up_distance and left_distance <= up_left_distance:
        return left
    if up_distance <= up_left_distance:
        return up
    return up_left


def summarize_samples(samples: list[tuple[int, int, int, int]]) -> dict[str, Any]:
    visible = [pixel for pixel in samples if pixel[3] > 16]
    if not visible:
        return {
            "sample_count": 0,
            "foreground_ratio": 0.0,
            "dominant_color": (255, 255, 255),
            "dark_ratio": 0.0,
            "colorful_ratio": 0.0,
        }

    buckets = Counter(quantize_rgb(pixel) for pixel in visible)
    dominant_bucket, _ = buckets.most_common(1)[0]
    foreground = 0
    dark_pixels = 0
    colorful_pixels = 0

    for pixel in visible:
        rgb = (pixel[0], pixel[1], pixel[2])
        if color_distance(rgb, dominant_bucket) > 24:
            foreground += 1
        if luminance(pixel) < 232:
            dark_pixels += 1
        if saturation(pixel) > 18:
            colorful_pixels += 1

    foreground_ratio = foreground / len(visible)
    dark_ratio = dark_pixels / len(visible)
    colorful_ratio = colorful_pixels / len(visible)
    return {
        "sample_count": len(visible),
        "foreground_ratio": foreground_ratio,
        "dominant_color": dominant_bucket,
        "dark_ratio": dark_ratio,
        "colorful_ratio": colorful_ratio,
    }


def load_spec_page_dimensions(
    spec_path: Path | None,
    page_name: str | None,
    default_width: float,
    default_height: float,
) -> tuple[float, float]:
    if spec_path is None:
        return default_width, default_height
    spec = json.loads(spec_path.read_text())
    pages = spec.get("pages")
    if not isinstance(pages, list) or not pages:
        return default_width, default_height

    selected_page: dict[str, Any] | None = None
    if page_name:
        for page in pages:
            if page.get("name") == page_name:
                selected_page = page
                break
    if selected_page is None:
        selected_page = pages[0]

    return (
        float(selected_page.get("width", default_width)),
        float(selected_page.get("height", default_height)),
    )


def normalize_report_page(report_path: Path, page_name: str | None) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    raw = json.loads(report_path.read_text())
    if isinstance(raw, dict) and isinstance(raw.get("pages"), list):
        pages = raw["pages"]
        selected = None
        if page_name:
            for page in pages:
                if page.get("page") == page_name:
                    selected = page
                    break
        if selected is None:
            selected = pages[0]
        page_label = str(selected.get("page") or page_name or "page-1")
        return page_label, list(selected.get("elements", [])), list(selected.get("edges", []))

    if isinstance(raw, list):
        by_page: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for record in raw:
            by_page[str(record.get("page") or "page-1")].append(record)
        if not by_page:
            raise ValueError(f"{report_path} does not contain any report rows.")
        selected_name = page_name if page_name in by_page else sorted(by_page)[0]
        rows = by_page[selected_name]
        elements = [normalize_drawio_element(row) for row in rows if row.get("kind") != "edge"]
        element_by_id = {
            identifier_for_element(element): element
            for element in elements
        }
        edges = [
            normalize_drawio_edge(row, element_by_id)
            for row in rows
            if row.get("kind") == "edge"
        ]
        return selected_name, elements, edges

    raise ValueError(f"Unsupported report structure in {report_path}.")


def normalize_drawio_element(row: dict[str, Any]) -> dict[str, Any]:
    bbox = {
        "x": float(row.get("x", 0.0)),
        "y": float(row.get("y", 0.0)),
        "w": float(row.get("w", 0.0)),
        "h": float(row.get("h", 0.0)),
    }
    resolution = {
        "query": row.get("query"),
        "resolution": row.get("resolution"),
        "icon_title": row.get("icon_title"),
        "category": row.get("icon_title"),
        "source": row.get("source"),
    }
    return {
        "id": row.get("element_id") or row.get("cell_id"),
        "cell_id": row.get("cell_id"),
        "parent": row.get("parent_element_id"),
        "bbox": bbox,
        "kind": row.get("kind"),
        "role": row.get("role"),
        "visible": True,
        "qa_ignore": bool(row.get("qa_ignore")),
        "resolution": resolution,
        "category": row.get("icon_title"),
        "boundary_parent": None,
        "boundary_side": None,
    }


def anchor_point(bbox: dict[str, float], side: str | None) -> tuple[float, float]:
    x = bbox["x"]
    y = bbox["y"]
    w = bbox["w"]
    h = bbox["h"]
    if side == "left":
        return x, y + (h / 2)
    if side == "right":
        return x + w, y + (h / 2)
    if side == "top":
        return x + (w / 2), y
    if side == "bottom":
        return x + (w / 2), y + h
    return x + (w / 2), y + (h / 2)


def normalize_drawio_edge(row: dict[str, Any], element_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    source_id = row.get("source_element_id")
    target_id = row.get("target_element_id")
    source_bbox = element_by_id.get(str(source_id), {}).get("bbox", {"x": 0.0, "y": 0.0, "w": 0.0, "h": 0.0})
    target_bbox = element_by_id.get(str(target_id), {}).get("bbox", {"x": 0.0, "y": 0.0, "w": 0.0, "h": 0.0})
    points = [anchor_point(source_bbox, row.get("source_anchor"))]
    for waypoint in row.get("waypoints", []):
        points.append((float(waypoint.get("x", 0.0)), float(waypoint.get("y", 0.0))))
    points.append(anchor_point(target_bbox, row.get("target_anchor")))
    return {
        "id": row.get("cell_id"),
        "source": source_id,
        "target": target_id,
        "points": points,
        "semantic": row.get("label") or "",
    }


def identifier_for_element(element: dict[str, Any]) -> str:
    return str(element.get("id") or element.get("cell_id") or "unknown")


def is_grouping_element(element: dict[str, Any]) -> bool:
    role = str(element.get("role") or "")
    if role == "grouping":
        return True
    if role == "special-connector":
        return False
    resolution = element.get("resolution")
    if not isinstance(resolution, dict):
        return False
    icon_title = str(resolution.get("icon_title") or "")
    category = str(element.get("category") or resolution.get("category") or "")
    if category == "Physical":
        return True
    return "Grouping -" in icon_title or icon_title.startswith("Physical - Grouping -")


def is_service_icon(element: dict[str, Any]) -> bool:
    if not element.get("visible", True) or element.get("qa_ignore"):
        return False
    if element.get("kind") != "library":
        return False
    resolution = element.get("resolution")
    if not isinstance(resolution, dict):
        return False
    resolution_type = str(resolution.get("resolution") or "")
    if resolution_type not in {"direct", "alias", "closest"}:
        return False
    if is_grouping_element(element):
        return False
    bbox = element.get("bbox") or {}
    return float(bbox.get("w", 0.0)) * float(bbox.get("h", 0.0)) >= 500.0


def is_text_like(element: dict[str, Any]) -> bool:
    element_id = identifier_for_element(element)
    if element.get("kind") == "text":
        return True
    return element_id.endswith("__external_label")


def segment_intersects_bbox(
    start: tuple[float, float],
    end: tuple[float, float],
    bbox: dict[str, float],
    padding: float,
) -> bool:
    min_x = bbox["x"] - padding
    max_x = bbox["x"] + bbox["w"] + padding
    min_y = bbox["y"] - padding
    max_y = bbox["y"] + bbox["h"] + padding
    if math.isclose(start[1], end[1]):
        y = start[1]
        segment_start = min(start[0], end[0])
        segment_end = max(start[0], end[0])
        return min_y <= y <= max_y and max(segment_start, min_x) <= min(segment_end, max_x)
    if math.isclose(start[0], end[0]):
        x = start[0]
        segment_start = min(start[1], end[1])
        segment_end = max(start[1], end[1])
        return min_x <= x <= max_x and max(segment_start, min_y) <= min(segment_end, max_y)
    return False


def edge_segments(points: list[tuple[float, float]]) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    return list(zip(points, points[1:]))


def audit_preview(
    preview_path: Path,
    report_path: Path,
    spec_path: Path | None,
    page_name: str | None,
    page_width: float,
    page_height: float,
) -> dict[str, Any]:
    page_label, elements, edges = normalize_report_page(report_path, page_name)
    logical_width, logical_height = load_spec_page_dimensions(spec_path, page_label, page_width, page_height)
    image = SimplePNG.load(preview_path)
    scale_x = image.width / logical_width
    scale_y = image.height / logical_height

    page_stats = image.sample_page()
    page_foreground_ratio = max(page_stats["foreground_ratio"], page_stats["dark_ratio"] * 0.8)

    service_icons = [element for element in elements if is_service_icon(element)]
    text_like_elements = [element for element in elements if is_text_like(element)]

    issues: list[dict[str, Any]] = []
    icon_metrics: list[dict[str, Any]] = []

    for element in service_icons:
        bbox = element["bbox"]
        stats = image.sample_bbox(bbox, scale_x, scale_y)
        visibility_ratio = max(stats["foreground_ratio"], stats["dark_ratio"], stats["colorful_ratio"])
        metric = {
            "element_id": identifier_for_element(element),
            "icon_title": element.get("resolution", {}).get("icon_title"),
            "foreground_ratio": visibility_ratio,
            "dominant_color": stats["dominant_color"],
        }
        icon_metrics.append(metric)

        if visibility_ratio < ICON_FOREGROUND_THRESHOLD:
            issues.append(
                {
                    "severity": "error",
                    "type": "icon-visibility-low",
                    "element_id": identifier_for_element(element),
                    "message": (
                        f"{identifier_for_element(element)} looks visually blank or clipped in the preview "
                        f"(foreground ratio {visibility_ratio:.3f})."
                    ),
                }
            )
        elif visibility_ratio < ICON_VISIBILITY_WARNING_THRESHOLD:
            issues.append(
                {
                    "severity": "warning",
                    "type": "icon-visibility-weak",
                    "element_id": identifier_for_element(element),
                    "message": (
                        f"{identifier_for_element(element)} is only weakly visible in the preview "
                        f"(foreground ratio {visibility_ratio:.3f})."
                    ),
                }
            )

    for element in text_like_elements:
        bbox = element.get("bbox") or {}
        element_id = identifier_for_element(element)
        for edge in edges:
            points = edge.get("points") or []
            if len(points) < 2:
                continue
            for start, end in edge_segments(points):
                if segment_intersects_bbox(start, end, bbox, TEXT_EDGE_PADDING):
                    issues.append(
                        {
                            "severity": "error",
                            "type": "label-on-connector",
                            "element_id": element_id,
                            "edge_id": edge.get("id"),
                            "message": f"{element_id} sits on top of connector {edge.get('id')}.",
                        }
                    )
                    break
            else:
                continue
            break

    external_label_count = sum(1 for element in text_like_elements if identifier_for_element(element).endswith("__external_label"))
    median_icon_visibility = median([metric["foreground_ratio"] for metric in icon_metrics])
    if service_icons and external_label_count > len(service_icons) * TEXT_CARD_RATIO_THRESHOLD and median_icon_visibility < 0.03:
        issues.append(
            {
                "severity": "warning",
                "type": "text-card-dominance",
                "message": (
                    "The preview is dominated by detached labels relative to visible service icons. "
                    "Consider restoring stronger icon emphasis or reducing external labels."
                ),
            }
        )

    if page_foreground_ratio < PAGE_FOREGROUND_WARNING_THRESHOLD:
        issues.append(
            {
                "severity": "warning",
                "type": "sparse-preview",
                "message": (
                    f"The preview reads as visually sparse (page foreground ratio {page_foreground_ratio:.3f}). "
                    "Consider tightening the layout or increasing meaningful foreground content."
                ),
            }
        )

    return {
        "page": page_label,
        "preview": str(preview_path),
        "report": str(report_path),
        "image_size": {"width": image.width, "height": image.height},
        "logical_page_size": {"width": logical_width, "height": logical_height},
        "metrics": {
            "page_foreground_ratio": page_foreground_ratio,
            "service_icon_count": len(service_icons),
            "text_like_count": len(text_like_elements),
            "external_label_count": external_label_count,
            "median_icon_visibility": median_icon_visibility,
            "icon_metrics": icon_metrics,
        },
        "issue_count": len(issues),
        "issues": issues,
    }


def median(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", type=Path, required=True, help="Preview PNG to audit.")
    parser.add_argument("--report", type=Path, required=True, help="Renderer report JSON.")
    parser.add_argument("--spec", type=Path, help="Renderable spec JSON, used to discover logical page size.")
    parser.add_argument("--page-name", help="Optional page name when the report contains multiple pages.")
    parser.add_argument("--page-width", type=float, default=1600.0, help="Fallback logical page width.")
    parser.add_argument("--page-height", type=float, default=900.0, help="Fallback logical page height.")
    parser.add_argument("--output", type=Path, help="Optional audit JSON path.")
    parser.add_argument("--fail-on-issues", action="store_true", help="Exit non-zero if any issues are found.")
    args = parser.parse_args()

    audit = audit_preview(
        preview_path=args.preview.resolve(),
        report_path=args.report.resolve(),
        spec_path=args.spec.resolve() if args.spec else None,
        page_name=args.page_name,
        page_width=args.page_width,
        page_height=args.page_height,
    )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(audit, indent=2) + "\n")

    print(json.dumps(audit, indent=2))
    if args.fail_on_issues and audit["issue_count"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

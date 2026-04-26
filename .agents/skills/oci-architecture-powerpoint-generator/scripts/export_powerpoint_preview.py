#!/usr/bin/env python3
"""Export a PowerPoint deck to a preview image using PowerPoint and Quick Look."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

POWERPOINT_TIMEOUT_SECONDS = 12


def run(
    command: list[str],
    *,
    check: bool = True,
    timeout: int | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=check,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def export_pdf_via_powerpoint(input_path: Path, pdf_out: Path) -> tuple[bool, str]:
    script_lines = [
        'tell application "Microsoft PowerPoint"',
        "activate",
        f'set sourceFile to POSIX file "{input_path}"',
        "open sourceFile",
        "delay 1",
        f'save active presentation in POSIX file "{pdf_out}" as save as PDF',
        "close active presentation saving no",
        "end tell",
    ]
    command = ["osascript"]
    for line in script_lines:
        command.extend(["-e", line])

    try:
        result = run(command, check=False, timeout=POWERPOINT_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        return (
            False,
            f"PowerPoint automation timed out after {POWERPOINT_TIMEOUT_SECONDS} seconds.",
        )
    if result.returncode != 0:
        details = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part)
        return False, details or "PowerPoint automation failed without an error message."
    return pdf_out.exists(), result.stdout.strip()


def render_quicklook_preview(source_path: Path, *, image_out: Path, size: int) -> Path:
    result = run(
        ["qlmanage", "-t", "-s", str(size), "-o", str(source_path.parent), str(source_path)],
        check=False,
    )
    if result.returncode != 0:
        details = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part)
        raise SystemExit(details or f"Quick Look failed to render {source_path}.")

    generated_png = source_path.parent / f"{source_path.name}.png"
    if not generated_png.exists():
        raise SystemExit(f"Quick Look did not produce the expected thumbnail: {generated_png}")

    image_out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(generated_png, image_out)
    return generated_png


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Input .pptx path")
    parser.add_argument("--pdf-out", type=Path, help="Intermediate PDF path")
    parser.add_argument("--image-out", type=Path, help="Final preview image path")
    parser.add_argument("--size", type=int, default=2400, help="Quick Look preview size")
    args = parser.parse_args()

    input_path = args.input.resolve()
    pdf_out = (args.pdf_out or Path("/tmp") / f"{input_path.stem}.pdf").resolve()
    image_out = (args.image_out or Path("/tmp") / f"{input_path.stem}.png").resolve()

    backend = "quicklook-pptx"
    warning = ""
    exported_pdf, details = export_pdf_via_powerpoint(input_path, pdf_out)
    preview_source = input_path
    if exported_pdf:
        backend = "powerpoint-pdf"
        preview_source = pdf_out
    else:
        warning = details

    render_quicklook_preview(preview_source, image_out=image_out, size=args.size)

    print(f"PDF: {pdf_out}")
    print(f"Preview: {image_out}")
    print(f"Backend: {backend}")
    if warning:
        print(f"Warning: {warning}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate the GTK and Rofi palettes from tokens.json."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOKENS = ROOT / "tokens.json"
CSS_OUT = ROOT / "palette.css"
RASI_OUT = ROOT / "palette.rasi"


def main() -> None:
    data = json.loads(TOKENS.read_text(encoding="utf-8"))
    colors = data["colors"]
    metrics = data["rofi_metrics"]

    css_lines = [
        "/* Generated from tokens.json. Do not edit by hand. */",
        "",
    ]
    for name, value in colors.items():
        css_lines.append(f"@define-color lg_{name} {value};")
    CSS_OUT.write_text("\n".join(css_lines) + "\n", encoding="utf-8")

    rasi_lines = [
        "/* Generated from tokens.json. Do not edit by hand. */",
        "* {",
    ]
    for name, value in colors.items():
        rasi_lines.append(f"    lg-{name.replace('_', '-')}: {value};")
    rasi_lines.append("")
    for name, value in metrics.items():
        rasi_lines.append(f"    lg-{name.replace('_', '-')}: {value};")
    rasi_lines.append("}")
    RASI_OUT.write_text("\n".join(rasi_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

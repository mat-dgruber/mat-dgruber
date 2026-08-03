import json
import os
import sys
from datetime import datetime

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
MONTH_NAMES_PT = [
    "Jan",
    "Fev",
    "Mar",
    "Abr",
    "Mai",
    "Jun",
    "Jul",
    "Ago",
    "Set",
    "Out",
    "Nov",
    "Dez",
]


def render_heatmap_svg(
    json_path: str = "data/contributions.json",
    output_svg: str = "contrib-heatmap.svg",
) -> str:
    """Renders a GitHub contribution heatmap SVG with terminal styling and diagonal reveal animation."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_contributions = data.get("total_contributions", 0)
    raw_days = data.get("days", [])

    # Sort days chronologically
    sorted_days = sorted(raw_days, key=lambda d: d["date"])

    width = 860
    height = 180

    # Layout dimensions
    box_size = 10
    gap = 4
    step = box_size + gap  # 14px

    x_start = 54
    y_start = 70

    if sorted_days:
        first_dt = datetime.strptime(sorted_days[0]["date"], "%Y-%m-%d")
    else:
        first_dt = datetime.now()

    # Calculate max diagonal for animation delays
    max_diag = 0
    day_elements = []
    month_labels = []
    last_month = None

    for day_info in sorted_days:
        dt = datetime.strptime(day_info["date"], "%Y-%m-%d")
        days_from_start = (dt - first_dt).days
        if days_from_start < 0:
            continue

        col = days_from_start // 7
        row = (dt.weekday() + 1) % 7  # 0 = Sunday, 1 = Monday, ..., 6 = Saturday

        x = x_start + col * step
        y = y_start + row * step

        diag = col + row
        if diag > max_diag:
            max_diag = diag

        level = day_info.get("level", 0)
        if level < 0:
            level = 0
        elif level >= len(PALETTE):
            level = len(PALETTE) - 1

        color = PALETTE[level]
        count = day_info.get("count", 0)
        date_str = day_info.get("date", "")

        # Check for month label placement at start of month (row == 0 or first occurrence)
        if dt.month != last_month:
            last_month = dt.month
            month_name = MONTH_NAMES_PT[dt.month - 1]
            month_labels.append((x, month_name))

        tooltip = f"{date_str}: {count} contribuições"
        rect_html = (
            f'      <rect class="day-box d-{diag}" x="{x}" y="{y}" '
            f'width="{box_size}" height="{box_size}" rx="2" fill="{color}">\n'
            f"        <title>{tooltip}</title>\n"
            f"      </rect>"
        )
        day_elements.append(rect_html)

    # Build SVG content
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        "  <style>",
        "    @keyframes boxFade {",
        "      from { opacity: 0; transform: scale(0.3); }",
        "      to { opacity: 1; transform: scale(1); }",
        "    }",
        "    .bg { fill: #0d1117; rx: 8px; }",
        "    .border { fill: none; stroke: #30363d; stroke-width: 1px; rx: 8px; }",
        "    .header { fill: #161b22; }",
        '    .header-title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; font-size: 12px; font-weight: 600; fill: #8b949e; text-anchor: middle; }',
        '    .stat-text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; font-size: 12px; font-weight: 600; fill: #c9d1d9; }',
        '    .label-text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; font-size: 9px; fill: #8b949e; }',
        '    .legend-text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; font-size: 10px; fill: #8b949e; }',
        "    .day-box { opacity: 0; animation: boxFade 0.3s ease-out forwards; transform-box: fill-box; transform-origin: center; }",
    ]

    for d in range(max_diag + 1):
        delay = round(d * 0.012, 3)
        svg_parts.append(f"    .d-{d} {{ animation-delay: {delay}s; }}")

    svg_parts.extend(
        [
            "  </style>",
            "  <!-- Background -->",
            f'  <rect width="{width}" height="{height}" class="bg" />',
            "  <!-- Header Bar -->",
            f'  <path d="M 0 8 A 8 8 0 0 1 8 0 L {width - 8} 0 A 8 8 0 0 1 {width} 8 L {width} 32 L 0 32 Z" class="header" />',
            "  <!-- Header Window Dots -->",
            '  <circle cx="20" cy="16" r="6" fill="#ff5f56" />',
            '  <circle cx="38" cy="16" r="6" fill="#ffbd2e" />',
            '  <circle cx="56" cy="16" r="6" fill="#27c93f" />',
            "  <!-- Header Title -->",
            f'  <text x="{width // 2}" y="20" class="header-title">matheus@github ~ ./contributions.sh --year 2025-2026</text>',
            "  <!-- Stat Text -->",
            f'  <text x="24" y="48" class="stat-text">{total_contributions:,} contribuições no último ano</text>',
            "  <!-- Legend -->",
            '  <g transform="translate(680, 38)">',
            '    <text x="0" y="9" class="legend-text">Menos</text>',
        ]
    )

    # Legend color squares
    lx = 42
    for color in PALETTE:
        svg_parts.append(
            f'    <rect x="{lx}" y="0" width="{box_size}" height="{box_size}" rx="2" fill="{color}" />'
        )
        lx += box_size + 3

    svg_parts.append(f'    <text x="{lx + 4}" y="9" class="legend-text">Mais</text>')
    svg_parts.append("  </g>")

    # Day labels (Seg, Qua, Sex)
    svg_parts.extend(
        [
            "  <!-- Day Labels -->",
            '  <text x="44" y="92" class="label-text" text-anchor="end">Seg</text>',
            '  <text x="44" y="120" class="label-text" text-anchor="end">Qua</text>',
            '  <text x="44" y="148" class="label-text" text-anchor="end">Sex</text>',
        ]
    )

    # Month Labels
    svg_parts.append("  <!-- Month Labels -->")
    prev_x = -100
    for m_x, m_name in month_labels:
        # Avoid overlapping month labels
        if m_x - prev_x >= 28:
            svg_parts.append(
                f'  <text x="{m_x}" y="63" class="label-text">{m_name}</text>'
            )
            prev_x = m_x

    # Heatmap Boxes
    svg_parts.append("  <!-- Heatmap Boxes -->")
    svg_parts.extend(day_elements)

    # Outer border
    svg_parts.extend(
        [
            f'  <rect width="{width - 1}" height="{height - 1}" x="0.5" y="0.5" class="border" />',
            "</svg>",
        ]
    )

    output_content = "\n".join(svg_parts)

    out_dir = os.path.dirname(output_svg)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(output_svg, "w", encoding="utf-8") as f:
        f.write(output_content)

    return output_svg


if __name__ == "__main__":
    json_path = sys.argv[1] if len(sys.argv) > 1 else "data/contributions.json"
    output_svg = sys.argv[2] if len(sys.argv) > 2 else "contrib-heatmap.svg"
    render_heatmap_svg(json_path, output_svg)
    print(f"Generated heatmap SVG at {output_svg}")

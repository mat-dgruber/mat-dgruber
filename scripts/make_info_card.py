import html
import os
import sys


def generate_info_card_svg(output_path: str = "info-card.svg") -> str:
    """Generates a neofetch-style terminal info card SVG with animations."""
    width = 490
    height = 320

    top_fields = [
        ("User", "Matheus Diniz (@mat-dgruber)"),
        ("Role", "Engenheiro de Software Pleno"),
        ("Company", "Casa Publicadora Brasileira (CPB)"),
        ("Location", "Tatuí, SP - Brasil 🇧🇷"),
    ]

    bottom_fields = [
        ("Core Stack", "Go | TypeScript | Python | SQL"),
        ("AI & Agentes", "OpenClaude | Tool Calling | MCP"),
        ("Compiladores", "Harpia (Linguagem Reativa em Go)"),
        ("Formação", "ADS + Pós em IA Aplicada"),
    ]

    quote = '"Elegância é quando não há mais nada a retirar."'

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        '  <style>',
        '    @keyframes fadeIn {',
        '      from { opacity: 0; transform: translateY(3px); }',
        '      to { opacity: 1; transform: translateY(0); }',
        '    }',
        '    .bg { fill: #0d1117; rx: 8px; }',
        '    .border { fill: none; stroke: #30363d; stroke-width: 1px; rx: 8px; }',
        '    .header { fill: #161b22; }',
        '    .title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; font-size: 12px; font-weight: 600; fill: #8b949e; text-anchor: middle; }',
        '    .key { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; font-size: 12px; font-weight: 600; fill: #58a6ff; }',
        '    .val { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace, "Apple Color Emoji", "Segoe UI Emoji"; font-size: 12px; fill: #c9d1d9; }',
        '    .quote-text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; font-size: 11px; font-style: italic; fill: #8b949e; text-anchor: middle; }',
    ]

    svg_parts.extend([
        '  </style>',
        '  <!-- Background -->',
        f'  <rect width="{width}" height="{height}" class="bg" />',
        '  <!-- Header Bar -->',
        '  <path d="M 0 8 A 8 8 0 0 1 8 0 L 482 0 A 8 8 0 0 1 490 8 L 490 32 L 0 32 Z" class="header" />',
        '  <!-- Header Window Dots -->',
        '  <circle cx="20" cy="16" r="6" fill="#ff5f56" />',
        '  <circle cx="38" cy="16" r="6" fill="#ffbd2e" />',
        '  <circle cx="56" cy="16" r="6" fill="#27c93f" />',
        '  <!-- Header Title -->',
        '  <text x="245" y="20" class="title">matheus@cpb ~ neofetch</text>',
        '  <!-- Content Container -->',
        '  <g transform="translate(24, 0)">',
    ])

    current_y = 58

    for k, v in top_fields:
        esc_k = html.escape(k)
        esc_v = html.escape(v)
        svg_parts.append(f'    <g transform="translate(0, {current_y})">')
        svg_parts.append(f'      <text x="0" y="0" class="key">{esc_k}:</text>')
        svg_parts.append(f'      <text x="120" y="0" class="val">{esc_v}</text>')
        svg_parts.append('    </g>')
        current_y += 22

    # Separator Line
    line_y = current_y - 8
    svg_parts.append(f'    <line x1="0" y1="{line_y}" x2="442" y2="{line_y}" stroke="#30363d" stroke-width="1" />')
    current_y += 14

    for k, v in bottom_fields:
        esc_k = html.escape(k)
        esc_v = html.escape(v)
        svg_parts.append(f'    <g transform="translate(0, {current_y})">')
        svg_parts.append(f'      <text x="0" y="0" class="key">{esc_k}:</text>')
        svg_parts.append(f'      <text x="120" y="0" class="val">{esc_v}</text>')
        svg_parts.append('    </g>')
        current_y += 22

    # Quote
    esc_quote = html.escape(quote)
    quote_y = current_y + 16
    svg_parts.append(f'    <g transform="translate(221, {quote_y})">')
    svg_parts.append(f'      <text x="0" y="0" class="quote-text">{esc_quote}</text>')
    svg_parts.append('    </g>')

    svg_parts.extend([
        '  </g>',
        f'  <rect width="{width - 1}" height="{height - 1}" x="0.5" y="0.5" class="border" />',
        '</svg>',
    ])

    content = "\n".join(svg_parts)

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return output_path


if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "info-card.svg"
    generate_info_card_svg(out_file)
    print(f"Generated info card SVG at {out_file}")

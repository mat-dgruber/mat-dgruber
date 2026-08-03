import html
import os
import sys
import cv2

RAMP = " .`:-=+*cs#%@"


def image_to_ascii_lines(image_path: str, width: int = 95) -> list[str]:
    """Converts image to grayscale ASCII string lines, adjusting aspect ratio (~0.52 factor)."""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")

    orig_height, orig_width = img.shape[:2]
    aspect_ratio = orig_height / orig_width
    height = int(width * aspect_ratio * 0.52)
    resized = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)

    lines = []
    ramp_len = len(RAMP) - 1
    for row in resized:
        line_chars = []
        for pixel in row:
            # Map pixel intensity: 255 (white bg) -> 0 (' '), 0 (dark feature) -> ramp_len ('@')
            pixel_val = float(pixel)
            idx = int((255.0 - pixel_val) * ramp_len / 255.0)
            line_chars.append(RAMP[idx])
        lines.append("".join(line_chars))

    return lines


def generate_ascii_svg(lines: list[str], output_path: str, svg_width: int = 370) -> str:
    """Generates an SVG string representing the terminal profile with SMIL typing animation."""
    if not lines:
        raise ValueError("ASCII lines list cannot be empty")

    cols = len(lines[0])
    rows = len(lines)

    # Character and line layout calculations
    padding_x = 10
    padding_y = 10
    usable_width = svg_width - (padding_x * 2)
    char_width = usable_width / cols if cols > 0 else 3.6
    font_size = char_width * 1.6
    line_height = font_size * 1.15

    svg_height = int(rows * line_height + (padding_y * 2))

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">',
        '  <style>',
        f'    .ascii-text {{ font-family: "Courier New", Courier, monospace; font-size: {font_size:.2f}px; fill: #38bdf8; white-space: pre; }}',
        '    .bg { fill: #0d1117; rx: 8px; }',
        '  </style>',
        '  <rect width="100%" height="100%" class="bg" />',
        f'  <g transform="translate({padding_x}, {padding_y})">'
    ]

    row_duration = 0.04
    for i, line in enumerate(lines):
        escaped_line = html.escape(line)
        y = (i + 1) * line_height
        delay = i * row_duration

        clip_id = f"clip-{i}"
        target_width = cols * char_width

        svg_parts.append(f'    <clipPath id="{clip_id}">')
        svg_parts.append(f'      <rect x="0" y="{y - line_height:.2f}" width="0" height="{line_height:.2f}">')
        svg_parts.append(f'        <animate attributeName="width" from="0" to="{target_width:.2f}" begin="{delay:.2f}s" dur="0.15s" fill="freeze" />')
        svg_parts.append('      </rect>')
        svg_parts.append('    </clipPath>')
        svg_parts.append(f'    <text x="0" y="{y:.2f}" class="ascii-text" clip-path="url(#{clip_id})">{escaped_line}</text>')

    svg_parts.append('  </g>')
    svg_parts.append('</svg>')

    content = "\n".join(svg_parts)
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return output_path


if __name__ == "__main__":
    input_image = sys.argv[1] if len(sys.argv) > 1 else "data/source-prepped.png"
    output_svg = sys.argv[2] if len(sys.argv) > 2 else "matheus-ascii.svg"

    ascii_lines = image_to_ascii_lines(input_image, width=95)
    generate_ascii_svg(ascii_lines, output_svg, svg_width=370)
    print(f"Generated ASCII SVG at {output_svg}")

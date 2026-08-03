# Animated Terminal Profile Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an animated terminal-styled GitHub Profile README featuring a typing monochrome ASCII portrait, a neofetch info card, a live contribution heatmap SVG, and an automated daily GitHub Actions cron workflow.

**Architecture:** A Python toolchain converts `assets/IMG_2250.jpg` into `matheus-ascii.svg` (SMIL animation) and generates `info-card.svg`. A separate scraper fetches public GitHub contribution data without tokens to generate `contrib-heatmap.svg`. `README.md` layouts all three SVGs in a terminal-style table structure, and GitHub Actions refreshes the heatmap daily.

**Tech Stack:** Python 3.11+, OpenCV, rembg, Pillow, NumPy, BeautifulSoup4, Requests, GitHub Actions, SVG/SMIL, Markdown.

## Global Constraints
- Monochrome ASCII palette: ` .`:-=+*cs#%@`
- Card width: 490px; ASCII portrait width: 370px; Heatmap width: 860px.
- No third-party stats services, no GitHub Personal Access Token required.
- Pure SVG + CSS/SMIL animations (compatible with GitHub Sanitizer).

---

### Task 1: Project Setup & Requirements

**Files:**
- Create: `scripts/requirements.txt`
- Create: `scripts/test_setup.py`

**Interfaces:**
- Consumes: System Python environment
- Produces: Installed dependencies (`requests`, `beautifulsoup4`, `pillow`, `numpy`, `opencv-python`, `rembg`)

- [ ] **Step 1: Create `scripts/requirements.txt`**

```text
requests==2.32.3
beautifulsoup4==4.12.3
pillow
numpy
opencv-python
rembg
```

- [ ] **Step 2: Create `scripts/test_setup.py`**

```python
import requests
import bs4
import PIL
import numpy
import cv2
import rembg

print("All dependencies imported successfully.")
```

- [ ] **Step 3: Run dependency test**

Run: `python3 scripts/test_setup.py`
Expected: `All dependencies imported successfully.`

- [ ] **Step 4: Commit**

```bash
git add scripts/requirements.txt scripts/test_setup.py
git commit -m "chore: setup dependencies for terminal profile art toolchain"
```

---

### Task 2: Photo Prep Script

**Files:**
- Create: `scripts/prep_photo.py`
- Test: `scripts/test_prep_photo.py`
- Input: `assets/IMG_2250.jpg`
- Produces: `data/source-prepped.png`

**Interfaces:**
- Consumes: `assets/IMG_2250.jpg`
- Produces: Grayscale prepped image at `data/source-prepped.png`

- [ ] **Step 1: Write `scripts/prep_photo.py`**

```python
import os
import sys
import cv2
import numpy as np
from PIL import Image
from rembg import remove

def prep_photo(input_path: str, output_path: str) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(input_path, 'rb') as f:
        input_bytes = f.read()
    output_bytes = remove(input_bytes)
    
    nparr = np.frombuffer(output_bytes, np.uint8)
    img_rgba = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
    
    alpha = img_rgba[:, :, 3] / 255.0
    gray = cv2.cvtColor(img_rgba, cv2.COLOR_BGRA2GRAY)
    
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray_clahe = clahe.apply(gray)
    
    white_bg = np.ones_like(gray, dtype=np.uint8) * 255
    final_img = (gray_clahe * alpha + white_bg * (1.0 - alpha)).astype(np.uint8)
    
    cv2.imwrite(output_path, final_img)
    return output_path

if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else "assets/IMG_2250.jpg"
    out = "data/source-prepped.png"
    prep_photo(inp, out)
    print(f"Saved prepped photo to {out}")
```

- [ ] **Step 2: Create unit test `scripts/test_prep_photo.py`**

```python
import os
import cv2
from prep_photo import prep_photo

def test_prep_photo_creates_image():
    out = "data/test-prepped.png"
    res = prep_photo("assets/IMG_2250.jpg", out)
    assert os.path.exists(res)
    img = cv2.imread(res)
    assert img is not None
    assert img.shape[0] > 0 and img.shape[1] > 0
    if os.path.exists(out):
        os.remove(out)

if __name__ == "__main__":
    test_prep_photo_creates_image()
    print("test_prep_photo passed.")
```

- [ ] **Step 3: Run test**

Run: `python3 scripts/test_prep_photo.py`
Expected: `test_prep_photo passed.`

- [ ] **Step 4: Run script on assets/IMG_2250.jpg**

Run: `python3 scripts/prep_photo.py assets/IMG_2250.jpg`
Expected: `Saved prepped photo to data/source-prepped.png`

- [ ] **Step 5: Commit**

```bash
git add scripts/prep_photo.py scripts/test_prep_photo.py data/source-prepped.png
git commit -m "feat: add photo preparation script with CLAHE and rembg background removal"
```

---

### Task 3: Animated Monochrome ASCII SVG Generator

**Files:**
- Create: `scripts/make_ascii_svg.py`
- Test: `scripts/test_make_ascii_svg.py`
- Consumes: `data/source-prepped.png`
- Produces: `matheus-ascii.svg`

**Interfaces:**
- Consumes: `data/source-prepped.png`
- Produces: `matheus-ascii.svg` (width 370px, typing SMIL animation)

- [ ] **Step 1: Write `scripts/make_ascii_svg.py`**

```python
import os
import sys
import cv2
import html

RAMP = " .`:-=+*cs#%@"  # Bright (sparse) -> Dark (dense)

def image_to_ascii_lines(image_path: str, width: int = 100) -> list[str]:
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")
    
    aspect_ratio = img.shape[0] / img.shape[1]
    height = int(width * aspect_ratio * 0.52)
    resized = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)
    
    lines = []
    for row in resized:
        line_chars = []
        for pixel in row:
            idx = int((pixel / 255.0) * (len(RAMP) - 1))
            char = RAMP[idx]
            line_chars.append(char)
        lines.append("".join(line_chars))
    return lines

def generate_ascii_svg(lines: list[str], output_path: str, svg_width: int = 370) -> str:
    char_width = 3.6
    line_height = 7.0
    cols = len(lines[0])
    rows = len(lines)
    
    svg_height = int(rows * line_height + 20)
    
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">',
        '  <style>',
        '    .ascii-text { font-family: "Courier New", Courier, monospace; font-size: 6px; fill: #38bdf8; white-space: pre; }',
        '    .bg { fill: #0d1117; rx: 8px; }',
        '  </style>',
        f'  <rect width="100%" height="100%" class="bg" />',
        f'  <g transform="translate(10, 10)">'
    ]
    
    total_rows = len(lines)
    row_duration = 0.05
    
    for i, line in enumerate(lines):
        escaped_line = html.escape(line)
        y = (i + 1) * line_height
        delay = i * row_duration
        
        clip_id = f"clip-{i}"
        svg_parts.append(f'    <clipPath id="{clip_id}">')
        svg_parts.append(f'      <rect x="0" y="{y - line_height}" width="0" height="{line_height}">')
        svg_parts.append(f'        <animate attributeName="width" from="0" to="{cols * char_width}" begin="{delay:.2f}s" dur="0.2s" fill="freeze" />')
        svg_parts.append(f'      </rect>')
        svg_parts.append(f'    </clipPath>')
        svg_parts.append(f'    <text x="0" y="{y}" class="ascii-text" clip-path="url(#{clip_id})">{escaped_line}</text>')
        
    svg_parts.append('  </g>')
    svg_parts.append('</svg>')
    
    content = "\n".join(svg_parts)
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    return output_path

if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else "data/source-prepped.png"
    out = "matheus-ascii.svg"
    lines = image_to_ascii_lines(inp, width=95)
    generate_ascii_svg(lines, out, svg_width=370)
    print(f"Generated ASCII SVG at {out}")
```

- [ ] **Step 2: Write test `scripts/test_make_ascii_svg.py`**

```python
import os
from make_ascii_svg import image_to_ascii_lines, generate_ascii_svg

def test_ascii_svg_generation():
    lines = image_to_ascii_lines("data/source-prepped.png", width=50)
    assert len(lines) > 0
    out_svg = "matheus-ascii.svg"
    generate_ascii_svg(lines, out_svg, svg_width=370)
    assert os.path.exists(out_svg)
    with open(out_svg, "r") as f:
        content = f.read()
    assert "<svg" in content
    assert "clip-path=" in content
    assert "animate" in content

if __name__ == "__main__":
    test_ascii_svg_generation()
    print("test_ascii_svg_generation passed.")
```

- [ ] **Step 3: Run test**

Run: `python3 scripts/test_make_ascii_svg.py`
Expected: `test_ascii_svg_generation passed.`

- [ ] **Step 4: Generate `matheus-ascii.svg`**

Run: `python3 scripts/make_ascii_svg.py data/source-prepped.png`
Expected: `Generated ASCII SVG at matheus-ascii.svg`

- [ ] **Step 5: Commit**

```bash
git add scripts/make_ascii_svg.py scripts/test_make_ascii_svg.py matheus-ascii.svg
git commit -m "feat: add ASCII SVG generator with row-by-row SMIL typing animation"
```

---

### Task 4: Neofetch Info Card Generator

**Files:**
- Create: `scripts/make_info_card.py`
- Test: `scripts/test_make_info_card.py`
- Produces: `info-card.svg`

**Interfaces:**
- Produces: `info-card.svg` (490px width, terminal style)

- [ ] **Step 1: Write `scripts/make_info_card.py`**

```python
import os

def generate_info_card_svg(output_path: str = "info-card.svg") -> str:
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 490 320" width="490" height="320">
  <style>
    .bg { fill: #0d1117; stroke: #30363d; stroke-width: 1px; rx: 8px; }
    .header { fill: #161b22; rx: 8px; }
    .title { font-family: 'Fira Code', Monaco, Consolas, monospace; font-size: 13px; font-weight: bold; fill: #c9d1d9; }
    .dot-red { fill: #ff5f56; }
    .dot-yellow { fill: #ffbd2e; }
    .dot-green { fill: #27c93f; }
    .label { font-family: 'Fira Code', Monaco, Consolas, monospace; font-size: 12px; font-weight: bold; fill: #38bdf8; }
    .value { font-family: 'Fira Code', Monaco, Consolas, monospace; font-size: 12px; fill: #e6edf3; }
    .subtext { font-family: 'Fira Code', Monaco, Consolas, monospace; font-size: 11px; fill: #8b949e; }
    .row { opacity: 0; animation: fadeIn 0.5s ease-forwards; animation-fill-mode: forwards; }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(4px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>

  <rect width="490" height="320" class="bg" />
  
  <!-- Title bar -->
  <path d="M 0 8 Q 0 0 8 0 L 482 0 Q 490 0 490 8 L 490 32 L 0 32 Z" class="header" />
  <circle cx="16" cy="16" r="5" class="dot-red" />
  <circle cx="32" cy="16" r="5" class="dot-yellow" />
  <circle cx="48" cy="16" r="5" class="dot-green" />
  <text x="70" y="20" class="title">matheus@cpb ~ neofetch</text>

  <!-- Content Rows -->
  <g transform="translate(20, 60)">
    <!-- Row 1 -->
    <g class="row" style="animation-delay: 0.1s;">
      <text x="0" y="0" class="label">User:</text>
      <text x="90" y="0" class="value">Matheus Diniz (@mat-dgruber)</text>
    </g>

    <!-- Row 2 -->
    <g class="row" style="animation-delay: 0.2s;">
      <text x="0" y="25" class="label">Role:</text>
      <text x="90" y="25" class="value">Engenheiro de Software Pleno</text>
    </g>

    <!-- Row 3 -->
    <g class="row" style="animation-delay: 0.3s;">
      <text x="0" y="50" class="label">Company:</text>
      <text x="90" y="50" class="value">Casa Publicadora Brasileira (CPB)</text>
    </g>

    <!-- Row 4 -->
    <g class="row" style="animation-delay: 0.4s;">
      <text x="0" y="75" class="label">Location:</text>
      <text x="90" y="75" class="value">Tatuí, SP - Brasil 🇧🇷</text>
    </g>

    <!-- Separator -->
    <line x1="0" y1="95" x2="450" y2="95" stroke="#30363d" stroke-width="1" />

    <!-- Row 5 -->
    <g class="row" style="animation-delay: 0.5s;">
      <text x="0" y="120" class="label">Core Stack:</text>
      <text x="90" y="120" class="value">Go | TypeScript | Python | SQL</text>
    </g>

    <!-- Row 6 -->
    <g class="row" style="animation-delay: 0.6s;">
      <text x="0" y="145" class="label">AI &amp; Agentes:</text>
      <text x="90" y="145" class="value">OpenClaude | Tool Calling | MCP</text>
    </g>

    <!-- Row 7 -->
    <g class="row" style="animation-delay: 0.7s;">
      <text x="0" y="170" class="label">Compiladores:</text>
      <text x="90" y="170" class="value">Harpia (Linguagem Reativa em Go)</text>
    </g>

    <!-- Row 8 -->
    <g class="row" style="animation-delay: 0.8s;">
      <text x="0" y="195" class="label">Formação:</text>
      <text x="90" y="195" class="value">ADS + Pós em IA Aplicada</text>
    </g>

    <!-- Footer Quote -->
    <g class="row" style="animation-delay: 0.9s;">
      <text x="0" y="230" class="subtext">"Elegância é quando não há mais nada a retirar."</text>
    </g>
  </g>
</svg>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    return output_path

if __name__ == "__main__":
    generate_info_card_svg("info-card.svg")
    print("Generated info-card.svg")
```

- [ ] **Step 2: Create test `scripts/test_make_info_card.py`**

```python
import os
from make_info_card import generate_info_card_svg

def test_info_card_generation():
    out = "info-card.svg"
    generate_info_card_svg(out)
    assert os.path.exists(out)
    with open(out, "r") as f:
        content = f.read()
    assert "<svg" in content
    assert "matheus@cpb ~ neofetch" in content
    assert "Engenheiro de Software Pleno" in content

if __name__ == "__main__":
    test_info_card_generation()
    print("test_info_card_generation passed.")
```

- [ ] **Step 3: Run test**

Run: `python3 scripts/test_make_info_card.py`
Expected: `test_info_card_generation passed.`

- [ ] **Step 4: Generate `info-card.svg`**

Run: `python3 scripts/make_info_card.py`
Expected: `Generated info-card.svg`

- [ ] **Step 5: Commit**

```bash
git add scripts/make_info_card.py scripts/test_make_info_card.py info-card.svg
git commit -m "feat: add neofetch-style info card SVG generator"
```

---

### Task 5: Contribution Scraper

**Files:**
- Create: `scripts/fetch_contributions.py`
- Test: `scripts/test_fetch_contributions.py`
- Produces: `data/contributions.json`

**Interfaces:**
- Fetches HTML from `https://github.com/users/mat-dgruber/contributions`
- Produces: JSON data structure with daily contributions and total count at `data/contributions.json`

- [ ] **Step 1: Write `scripts/fetch_contributions.py`**

```python
import json
import os
import re
import requests
from bs4 import BeautifulSoup

def fetch_contributions(username: str = "mat-dgruber", output_json: str = "data/contributions.json") -> dict:
    url = f"https://github.com/users/{username}/contributions"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to fetch contributions: HTTP {resp.status_code}")
        
    soup = BeautifulSoup(resp.text, "html.parser")
    days_data = []
    
    td_elements = soup.find_all("td", class_=re.compile(r"ContributionCalendar-day"))
    
    for td in td_elements:
        date_str = td.get("data-date")
        level_str = td.get("data-level", "0")
        if not date_str:
            continue
        
        # Extract count from tooltip / text
        count = 0
        tooltip_id = td.get("aria-describedby")
        if tooltip_id:
            tool_el = soup.find(id=tooltip_id)
            if tool_el:
                match = re.search(r"(\d+)\s+contribution", tool_el.text)
                if match:
                    count = int(match.group(1))
                    
        days_data.append({
            "date": date_str,
            "count": count,
            "level": int(level_str)
        })

    # Total count from header
    total_count = sum(d["count"] for d in days_data)
    h2_el = soup.find("h2", class_=re.compile(r"f4"))
    if h2_el:
        match = re.search(r"([\d,]+)\s+contributions", h2_el.text)
        if match:
            total_count = int(match.group(1).replace(",", ""))

    result = {
        "username": username,
        "total_contributions": total_count,
        "days": days_data
    }
    
    os.makedirs(os.path.dirname(output_json) if os.path.dirname(output_json) else ".", exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        
    return result

if __name__ == "__main__":
    data = fetch_contributions("mat-dgruber", "data/contributions.json")
    print(f"Fetched {data['total_contributions']} contributions for {data['username']}.")
```

- [ ] **Step 2: Create unit test `scripts/test_fetch_contributions.py`**

```python
import os
from fetch_contributions import fetch_contributions

def test_fetch_contributions():
    out = "data/test-contributions.json"
    data = fetch_contributions("mat-dgruber", out)
    assert os.path.exists(out)
    assert "total_contributions" in data
    assert "days" in data
    assert len(data["days"]) > 0
    if os.path.exists(out):
        os.remove(out)

if __name__ == "__main__":
    test_fetch_contributions()
    print("test_fetch_contributions passed.")
```

- [ ] **Step 3: Run test**

Run: `python3 scripts/test_fetch_contributions.py`
Expected: `test_fetch_contributions passed.`

- [ ] **Step 4: Fetch real contribution data**

Run: `python3 scripts/fetch_contributions.py`
Expected: `Fetched X contributions for mat-dgruber.`

- [ ] **Step 5: Commit**

```bash
git add scripts/fetch_contributions.py scripts/test_fetch_contributions.py data/contributions.json
git commit -m "feat: add public contribution scraper for GitHub profile"
```

---

### Task 6: Contribution Heatmap SVG Generator

**Files:**
- Create: `scripts/render_heatmap_svg.py`
- Test: `scripts/test_render_heatmap_svg.py`
- Consumes: `data/contributions.json`
- Produces: `contrib-heatmap.svg`

**Interfaces:**
- Consumes: `data/contributions.json`
- Produces: `contrib-heatmap.svg` (860px width, animated heatmap)

- [ ] **Step 1: Write `scripts/render_heatmap_svg.py`**

```python
import json
import os

PALETTE = [
    "#161b22",  # level 0
    "#0e4429",  # level 1
    "#006d32",  # level 2
    "#26a641",  # level 3
    "#39d353",  # level 4
    "#69f0a0"   # level 5
]

def render_heatmap_svg(json_path: str = "data/contributions.json", output_svg: str = "contrib-heatmap.svg") -> str:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    days = data.get("days", [])
    total_contributions = data.get("total_contributions", 0)
    
    box_size = 10
    box_gap = 4
    start_x = 35
    start_y = 40
    
    svg_width = 860
    svg_height = 180
    
    weeks = []
    current_week = []
    
    for i, day in enumerate(days):
        current_week.append(day)
        if len(current_week) == 7 or i == len(days) - 1:
            weeks.append(current_week)
            current_week = []

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">',
        '  <style>',
        '    .bg { fill: #0d1117; stroke: #30363d; stroke-width: 1px; rx: 8px; }',
        '    .header { fill: #161b22; rx: 8px; }',
        '    .title { font-family: "Fira Code", Monaco, Consolas, monospace; font-size: 13px; font-weight: bold; fill: #c9d1d9; }',
        '    .dot-red { fill: #ff5f56; } .dot-yellow { fill: #ffbd2e; } .dot-green { fill: #27c93f; }',
        '    .text-stat { font-family: "Fira Code", Monaco, Consolas, monospace; font-size: 11px; fill: #8b949e; }',
        '    .day-box { rx: 2px; opacity: 0; animation: boxFade 0.4s ease-out forwards; }',
        '    @keyframes boxFade { from { opacity: 0; transform: scale(0.6); } to { opacity: 1; transform: scale(1); } }',
        '  </style>',
        f'  <rect width="{svg_width}" height="{svg_height}" class="bg" />',
        '  <path d="M 0 8 Q 0 0 8 0 L 852 0 Q 860 0 860 8 L 860 32 L 0 32 Z" class="header" />',
        '  <circle cx="16" cy="16" r="5" class="dot-red" />',
        '  <circle cx="32" cy="16" r="5" class="dot-yellow" />',
        '  <circle cx="48" cy="16" r="5" class="dot-green" />',
        f'  <text x="70" y="20" class="title">matheus@github ~ ./contributions.sh --year 2025-2026</text>',
        f'  <text x="640" y="20" class="text-stat">{total_contributions:,} contribuições no último ano</text>',
        '  <g transform="translate(0, 10)">'
    ]
    
    for w_idx, week in enumerate(weeks):
        for d_idx, day in enumerate(week):
            level = min(day.get("level", 0), len(PALETTE) - 1)
            color = PALETTE[level]
            x = start_x + w_idx * (box_size + box_gap)
            y = start_y + d_idx * (box_size + box_gap)
            delay = (w_idx * 0.015) + (d_idx * 0.02)
            
            svg_parts.append(
                f'    <rect x="{x}" y="{y}" width="{box_size}" height="{box_size}" fill="{color}" '
                f'class="day-box" style="animation-delay: {delay:.3f}s;"><title>{day["date"]}: {day["count"]} contribuições</title></rect>'
            )
            
    svg_parts.append('  </g>')
    svg_parts.append('</svg>')
    
    with open(output_svg, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_parts))
    return output_svg

if __name__ == "__main__":
    render_heatmap_svg("data/contributions.json", "contrib-heatmap.svg")
    print("Rendered contrib-heatmap.svg")
```

- [ ] **Step 2: Create unit test `scripts/test_render_heatmap_svg.py`**

```python
import os
from render_heatmap_svg import render_heatmap_svg

def test_render_heatmap_svg():
    out = "contrib-heatmap.svg"
    render_heatmap_svg("data/contributions.json", out)
    assert os.path.exists(out)
    with open(out, "r") as f:
        content = f.read()
    assert "<svg" in content
    assert "matheus@github ~ ./contributions.sh" in content
    assert "day-box" in content

if __name__ == "__main__":
    test_render_heatmap_svg()
    print("test_render_heatmap_svg passed.")
```

- [ ] **Step 3: Run test**

Run: `python3 scripts/test_render_heatmap_svg.py`
Expected: `test_render_heatmap_svg passed.`

- [ ] **Step 4: Render `contrib-heatmap.svg`**

Run: `python3 scripts/render_heatmap_svg.py`
Expected: `Rendered contrib-heatmap.svg`

- [ ] **Step 5: Commit**

```bash
git add scripts/render_heatmap_svg.py scripts/test_render_heatmap_svg.py contrib-heatmap.svg
git commit -m "feat: add SVG heatmap renderer with diagonal reveal animation"
```

---

### Task 7: Layout Integration in README.md

**Files:**
- Modify: `README.md`

**Interfaces:**
- Integrates `contrib-heatmap.svg`, `matheus-ascii.svg`, and `info-card.svg` in terminal layout.

- [ ] **Step 1: Edit `README.md` to insert Terminal section right after top banners**

Insert the following section below line 24 of `README.md`:

```html
<br />

<!-- Terminal Profile Section -->
<div align="center">
  <h3><code>matheus@github ~ $ ./contributions.sh</code></h3>
  <img src="./contrib-heatmap.svg" width="860" alt="Heatmap de Contribuições" />

  <br /><br />

  <h3><code>matheus@github ~ $ neofetch --user mat-dgruber</code></h3>
  <table>
    <tr>
      <td valign="top"><img src="./matheus-ascii.svg" width="370" alt="ASCII Portrait" /></td>
      <td valign="top"><img src="./info-card.svg" width="490" alt="Info Card Neofetch" /></td>
    </tr>
  </table>
</div>

<br />
```

- [ ] **Step 2: Verify `README.md` syntax and formatting**

Check that HTML tags are balanced and image paths match generated SVG names.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: integrate terminal profile SVGs into README.md"
```

---

### Task 8: GitHub Actions Workflow

**Files:**
- Create: `.github/workflows/update-profile-art.yml`

**Interfaces:**
- Runs daily on cron schedule `"17 6 * * *"` and manual `workflow_dispatch`.

- [ ] **Step 1: Write `.github/workflows/update-profile-art.yml`**

```yaml
name: Update Profile Art

on:
  schedule:
    - cron: "17 6 * * *"
  workflow_dispatch:
  push:
    branches: [main]

permissions:
  contents: write

jobs:
  heatmap:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests beautifulsoup4

      - name: Fetch contributions & render heatmap
        run: |
          python scripts/fetch_contributions.py
          python scripts/render_heatmap_svg.py

      - name: Commit updated heatmap
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "chore: refresh contribution graph [skip ci]"
          file_pattern: "data/contributions.json contrib-heatmap.svg"
```

- [ ] **Step 2: Commit workflow**

```bash
git add .github/workflows/update-profile-art.yml
git commit -m "ci: add daily GitHub Actions workflow to refresh profile contribution graph"
```

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-08-03-animated-terminal-profile.md`. Two execution options:

1. **Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration
2. **Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?

# Design Spec: Animated Terminal-Style GitHub Profile README

## Context & Purpose
Transform Matheus Diniz's (`mat-dgruber`) GitHub profile README into an animated, terminal-styled interface containing:
1. **Monochrome Animated ASCII Portrait**: Generated from `assets/IMG_2250.jpg` with smooth row-by-row typing animation.
2. **Neofetch Info Card**: Displays role (Engenheiro de Software Pleno @ CPB), location (Tatuí - SP), stack (Go, TypeScript, Python, IA), and highlighted projects (Harpia, OpenClaude, Lamed).
3. **Live Animated Contribution Heatmap**: Scraped from GitHub's public contribution calendar without tokens, featuring rounded boxes and diagonal reveal animation.
4. **Daily Action Cron**: GitHub Actions workflow that automatically refreshes contribution data and re-renders the heatmap SVG daily.

## System Architecture

```
[assets/IMG_2250.jpg] ──> [prep_photo.py] ──> [source-prepped.png] ──> [make_ascii_svg.py] ──> [matheus-ascii.svg]
                                                                                                 │
                                                        [make_info_card.py] ──────────────────> [info-card.svg]
                                                                                                 │
https://github.com/users/mat-dgruber/contributions ──> [fetch_contributions.py] ──> [data/contributions.json] ──> [render_heatmap_svg.py] ──> [contrib-heatmap.svg]
```

## Component Details

### 1. Photo Prep & ASCII SVG Generator
- **`scripts/prep_photo.py`**:
  - Input: `assets/IMG_2250.jpg`
  - Processing: Background removal via `rembg`, CLAHE local contrast enhancement via `opencv-python`, white background composite.
  - Output: `data/source-prepped.png`
- **`scripts/make_ascii_svg.py`**:
  - Downsamples to character grid (~100x53 characters).
  - Uses monochrome density ramp: ` .`:-=+*cs#%@`
  - Encapsulates character rows in SVG `<clipPath>` elements animated with SMIL `<animate>` to simulate horizontal typing sweep per row.
  - Output: `matheus-ascii.svg`

### 2. Neofetch Info Card
- **`scripts/make_info_card.py`**:
  - Generates `info-card.svg` (490px width).
  - Terminal titlebar + key/value entries with staggered CSS fade/slide-in animation.
  - Key sections:
    - User: `mat-dgruber@CPB`
    - Role: `Engenheiro de Software Pleno`
    - Location: `Tatuí, SP - Brasil`
    - Stack: `Go | TypeScript | Python | AI & Agentes`
    - Highlights: `Harpia Compiler | OpenClaude CLI`

### 3. Contribution Heatmap
- **`scripts/fetch_contributions.py`**:
  - Fetches public HTML from `https://github.com/users/mat-dgruber/contributions`.
  - Parses grid with `BeautifulSoup` to extract daily contribution counts and color levels.
  - Generates `data/contributions.json`.
- **`scripts/render_heatmap_svg.py`**:
  - Renders 53-week x 7-day SVG calendar (860px width) with rounded rects.
  - Color palette: `#161b22`, `#0e4429`, `#006d32`, `#26a641`, `#39d353`, `#69f0a0`.
  - Staggered diagonal animation via CSS keyframes.
  - Includes legend and summary footer.
  - Output: `contrib-heatmap.svg`

### 4. Layout Integration in README.md
Placed immediately after the current top banner/badges section:
```html
<div align="center">
  <h3><code>matheus@github ~ $ ./contributions.sh</code></h3>
  <img src="./contrib-heatmap.svg" width="860" />

  <br><br>

  <h3><code>matheus@github ~ $ neofetch --user mat-dgruber</code></h3>
  <table>
    <tr>
      <td valign="top"><img src="./matheus-ascii.svg" width="370" /></td>
      <td valign="top"><img src="./info-card.svg" width="490" /></td>
    </tr>
  </table>
</div>
```

### 5. GitHub Actions Workflow
- **Path**: `.github/workflows/update-profile-art.yml`
- **Schedule**: Cron `"17 6 * * *"` daily + `workflow_dispatch`.
- **Dependencies**: `requests`, `beautifulsoup4`.
- **Steps**:
  1. Checkout repository.
  2. Setup Python 3.11.
  3. Install lightweight requirements (`scripts/requirements.txt`).
  4. Run `fetch_contributions.py` and `render_heatmap_svg.py`.
  5. Auto-commit changes to `data/contributions.json` and `contrib-heatmap.svg`.

## Verification & Self-Review
- **Completeness**: All files, paths, dependencies, and animations specified.
- **Consistency**: Dimensions match layout constraints (370px + 490px = 860px).
- **Scope**: Covers local SVG generation and GitHub Actions daily refresh without external service dependencies.

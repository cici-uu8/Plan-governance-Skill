#!/usr/bin/env python3
"""Generate synthetic README assets for the public repository.

This script renders the logo, hero banner, and example screenshots used in
the repository README files. It reads sample Markdown outputs from
`examples/` and writes PNG assets into `assets/`.
"""

from __future__ import annotations

from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "assets"
SAMPLES_DIR = ROOT / "examples"

BG = "#06141B"
PANEL = "#0B1F29"
PANEL_ALT = "#102A36"
TEXT = "#E8F1F4"
MUTED = "#9FB5BF"
TEAL = "#14B8A6"
TEAL_DARK = "#0F766E"
AMBER = "#F59E0B"
RED = "#F97316"
BLUE = "#38BDF8"
SLATE = "#334155"
INK = "#0F172A"
PAPER = "#F8FAFC"
GRID = "#173543"
WHITE = "#FFFFFF"

FONT_SANS = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_CJK = "/System/Library/Fonts/Hiragino Sans GB.ttc"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_SANS, size=size)


def cjk_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_CJK, size=size)


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: str, radius: int = 24, outline: str | None = None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font_obj: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    if " " not in text:
        current = ""
        lines: list[str] = []
        for char in text:
            probe = current + char
            if draw.textlength(probe, font=font_obj) <= max_width or not current:
                current = probe
            else:
                lines.append(current)
                current = char
        if current:
            lines.append(current)
        return lines
    words = text.split(" ")
    lines: list[str] = []
    current = ""
    for word in words:
        probe = word if not current else current + " " + word
        if draw.textlength(probe, font=font_obj) <= max_width or not current:
            current = probe
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def write_multiline(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, *, fill: str, font_obj: ImageFont.FreeTypeFont, max_width: int, line_gap: int = 10) -> int:
    x, y = xy
    lines: list[str] = []
    for paragraph in text.splitlines():
        if not paragraph:
            lines.append("")
            continue
        lines.extend(wrap_text(draw, paragraph, font_obj, max_width))
    line_height = font_obj.size + line_gap
    for idx, line in enumerate(lines):
        draw.text((x, y + idx * line_height), line, font=font_obj, fill=fill)
    return y + max(1, len(lines)) * line_height


def draw_badge(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, fill: str, text_fill: str = WHITE, *, bold: bool = True) -> int:
    use_cjk = any(ord(ch) > 127 for ch in text)
    f = cjk_font(24) if use_cjk else font(24, bold=bold)
    padding_x = 18
    padding_y = 10
    w = int(draw.textlength(text, font=f)) + padding_x * 2
    h = 24 + padding_y * 2
    rounded(draw, (x, y, x + w, y + h), fill=fill, radius=20)
    draw.text((x + padding_x, y + padding_y - 2), text, font=f, fill=text_fill)
    return w


def card_title(draw: ImageDraw.ImageDraw, x: int, y: int, text: str) -> int:
    draw.text((x, y), text, font=font(26, bold=True), fill=WHITE)
    return y + 42


def centered_text(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, *, font_obj: ImageFont.FreeTypeFont, fill: str) -> None:
    left, top, right, bottom = box
    bbox = draw.textbbox((0, 0), text, font=font_obj)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((left + (right - left - w) / 2, top + (bottom - top - h) / 2 - 2), text, font=font_obj, fill=fill)


def draw_arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], *, fill: str = TEAL, width: int = 5) -> None:
    sx, sy = start
    ex, ey = end
    draw.line((sx, sy, ex, ey), fill=fill, width=width)
    if ex >= sx:
        head = [(ex, ey), (ex - 18, ey - 11), (ex - 18, ey + 11)]
    else:
        head = [(ex, ey), (ex + 18, ey - 11), (ex + 18, ey + 11)]
    draw.polygon(head, fill=fill)


def draw_doc_icon(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, *, label: str, accent: str) -> None:
    rounded(draw, (x, y, x + w, y + h), fill=PAPER, radius=16, outline="#CBD5E1", width=2)
    draw.polygon([(x + w - 38, y), (x + w, y + 38), (x + w - 38, y + 38)], fill="#E2E8F0")
    draw.line((x + 24, y + 52, x + w - 40, y + 52), fill=accent, width=6)
    draw.line((x + 24, y + 82, x + w - 26, y + 82), fill="#CBD5E1", width=4)
    draw.line((x + 24, y + 108, x + w - 50, y + 108), fill="#CBD5E1", width=4)
    if label:
        centered_text(draw, (x + 18, y + h - 54, x + w - 18, y + h - 16), label, font_obj=font(19, bold=True), fill=INK)


def draw_graph_node(draw: ImageDraw.ImageDraw, x: int, y: int, r: int, *, fill: str, outline: str = BG) -> None:
    draw.ellipse((x - r, y - r, x + r, y + r), fill=fill, outline=outline, width=5)


def generate_logo() -> None:
    img = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    rounded(draw, (48, 48, 464, 464), fill=BG, radius=84, outline=TEAL_DARK, width=4)
    rounded(draw, (76, 76, 436, 436), fill=PANEL, radius=64, outline=GRID, width=2)

    draw_doc_icon(draw, 108, 118, 146, 188, label="", accent=BLUE)
    draw_doc_icon(draw, 148, 156, 146, 188, label="", accent=AMBER)

    points = [(186, 360), (246, 304), (296, 236), (366, 176)]
    branch = [(296, 236), (386, 310)]
    draw.line(points, fill=TEAL, width=12, joint="curve")
    draw.line(branch, fill=AMBER, width=8)
    for x, y in points[:-1]:
        draw_graph_node(draw, x, y, 18, fill=TEAL)
    draw_graph_node(draw, *points[-1], 26, fill=WHITE, outline=TEAL)
    draw_graph_node(draw, *branch[-1], 18, fill=AMBER)
    img.save(ASSETS_DIR / "logo.png")


def generate_banner() -> None:
    img = Image.new("RGBA", (1600, 900), BG)
    draw = ImageDraw.Draw(img)
    rounded(draw, (48, 48, 1552, 852), fill=PANEL, radius=40, outline=GRID, width=2)

    draw_badge(draw, 92, 88, "MIT", TEAL_DARK)
    draw_badge(draw, 208, 88, "Codex Plugin", PANEL_ALT)
    draw_badge(draw, 418, 88, "English / 简体中文", PANEL_ALT, bold=False)

    draw.text((92, 168), "PlanGraph", font=font(88, bold=True), fill=WHITE)
    write_multiline(
        draw,
        (92, 286),
        "CodeGraph for project plans: local-first lineage, mainline, impact, and governance for AI agents.",
        fill=TEXT,
        font_obj=font(34),
        max_width=720,
        line_gap=14,
    )

    draw.text((92, 430), "Why this exists", font=font(30, bold=True), fill=WHITE)
    write_multiline(
        draw,
        (92, 478),
        "Agents can read a plan file, but they often miss which plan is current, what it replaced, and what might break downstream. "
        "PlanGraph turns plan docs into a repo-visible graph of lineage, mainline, impact, and lifecycle state.",
        fill=MUTED,
        font_obj=font(26),
        max_width=720,
        line_gap=12,
    )

    rounded(draw, (900, 126, 1468, 780), fill=PANEL_ALT, radius=28, outline=GRID, width=2)
    draw.text((940, 168), "From plan files to agent context", font=font(29, bold=True), fill=WHITE)
    labels = [
        ("Docs", "plans, closeouts,\ndecisions"),
        ("Registry", "lifecycle +\nauthority"),
        ("Graph", "mainline, impact,\ncontext"),
        ("Agent", "reads the right\nsource of truth"),
    ]
    y = 248
    for index, (title, desc) in enumerate(labels):
        x = 950 + (index % 2) * 252
        if index == 2:
            y = 494
        rounded(draw, (x, y, x + 196, y + 138), fill=PANEL, radius=22, outline=GRID, width=2)
        draw.text((x + 24, y + 22), title, font=font(24, bold=True), fill=TEXT)
        write_multiline(draw, (x + 24, y + 62), desc, fill=MUTED, font_obj=font(18), max_width=148, line_gap=6)
    draw_arrow(draw, (1148, 318), (1198, 318), fill=TEAL, width=4)
    draw_arrow(draw, (1298, 392), (1298, 492), fill=TEAL, width=4)
    draw_arrow(draw, (1198, 564), (1148, 564), fill=TEAL, width=4)
    draw.text((950, 704), "The registry stays the source of truth.", font=font(22, bold=True), fill=AMBER)

    draw.text((92, 744), "Two entry phrases. Graph-aware upkeep after enablement.", font=font(24, bold=True), fill=AMBER)
    img.save(ASSETS_DIR / "hero-banner.png")


def generate_workflow_diagram() -> None:
    width, height = 1600, 760
    img = Image.new("RGBA", (width, height), BG)
    draw = ImageDraw.Draw(img)
    rounded(draw, (44, 44, width - 44, height - 44), fill=PANEL, radius=36, outline=GRID, width=2)
    draw.text((84, 82), "How PlanGraph Works", font=font(54, bold=True), fill=WHITE)
    draw.text((84, 150), "A local, registry-backed planning graph that agents can query before changing plans", font=font(24), fill=MUTED)

    columns = [
        (92, "Scattered plans", "current plans, old drafts,\ncloseouts, decisions"),
        (430, "Read-only scan", "find candidates without\nchanging graph state"),
        (768, "Canonical registry", "lifecycle, authority,\nsupersession links"),
        (1106, "Agent context", "mainline, lineage,\nimpact, conflicts"),
    ]
    top = 246
    card_w = 270
    card_h = 260
    for index, (x, title, desc) in enumerate(columns):
        rounded(draw, (x, top, x + card_w, top + card_h), fill=PANEL_ALT, radius=26, outline=GRID, width=2)
        draw.text((x + 28, top + 26), title, font=font(24, bold=True), fill=TEXT)
        write_multiline(draw, (x + 28, top + 66), desc, fill=MUTED, font_obj=font(18), max_width=210, line_gap=7)

        if index == 0:
            draw_doc_icon(draw, x + 46, top + 138, 82, 96, label="v1", accent=AMBER)
            draw_doc_icon(draw, x + 104, top + 118, 82, 96, label="v2", accent=TEAL)
            draw_doc_icon(draw, x + 160, top + 148, 82, 96, label="log", accent=BLUE)
        elif index == 1:
            rounded(draw, (x + 56, top + 138, x + 214, top + 194), fill=BG, radius=18, outline=GRID, width=2)
            centered_text(draw, (x + 56, top + 138, x + 214, top + 194), "init report", font_obj=font(19, bold=True), fill=TEAL)
            draw.line((x + 84, top + 218, x + 186, top + 218), fill=AMBER, width=8)
            draw.line((x + 84, top + 238, x + 152, top + 238), fill=GRID, width=8)
        elif index == 2:
            rows = [("active", TEAL), ("closed", BLUE), ("superseded", AMBER)]
            for offset, (label, color) in enumerate(rows):
                y = top + 132 + offset * 38
                draw.ellipse((x + 54, y + 6, x + 72, y + 24), fill=color)
                draw.text((x + 84, y), label, font=font(18, bold=True), fill=TEXT)
        else:
            nodes = [(x + 80, top + 210), (x + 140, top + 154), (x + 202, top + 210), (x + 140, top + 238)]
            draw.line((nodes[0], nodes[1], nodes[2], nodes[3], nodes[0]), fill=TEAL, width=5)
            draw.line((nodes[1], nodes[3]), fill=GRID, width=4)
            for n, color in zip(nodes, [TEAL, WHITE, AMBER, BLUE]):
                draw_graph_node(draw, n[0], n[1], 16, fill=color, outline=PANEL_ALT)

        if index < len(columns) - 1:
            draw_arrow(draw, (x + card_w + 16, top + 130), (x + card_w + 68, top + 130), fill=TEAL, width=5)

    rounded(draw, (92, 574, width - 92, 676), fill=BG, radius=24, outline=GRID, width=2)
    draw.text((132, 606), "Why it matters:", font=font(25, bold=True), fill=AMBER)
    draw.text((324, 606), "agents stop guessing from chat history and read repo-visible plan state instead.", font=font(25, bold=True), fill=TEXT)
    img.save(ASSETS_DIR / "how-it-works.png")


def read_text(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def render_report(lines: list[str], title: str, subtitle: str, out_name: str) -> None:
    width, height = 1600, 1040
    img = Image.new("RGBA", (width, height), BG)
    draw = ImageDraw.Draw(img)
    rounded(draw, (40, 40, width - 40, height - 40), fill=PANEL, radius=36, outline=GRID, width=2)
    draw.text((84, 82), title, font=font(54, bold=True), fill=WHITE)
    draw.text((84, 150), subtitle, font=font(24), fill=MUTED)

    content_box = (84, 208, width - 84, height - 84)
    rounded(draw, content_box, fill=PANEL_ALT, radius=24, outline=GRID, width=2)
    x = content_box[0] + 28
    y = content_box[1] + 28
    max_width = content_box[2] - content_box[0] - 56

    mono = font(20)
    heading = font(22, bold=True)
    table_font = font(18)

    for raw in lines[:38]:
        line = raw.rstrip()
        if not line:
            y += 16
            continue
        if line.startswith("#"):
            level_text = line.lstrip("# ").strip()
            draw.text((x, y), level_text, font=heading, fill=WHITE)
            y += 34
            continue
        if line.startswith("|"):
            color = TEAL if "---" not in line else GRID
            current_font = table_font
        elif line.startswith("- ") or line[:2].isdigit() and line[1:3] == ". ":
            color = TEXT
            current_font = mono
        elif line.startswith("`") or line.startswith('"'):
            color = TEAL
            current_font = mono
        else:
            color = TEXT
            current_font = mono
        y = write_multiline(draw, (x, y), line, fill=color, font_obj=current_font, max_width=max_width, line_gap=6) + 4
        if y > content_box[3] - 50:
            break

    img.save(ASSETS_DIR / out_name)


def parse_markdown_table(lines: list[str]) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if set(stripped.replace("|", "").replace("-", "").replace(":", "").strip()) == set():
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        rows.append(cells)
    return rows


def render_registry_table(lines: list[str]) -> None:
    width, height = 1600, 960
    img = Image.new("RGBA", (width, height), BG)
    draw = ImageDraw.Draw(img)
    rounded(draw, (40, 40, width - 40, height - 40), fill=PANEL, radius=36, outline=GRID, width=2)
    draw.text((84, 82), "Plan registry", font=font(54, bold=True), fill=WHITE)
    draw.text((84, 150), "Canonical registry for active, historical, and superseded plan docs", font=font(24), fill=MUTED)

    header_y = 248
    columns = [
        ("Plan ID", 132),
        ("Role", 380),
        ("Path", 580),
        ("Lifecycle", 1088),
        ("Source", 1300),
    ]
    rows = parse_markdown_table(lines)[1:]
    normalized = []
    for row in rows:
        normalized.append([
            row[0],
            row[3],
            row[2],
            row[5],
            row[8],
        ])

    rounded(draw, (84, 210, width - 84, 850), fill=PANEL_ALT, radius=24, outline=GRID, width=2)
    rounded(draw, (104, header_y, width - 104, header_y + 54), fill=TEAL_DARK, radius=16)
    for label, x in columns:
        draw.text((x, header_y + 14), label, font=font(22, bold=True), fill=WHITE)

    row_y = header_y + 82
    row_height = 92
    for index, row in enumerate(normalized):
        bg = PANEL if index % 2 == 0 else PANEL_ALT
        rounded(draw, (104, row_y - 10, width - 104, row_y + row_height - 14), fill=bg, radius=16, outline=GRID, width=1)
        draw.text((84, 0), "", font=font(1), fill=WHITE)
        draw.text((columns[0][1], row_y), row[0], font=font(20, bold=True), fill=TEXT)
        draw.text((columns[1][1], row_y), row[1], font=font(20), fill=TEXT)
        write_multiline(draw, (columns[2][1], row_y), row[2], fill=TEXT, font_obj=font(18), max_width=440, line_gap=4)
        draw.text((columns[3][1], row_y), row[3], font=font(20), fill=AMBER if row[3] == "active" else TEXT)
        draw.text((columns[4][1], row_y), row[4], font=font(18), fill=TEAL)
        row_y += row_height

    img.save(ASSETS_DIR / "screenshot-registry.png")


def generate_report_assets() -> None:
    render_report(
        read_text(SAMPLES_DIR / "plan_adoption_report.sample.md"),
        "Adoption report",
        "Read-only bootstrap analysis for brownfield repositories",
        "screenshot-adoption-report.png",
    )
    render_registry_table(read_text(SAMPLES_DIR / "plan_registry.sample.md"))
    render_report(
        read_text(SAMPLES_DIR / "plan_timeline_report.sample.md"),
        "Timeline report",
        "Derived lifecycle view after governance is enabled",
        "screenshot-timeline.png",
    )


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    generate_logo()
    generate_banner()
    generate_workflow_diagram()
    generate_report_assets()
    print("Generated README assets in", ASSETS_DIR)


if __name__ == "__main__":
    main()

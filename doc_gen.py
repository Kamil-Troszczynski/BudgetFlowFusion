#!/usr/bin/env python3
"""
Generate BudgetFlowFusion documentation from doc/*.rst into:
- doc/build/html/index.html
- doc/build/pdf/BudgetFlowFusion_documentation.pdf

The generator intentionally uses only the Python standard library. It is
not a full reStructuredText implementation; it supports the subset used
by this project documentation: headings, paragraphs, bullet lists,
numbered lists, literal code blocks and inline code markers.
"""

from __future__ import annotations

import html
import re
import textwrap
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DOC_DIR = ROOT / "doc"
BUILD_DIR = DOC_DIR / "build"
HTML_DIR = BUILD_DIR / "html"
PDF_DIR = BUILD_DIR / "pdf"
PDF_PATH = PDF_DIR / "BudgetFlowFusion_documentation.pdf"

ORDER = [
    "index.rst",
    "01_wprowadzenie.rst",
    "02_analiza_i_projekt.rst",
    "03_architektura.rst",
    "04_model_danych.rst",
    "05_procesy_biznesowe.rst",
    "06_api_backend.rst",
    "07_dokumentacja_uzytkownika.rst",
    "08_uruchomienie_testy.rst",
    "09_utrzymanie_slownik.rst",
]


def read_sources() -> list[tuple[str, str]]:
    sources: list[tuple[str, str]] = []
    for filename in ORDER:
        path = DOC_DIR / filename
        if path.exists():
            sources.append((filename, path.read_text(encoding="utf-8")))
    return sources


def slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-") or "section"


def inline_markup(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"``(.+?)``", r"<code>\1</code>", escaped)
    return escaped


def rst_to_blocks(text: str) -> list[dict[str, object]]:
    lines = text.splitlines()
    blocks: list[dict[str, object]] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        if i + 1 < len(lines):
            underline = lines[i + 1].strip()
            if underline and set(underline) <= {"="} and len(underline) >= len(line.strip()):
                blocks.append({"type": "heading", "level": 1, "text": line.strip()})
                i += 2
                continue
            if underline and set(underline) <= {"-"} and len(underline) >= len(line.strip()):
                blocks.append({"type": "heading", "level": 2, "text": line.strip()})
                i += 2
                continue
            if underline and set(underline) <= {"~"} and len(underline) >= len(line.strip()):
                blocks.append({"type": "heading", "level": 3, "text": line.strip()})
                i += 2
                continue

        if line.startswith(".. toctree::"):
            i += 1
            while i < len(lines) and (not lines[i].strip() or lines[i].startswith("   ") or lines[i].strip().startswith(":")):
                i += 1
            continue

        if line.startswith(".. code-block::"):
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            code_lines: list[str] = []
            while i < len(lines):
                if lines[i].startswith("   "):
                    code_lines.append(lines[i][3:])
                    i += 1
                    continue
                if not lines[i].strip():
                    code_lines.append("")
                    i += 1
                    continue
                break
            blocks.append({"type": "code", "text": "\n".join(code_lines).rstrip()})
            continue

        if re.match(r"\s*\* ", line):
            items: list[str] = []
            while i < len(lines) and re.match(r"\s*\* ", lines[i]):
                item = re.sub(r"^\s*\* ", "", lines[i]).strip()
                i += 1
                while i < len(lines) and lines[i].startswith("  ") and not re.match(r"\s*\* ", lines[i]):
                    item += " " + lines[i].strip()
                    i += 1
                items.append(item)
            blocks.append({"type": "ul", "items": items})
            continue

        if re.match(r"\s*\d+\. ", line):
            items = []
            while i < len(lines) and re.match(r"\s*\d+\. ", lines[i]):
                item = re.sub(r"^\s*\d+\. ", "", lines[i]).strip()
                i += 1
                while i < len(lines) and lines[i].startswith("  ") and not re.match(r"\s*\d+\. ", lines[i]):
                    item += " " + lines[i].strip()
                    i += 1
                items.append(item)
            blocks.append({"type": "ol", "items": items})
            continue

        paragraph = line.strip()
        i += 1
        while i < len(lines) and lines[i].strip():
            next_line = lines[i]
            if i + 1 < len(lines) and set(lines[i + 1].strip()) <= {"=", "-", "~"} and lines[i + 1].strip():
                break
            if next_line.startswith(".. ") or re.match(r"\s*(\*|\d+\.) ", next_line):
                break
            paragraph += " " + next_line.strip()
            i += 1
        blocks.append({"type": "p", "text": paragraph})

    return blocks


def blocks_to_html(blocks: list[dict[str, object]]) -> str:
    html_blocks: list[str] = []
    for block in blocks:
        kind = block["type"]
        if kind == "heading":
            level = int(block["level"])
            text = str(block["text"])
            tag = f"h{level}"
            html_blocks.append(f'<{tag} id="{slugify(text)}">{inline_markup(text)}</{tag}>')
        elif kind == "p":
            html_blocks.append(f"<p>{inline_markup(str(block['text']))}</p>")
        elif kind == "code":
            html_blocks.append(f"<pre><code>{html.escape(str(block['text']))}</code></pre>")
        elif kind == "ul":
            items = "".join(f"<li>{inline_markup(str(item))}</li>" for item in block["items"])  # type: ignore[index]
            html_blocks.append(f"<ul>{items}</ul>")
        elif kind == "ol":
            items = "".join(f"<li>{inline_markup(str(item))}</li>" for item in block["items"])  # type: ignore[index]
            html_blocks.append(f"<ol>{items}</ol>")
    return "\n".join(html_blocks)


def title_from_blocks(blocks: list[dict[str, object]], fallback: str) -> str:
    for block in blocks:
        if block["type"] == "heading" and block["level"] == 1:
            return str(block["text"])
    return fallback


def build_html(sources: list[tuple[str, str]]) -> None:
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    rendered = []
    for filename, content in sources:
        blocks = rst_to_blocks(content)
        rendered.append((filename, title_from_blocks(blocks, filename), blocks_to_html(blocks)))

    nav = "\n".join(
        f'<a href="#{slugify(title)}">{html.escape(title)}</a>'
        for _, title, _ in rendered
    )
    sections = "\n".join(
        f'<section class="doc-section" id="{slugify(title)}">{body}</section>'
        for _, title, body in rendered
    )

    page = f"""<!doctype html>
<html lang="pl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>BudgetFlowFusion - dokumentacja</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f8fb;
      --paper: #ffffff;
      --text: #172033;
      --muted: #64748b;
      --line: #d8e0ea;
      --accent: #2457d6;
      --code: #0f172a;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, Segoe UI, Arial, sans-serif;
      color: var(--text);
      background: var(--bg);
      line-height: 1.62;
    }}
    .layout {{ display: grid; grid-template-columns: 290px minmax(0, 1fr); min-height: 100vh; }}
    aside {{
      position: sticky;
      top: 0;
      height: 100vh;
      overflow: auto;
      padding: 28px 22px;
      background: #101827;
      color: #e5edf8;
    }}
    aside h1 {{ font-size: 20px; line-height: 1.25; margin: 0 0 20px; }}
    aside a {{
      display: block;
      color: #cbd5e1;
      text-decoration: none;
      padding: 8px 0;
      border-bottom: 1px solid rgba(255,255,255,.08);
      font-size: 14px;
    }}
    main {{ padding: 42px; }}
    .paper {{
      max-width: 1080px;
      margin: 0 auto;
      padding: 42px;
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 10px;
      box-shadow: 0 18px 50px rgba(15, 23, 42, .08);
    }}
    h1 {{ font-size: 34px; margin: 0 0 22px; color: #0f172a; }}
    h2 {{ margin-top: 38px; padding-top: 20px; border-top: 1px solid var(--line); color: var(--accent); }}
    h3 {{ margin-top: 28px; color: #334155; }}
    p {{ margin: 12px 0; }}
    code {{ background: #eef2ff; padding: 2px 5px; border-radius: 4px; }}
    pre {{
      overflow-x: auto;
      padding: 18px;
      border-radius: 8px;
      background: var(--code);
      color: #e2e8f0;
      line-height: 1.35;
    }}
    pre code {{ background: transparent; padding: 0; color: inherit; }}
    li {{ margin: 6px 0; }}
    .doc-section + .doc-section {{ margin-top: 56px; }}
    @media print {{
      aside {{ display: none; }}
      .layout {{ display: block; }}
      main {{ padding: 0; }}
      .paper {{ border: 0; box-shadow: none; border-radius: 0; }}
      h1, h2, h3 {{ page-break-after: avoid; }}
      pre {{ white-space: pre-wrap; }}
    }}
    @media (max-width: 900px) {{
      .layout {{ grid-template-columns: 1fr; }}
      aside {{ position: static; height: auto; }}
      main {{ padding: 18px; }}
      .paper {{ padding: 24px; }}
    }}
  </style>
</head>
<body>
  <div class="layout">
    <aside>
      <h1>BudgetFlowFusion<br>Dokumentacja</h1>
      {nav}
    </aside>
    <main>
      <article class="paper">
        {sections}
      </article>
    </main>
  </div>
</body>
</html>
"""
    (HTML_DIR / "index.html").write_text(page, encoding="utf-8")


def pdf_text(text: str) -> str:
    text = (
        text.replace("–", "-")
        .replace("—", "-")
        .replace("•", "-")
        .replace("„", '"')
        .replace("”", '"')
        .replace("…", "...")
    )
    data = text.encode("cp1250", "replace")
    escaped = bytearray()
    for byte in data:
        if byte in (40, 41, 92):
            escaped.extend(b"\\" + bytes([byte]))
        elif byte < 32 or byte > 126:
            escaped.extend(f"\\{byte:03o}".encode("ascii"))
        else:
            escaped.append(byte)
    return escaped.decode("ascii")


def strip_inline_markup(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"``(.+?)``", r"\1", text)
    return text


def wrap_text(text: str, width: int) -> list[str]:
    cleaned = strip_inline_markup(text).strip()
    if not cleaned:
        return [""]
    return textwrap.wrap(
        cleaned,
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
    ) or [cleaned]


def pdf_encoding_object() -> bytes:
    # CP1250 byte positions for Polish characters mapped to Adobe glyph names.
    differences = (
        "140 /Sacute 143 /Zacute 156 /sacute 159 /zacute "
        "163 /Lslash 165 /Aogonek 175 /Zdotaccent "
        "179 /lslash 185 /aogonek 191 /zdotaccent "
        "198 /Cacute 202 /Eogonek 209 /Nacute 211 /Oacute "
        "230 /cacute 234 /eogonek 241 /nacute 243 /oacute"
    )
    return f"<< /Type /Encoding /BaseEncoding /WinAnsiEncoding /Differences [{differences}] >>".encode("ascii")


class PdfLayout:
    page_width = 595.0
    page_height = 842.0
    margin_left = 56.0
    margin_right = 56.0
    margin_top = 60.0
    margin_bottom = 58.0

    def __init__(self) -> None:
        self.pages: list[list[str]] = []
        self.current: list[str] = []
        self.y = self.page_height - self.margin_top
        self.section_titles: list[tuple[str, int]] = []
        self.page_title = ""
        self.new_page()

    def new_page(self) -> None:
        if self.current:
            self.pages.append(self.current)
        self.current = []
        self.y = self.page_height - self.margin_top

    def finish(self) -> list[str]:
        if self.current:
            self.pages.append(self.current)
            self.current = []
        page_count = len(self.pages)
        finalized = []
        for index, ops in enumerate(self.pages, start=1):
            footer = [
                "0.55 0.60 0.68 RG 0.55 w 56 42 m 539 42 l S",
                self.text_op(
                    56,
                    28,
                    "F1",
                    8,
                    "BudgetFlowFusion - dokumentacja",
                    color="0.35 0.40 0.48",
                ),
                self.text_op(
                    500,
                    28,
                    "F1",
                    8,
                    f"{index}/{page_count}",
                    color="0.35 0.40 0.48",
                ),
            ]
            finalized.append("\n".join(ops + footer))
        return finalized

    def ensure_space(self, height: float) -> None:
        if self.y - height < self.margin_bottom:
            self.new_page()

    @staticmethod
    def text_op(x: float, y: float, font: str, size: float, text: str, color: str = "0.08 0.12 0.20") -> str:
        return f"{color} rg BT /{font} {size} Tf 1 0 0 1 {x:.2f} {y:.2f} Tm ({pdf_text(text)}) Tj ET"

    def text(self, x: float, y: float, font: str, size: float, text: str, color: str = "0.08 0.12 0.20") -> None:
        self.current.append(self.text_op(x, y, font, size, text, color))

    def rect(self, x: float, y: float, width: float, height: float, fill: str, stroke: str | None = None) -> None:
        if stroke:
            self.current.append(f"{fill} rg {stroke} RG {x:.2f} {y:.2f} {width:.2f} {height:.2f} re B")
        else:
            self.current.append(f"{fill} rg {x:.2f} {y:.2f} {width:.2f} {height:.2f} re f")

    def cover(self) -> None:
        self.rect(0, 0, self.page_width, self.page_height, "0.96 0.98 1.00")
        self.rect(0, 712, self.page_width, 130, "0.06 0.10 0.18")
        self.text(56, 760, "F2", 28, "BudgetFlowFusion", "1 1 1")
        self.text(56, 724, "F1", 15, "Dokumentacja analityczno-projektowa i użytkowa", "0.82 0.89 1")
        self.text(56, 650, "F2", 16, "Zakres dokumentu")
        for item in [
            "analiza dziedziny i projektu",
            "architektura aplikacji",
            "diagramy i opis modelu danych",
            "procesy biznesowe",
            "API backendu",
            "instrukcja użytkownika",
            "uruchomienie, testy i utrzymanie",
        ]:
            self.text(76, self.y - 220, "F1", 11, f"- {item}")
            self.y -= 18
        self.new_page()

    def toc(self, rendered: list[tuple[str, str, list[dict[str, object]]]]) -> None:
        self.text(56, self.y, "F2", 22, "Spis treści", "0.10 0.25 0.55")
        self.y -= 34
        for _, title, _ in rendered:
            self.ensure_space(22)
            self.text(72, self.y, "F1", 11, title)
            self.y -= 20
        self.new_page()

    def heading(self, level: int, text: str) -> None:
        text = strip_inline_markup(text)
        if level == 1:
            if self.current and self.y < self.page_height - self.margin_top - 10:
                self.new_page()
            self.section_titles.append((text, len(self.pages) + 1))
            self.text(56, self.y, "F2", 21, text, "0.10 0.25 0.55")
            self.y -= 15
            self.current.append("0.16 0.34 0.84 RG 1.2 w 56 {:.2f} m 539 {:.2f} l S".format(self.y, self.y))
            self.y -= 28
        elif level == 2:
            self.ensure_space(54)
            self.y -= 10
            self.text(56, self.y, "F2", 15, text, "0.12 0.18 0.30")
            self.y -= 22
        else:
            self.ensure_space(42)
            self.text(56, self.y, "F2", 12, text, "0.20 0.26 0.38")
            self.y -= 18

    def paragraph(self, text: str, indent: float = 0, size: float = 10.2, leading: float = 14.2) -> None:
        width = 92 if indent == 0 else 84
        for line in wrap_text(text, width):
            self.ensure_space(leading + 2)
            self.text(self.margin_left + indent, self.y, "F1", size, line)
            self.y -= leading
        self.y -= 4

    def bullet_list(self, items: list[str], ordered: bool = False) -> None:
        for index, item in enumerate(items, start=1):
            prefix = f"{index}. " if ordered else "- "
            lines = wrap_text(item, 82)
            self.ensure_space(18)
            self.text(72, self.y, "F1", 10.2, prefix + lines[0])
            self.y -= 14.2
            for extra in lines[1:]:
                self.ensure_space(18)
                self.text(92, self.y, "F1", 10.2, extra)
                self.y -= 14.2
            self.y -= 2
        self.y -= 4

    def code_block(self, code: str) -> None:
        raw_lines = code.splitlines() or [""]
        lines: list[str] = []
        for raw in raw_lines:
            if len(raw) <= 92:
                lines.append(raw)
            else:
                lines.extend(textwrap.wrap(raw, width=92, replace_whitespace=False, drop_whitespace=False))
        line_height = 11.6
        index = 0
        while index < len(lines):
            max_lines = int((self.y - self.margin_bottom - 22) // line_height)
            if max_lines < 4:
                self.new_page()
                max_lines = int((self.y - self.margin_bottom - 22) // line_height)
            chunk = lines[index:index + max_lines]
            height = len(chunk) * line_height + 16
            self.rect(56, self.y - height + 5, 483, height, "0.95 0.97 1.00", "0.82 0.87 0.94")
            cy = self.y - 10
            for line in chunk:
                self.text(66, cy, "F3", 8.1, line, "0.08 0.12 0.20")
                cy -= line_height
            self.y -= height + 8
            index += len(chunk)

    def render_blocks(self, blocks: list[dict[str, object]]) -> None:
        for block in blocks:
            kind = block["type"]
            if kind == "heading":
                self.heading(int(block["level"]), str(block["text"]))
            elif kind == "p":
                self.paragraph(str(block["text"]))
            elif kind == "code":
                self.code_block(str(block["text"]))
            elif kind == "ul":
                self.bullet_list([str(item) for item in block["items"]])  # type: ignore[index]
            elif kind == "ol":
                self.bullet_list([str(item) for item in block["items"]], ordered=True)  # type: ignore[index]


def build_pdf(sources: list[tuple[str, str]]) -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    rendered: list[tuple[str, str, list[dict[str, object]]]] = []
    for filename, content in sources:
        blocks = rst_to_blocks(content)
        rendered.append((filename, title_from_blocks(blocks, filename), blocks))

    layout = PdfLayout()
    layout.cover()
    layout.toc(rendered)
    for _, _, blocks in rendered:
        layout.render_blocks(blocks)
    page_streams = layout.finish()

    objects: list[bytes] = []

    def add_object(data: bytes) -> int:
        objects.append(data)
        return len(objects)

    encoding_obj = add_object(pdf_encoding_object())
    font_obj = add_object(f"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding {encoding_obj} 0 R >>".encode("ascii"))
    bold_font_obj = add_object(f"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding {encoding_obj} 0 R >>".encode("ascii"))
    mono_font_obj = add_object(f"<< /Type /Font /Subtype /Type1 /BaseFont /Courier /Encoding {encoding_obj} 0 R >>".encode("ascii"))
    page_refs: list[int] = []
    content_refs: list[int] = []

    for page in page_streams:
        content = page.encode("cp1250", "replace")
        stream = b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"\nendstream"
        content_refs.append(add_object(stream))
        page_refs.append(0)

    kids_placeholder = b""
    pages_obj = add_object(kids_placeholder)

    for idx, content_ref in enumerate(content_refs):
        page_data = (
            f"<< /Type /Page /Parent {pages_obj} 0 R /MediaBox [0 0 595 842] "
            f"/Resources << /Font << /F1 {font_obj} 0 R /F2 {bold_font_obj} 0 R /F3 {mono_font_obj} 0 R >> >> "
            f"/Contents {content_ref} 0 R >>"
        ).encode("latin-1")
        page_refs[idx] = add_object(page_data)

    kids = " ".join(f"{ref} 0 R" for ref in page_refs)
    objects[pages_obj - 1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_refs)} >>".encode("latin-1")
    catalog_obj = add_object(f"<< /Type /Catalog /Pages {pages_obj} 0 R >>".encode("latin-1"))

    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for number, data in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{number} 0 obj\n".encode("latin-1"))
        output.extend(data)
        output.extend(b"\nendobj\n")
    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("latin-1"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))
    output.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_obj} 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("latin-1")
    )
    PDF_PATH.write_bytes(output)


def main() -> None:
    if not DOC_DIR.exists():
        raise SystemExit("Missing doc directory")
    sources = read_sources()
    if not sources:
        raise SystemExit("No .rst sources found in doc")
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    build_html(sources)
    build_pdf(sources)
    print(f"HTML: {HTML_DIR / 'index.html'}")
    print(f"PDF:  {PDF_PATH}")


if __name__ == "__main__":
    main()

"""
scrape_anthropic_article.py

Deterministically scrape an Anthropic engineering blog article into local markdown
plus local image assets.

USAGE
=====

Basic:
    py scrape_anthropic_article.py "<article_url>"

With explicit output directory:
    py scrape_anthropic_article.py "<article_url>" "G:\\repos\\AI\\RoadTrip\\evaluation"

Examples:
    py scrape_anthropic_article.py "https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents"
    py scrape_anthropic_article.py "https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents" "."
    py scrape_anthropic_article.py "https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents" "G:\\repos\\AI\\RoadTrip\\evaluation"

Behavior:
    - Derives a slug from the URL path (e.g., "demystifying-evals-for-ai-agents").
    - Fetches the page HTML with browser-like headers.
    - Extracts the main article content from <div class="page-wrapper">.
    - Converts the extracted HTML fragment into markdown (headings, lists, links, code blocks).
    - Writes markdown to:
        <output_dir>/<slug>.md
    - Scans the markdown for Anthropic CDN image references of the form:
        https://www.anthropic.com/_next/image?url=...
    - Downloads each image and saves it to:
        <output_dir>/<slug>-images/<original-filename>.png
    - Rewrites markdown image links to use the local relative paths:
        ![alt](<slug>-images/<original-filename>.png)

Notes:
    - This script is tailored for Anthropic engineering blog articles that use
      a top-level <div class="page-wrapper"> container.
    - Network errors, layout changes, or blocked requests may raise exceptions.
    - You can import `scrape_anthropic_article(url, out_dir)` from this file and
      call it directly from other Python code instead of using the CLI.
"""

from __future__ import annotations

import re
import sys
import urllib.request
from html import unescape
from pathlib import Path
from typing import Dict, Tuple
from urllib.parse import urlparse, parse_qs, unquote

# ---------- Core HTTP helpers ----------

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_text(url: str, timeout: int = 60) -> str:
    req = urllib.request.Request(url, headers=DEFAULT_HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
    return data.decode("utf-8", errors="replace")


def fetch_bytes(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers=DEFAULT_HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


# ---------- HTML → markdown extractor (div.page-wrapper) ----------

def extract_page_wrapper_html(html: str) -> str:
    start = html.find('class="page-wrapper"')
    if start < 0:
        raise RuntimeError("page-wrapper class not found")

    open_idx = html.rfind("<div", 0, start)
    if open_idx < 0:
        raise RuntimeError("opening <div> for page-wrapper not found")

    pos = open_idx
    depth = 0
    close_idx = -1
    length = len(html)

    while pos < length:
        n_open = html.find("<div", pos)
        n_close = html.find("</div>", pos)
        if n_close < 0:
            break
        if n_open != -1 and n_open < n_close:
            depth += 1
            pos = n_open + 4
        else:
            depth -= 1
            pos = n_close + 6
            if depth == 0:
                close_idx = pos
                break

    if close_idx < 0:
        raise RuntimeError("closing </div> for page-wrapper not found")

    frag = html[open_idx:close_idx]
    return frag


def html_fragment_to_markdown(fragment: str) -> str:
    frag = fragment

    # Strip scripts/styles/svg
    frag = re.sub(r"<script[^>]*>.*?</script>", "", frag, flags=re.S | re.I)
    frag = re.sub(r"<style[^>]*>.*?</style>", "", frag, flags=re.S | re.I)
    frag = re.sub(r"<svg[^>]*>.*?</svg>", "", frag, flags=re.S | re.I)

    # Headings h1-h6
    for i in range(6, 0, -1):
        pattern = rf"<h{i}[^>]*>(.*?)</h{i}>"

        def repl(m, lvl=i):
            inner = re.sub(r"<[^>]+>", "", m.group(1))
            inner = unescape(re.sub(r"\s+", " ", inner)).strip()
            return "\n" + ("#" * lvl) + " " + inner + "\n"

        frag = re.sub(pattern, repl, frag, flags=re.S | re.I)

    # Code blocks
    def code_repl(m):
        inner = re.sub(r"<[^>]+>", "", m.group(1))
        inner = unescape(inner).strip()
        return "\n```\n" + inner + "\n```\n"

    frag = re.sub(
        r"<pre[^>]*><code[^>]*>(.*?)</code></pre>",
        code_repl,
        frag,
        flags=re.S | re.I,
    )

    # Links
    def link_repl(m):
        href = m.group(1)
        text = re.sub(r"<[^>]+>", "", m.group(2))
        text = unescape(re.sub(r"\s+", " ", text)).strip()
        return f"[{text}]({href})"

    frag = re.sub(
        r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
        link_repl,
        frag,
        flags=re.S | re.I,
    )

    # Lists
    def li_repl(m):
        inner = re.sub(r"<[^>]+>", "", m.group(1))
        inner = unescape(re.sub(r"\s+", " ", inner)).strip()
        return "- " + inner + "\n"

    frag = re.sub(r"<li[^>]*>(.*?)</li>", li_repl, frag, flags=re.S | re.I)

    # Paragraph-like breaks
    frag = re.sub(r"</p\s*>", "\n\n", frag, flags=re.I)
    frag = re.sub(r"<br\s*/?>", "\n", frag, flags=re.I)

    # Strip remaining tags → plain text
    text = re.sub(r"<[^>]+>", "", frag)
    text = unescape(text)

    # Normalize whitespace
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    return text.strip()


# ---------- Image localization & renaming ----------

NEXT_IMAGE_PATTERN = re.compile(
    r"!\[([^\]]*)\]\((https://www\.anthropic\.com/_next/image\?url=[^)]+)\)"
)


def localize_anthropic_images(
    markdown: str,
    md_path: Path,
    slug: str,
) -> Tuple[str, Dict[str, Path]]:
    """
    Downloads Anthropic _next/image assets to <slug>-images/ and rewrites links.
    Returns (updated_markdown, mapping of remote->local paths).
    """
    img_dir = md_path.parent / f"{slug}-images"
    img_dir.mkdir(parents=True, exist_ok=True)

    replacements: Dict[str, str] = {}
    url_to_local: Dict[str, Path] = {}

    session_headers = {
        "User-Agent": DEFAULT_HEADERS["User-Agent"],
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    text = markdown

    for match in NEXT_IMAGE_PATTERN.finditer(markdown):
        alt, next_image_url = match.group(1), match.group(2)

        parsed = urlparse(next_image_url)
        qs = parse_qs(parsed.query)
        encoded_source = qs.get("url", [None])[0]
        if not encoded_source:
            continue

        source_url = unquote(encoded_source)
        source_name = Path(urlparse(source_url).path).name
        if not source_name:
            continue

        local_path = img_dir / source_name
        if not local_path.exists():
            req = urllib.request.Request(source_url, headers=session_headers)
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            local_path.write_bytes(data)

        rel = f"{slug}-images/{source_name}"
        full_original = match.group(0)
        full_replacement = f"![{alt}]({rel})"
        replacements[full_original] = full_replacement
        url_to_local[source_url] = local_path

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text, url_to_local


def slugify_from_url(url: str) -> str:
    parsed = urlparse(url)
    slug = Path(parsed.path.rstrip("/")).name or "article"
    # Basic cleanup
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", slug)
    return slug


# ---------- Top-level deterministic function ----------

def scrape_anthropic_article(url: str, out_dir: Path) -> Path:
    """
    Deterministically scrape an Anthropic engineering blog page into:
      - <slug>.md
      - <slug>-images/ (local images, human-readable names where possible)
    Returns the path to the markdown file.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = slugify_from_url(url)
    md_path = out_dir / f"{slug}.md"

    # 1) Fetch + extract fragment
    html = fetch_text(url)
    fragment = extract_page_wrapper_html(html)
    body_md = html_fragment_to_markdown(fragment)

    header = (
        f"# Demystifying evals for AI agents\n\n"
        f"Source: {url}\n\n"
        "Extracted from div.page-wrapper\n\n"
    )

    # 2) Localize images & rewrite links (if any Anthropic _next/image URLs later appear)
    text_with_header = header + body_md + "\n"
    text_localized, _ = localize_anthropic_images(text_with_header, md_path, slug)

    md_path.write_text(text_localized, encoding="utf-8")
    return md_path


# ---------- CLI entrypoint ----------

def main(argv: list[str]) -> None:
    if len(argv) < 2:
        print("Usage: py scrape_anthropic_article.py <url> [output_dir]")
        raise SystemExit(1)

    url = argv[1].strip()
    if len(argv) >= 3:
        out_dir = Path(argv[2])
    else:
        out_dir = Path(".")

    md_path = scrape_anthropic_article(url, out_dir)
    print(f"Wrote markdown to: {md_path}")
    images_dir = md_path.parent / f"{slugify_from_url(url)}-images"
    if images_dir.exists():
        print(f"Images folder: {images_dir}")
    else:
        print("No images folder created (no Anthropic _next/image assets found).")


if __name__ == "__main__":
    main(sys.argv)

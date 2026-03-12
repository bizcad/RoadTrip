#!/usr/bin/env python3
"""MCP server for deterministic generic page scraping to markdown.

Tools:
- scrape_page_to_markdown
- scrape_page_text_only
- scrape_pages_batch
"""

from __future__ import annotations

import re
import urllib.request
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urljoin, urlparse

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("page-scraper")

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

IMAGE_MD_PATTERN = re.compile(r"!\[([^\]]*)\]\((https?://[^)\s]+)\)")


def _resolve_path(path_value: str) -> Path:
    return Path(path_value).resolve()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _fetch_text(url: str, timeout: int = 60) -> str:
    req = urllib.request.Request(url, headers=DEFAULT_HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
    return data.decode("utf-8", errors="replace")


def _fetch_bytes(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers=DEFAULT_HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _slugify(text: str, fallback: str = "page") -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", text).strip("_")
    return cleaned or fallback


def _slug_from_url(url: str) -> str:
    parsed = urlparse(url)
    host = _slugify(parsed.netloc.replace("www.", ""), fallback="site")
    path_name = Path(parsed.path.rstrip("/")).name
    path_part = _slugify(path_name, fallback="home")
    return f"{host}-{path_part}"


def _extract_tag_block(html: str, start_idx: int, tag_name: str) -> str:
    pos = start_idx
    depth = 0
    length = len(html)
    open_pattern = re.compile(rf"<{tag_name}(\s|>)", re.I)
    close_pattern = re.compile(rf"</{tag_name}\s*>", re.I)

    while pos < length:
        open_match = open_pattern.search(html, pos)
        close_match = close_pattern.search(html, pos)

        if close_match is None:
            break

        if open_match is not None and open_match.start() < close_match.start():
            depth += 1
            pos = open_match.end()
        else:
            depth -= 1
            pos = close_match.end()
            if depth == 0:
                return html[start_idx:pos]

    return html[start_idx:]


def _extract_best_fragment(html: str) -> str:
    candidates = [
        (r"<article(\s|>)", "article"),
        (r"<main(\s|>)", "main"),
        (r"<div[^>]*class=\"[^\"]*page-wrapper[^\"]*\"", "div"),
        (r"<body(\s|>)", "body"),
    ]

    for pattern, tag in candidates:
        match = re.search(pattern, html, flags=re.I)
        if not match:
            continue
        if tag == "div":
            # Find the closest opening <div> for matched class.
            open_idx = html.rfind("<div", 0, match.start())
            if open_idx >= 0:
                return _extract_tag_block(html, open_idx, "div")
            continue
        return _extract_tag_block(html, match.start(), tag)

    return html


def _extract_title(html: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.S | re.I)
    if not match:
        return "Untitled Page"
    title = re.sub(r"<[^>]+>", "", match.group(1))
    title = unescape(re.sub(r"\s+", " ", title)).strip()
    return title or "Untitled Page"


def _decode_next_image_url(url: str) -> str:
    parsed = urlparse(url)
    if "_next/image" not in parsed.path:
        return url
    qs = parse_qs(parsed.query)
    source = qs.get("url", [None])[0]
    if not source:
        return url
    return unquote(source)


def _html_fragment_to_markdown(fragment: str, base_url: str) -> str:
    frag = fragment

    # Remove non-content elements.
    frag = re.sub(r"<script[^>]*>.*?</script>", "", frag, flags=re.S | re.I)
    frag = re.sub(r"<style[^>]*>.*?</style>", "", frag, flags=re.S | re.I)
    frag = re.sub(r"<noscript[^>]*>.*?</noscript>", "", frag, flags=re.S | re.I)
    frag = re.sub(r"<svg[^>]*>.*?</svg>", "", frag, flags=re.S | re.I)

    # Code blocks first to preserve formatting.
    def _code_block_repl(match: re.Match[str]) -> str:
        inner = re.sub(r"<[^>]+>", "", match.group(1))
        inner = unescape(inner).strip("\n")
        return f"\n```\n{inner}\n```\n"

    frag = re.sub(
        r"<pre[^>]*><code[^>]*>(.*?)</code></pre>",
        _code_block_repl,
        frag,
        flags=re.S | re.I,
    )

    # Inline code.
    def _inline_code_repl(match: re.Match[str]) -> str:
        inner = re.sub(r"<[^>]+>", "", match.group(1))
        inner = unescape(re.sub(r"\s+", " ", inner)).strip()
        return f"`{inner}`" if inner else ""

    frag = re.sub(r"<code[^>]*>(.*?)</code>", _inline_code_repl, frag, flags=re.S | re.I)

    # Headings.
    for lvl in range(6, 0, -1):
        pattern = rf"<h{lvl}[^>]*>(.*?)</h{lvl}>"

        def _heading_repl(match: re.Match[str], level: int = lvl) -> str:
            inner = re.sub(r"<[^>]+>", "", match.group(1))
            inner = unescape(re.sub(r"\s+", " ", inner)).strip()
            return "\n" + ("#" * level) + f" {inner}\n"

        frag = re.sub(pattern, _heading_repl, frag, flags=re.S | re.I)

    # Images.
    def _img_repl(match: re.Match[str]) -> str:
        tag = match.group(0)
        src_match = re.search(r'src\s*=\s*"([^"]+)"', tag, flags=re.I)
        alt_match = re.search(r'alt\s*=\s*"([^"]*)"', tag, flags=re.I)
        if not src_match:
            return ""

        src = _decode_next_image_url(src_match.group(1).strip())
        resolved_src = urljoin(base_url, src)
        alt = unescape(alt_match.group(1).strip()) if alt_match else ""
        return f"![{alt}]({resolved_src})"

    frag = re.sub(r"<img[^>]*>", _img_repl, frag, flags=re.S | re.I)

    # Links.
    def _link_repl(match: re.Match[str]) -> str:
        href = match.group(1).strip()
        text = re.sub(r"<[^>]+>", "", match.group(2))
        text = unescape(re.sub(r"\s+", " ", text)).strip()
        if not text:
            text = href
        resolved_href = urljoin(base_url, href)
        return f"[{text}]({resolved_href})"

    frag = re.sub(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', _link_repl, frag, flags=re.S | re.I)

    # Lists.
    def _li_repl(match: re.Match[str]) -> str:
        inner = re.sub(r"<[^>]+>", "", match.group(1))
        inner = unescape(re.sub(r"\s+", " ", inner)).strip()
        return f"- {inner}\n" if inner else ""

    frag = re.sub(r"<li[^>]*>(.*?)</li>", _li_repl, frag, flags=re.S | re.I)

    # Paragraph and block separators.
    frag = re.sub(r"</(p|div|section|article|main|header|footer|aside|blockquote|tr)\s*>", "\n\n", frag, flags=re.I)
    frag = re.sub(r"<(br|hr)\s*/?>", "\n", frag, flags=re.I)

    # Remove remaining tags.
    text = re.sub(r"<[^>]+>", "", frag)
    text = unescape(text)

    # Normalize whitespace.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    return text.strip() + "\n"


def _localize_images(markdown: str, md_path: Path, slug: str) -> tuple[str, list[dict[str, str]]]:
    img_dir = md_path.parent / f"{slug}-images"
    img_dir.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, str]] = []
    updated = markdown

    for match in IMAGE_MD_PATTERN.finditer(markdown):
        alt = match.group(1)
        remote_url = _decode_next_image_url(match.group(2))

        parsed = urlparse(remote_url)
        if parsed.scheme not in {"http", "https"}:
            continue

        name = Path(parsed.path).name
        if not name:
            name = f"image_{len(records)+1}.bin"

        name = _slugify(name, fallback=f"image_{len(records)+1}")
        local_file = img_dir / name

        if not local_file.exists():
            try:
                data = _fetch_bytes(remote_url)
                local_file.write_bytes(data)
            except Exception:
                continue

        rel = f"{slug}-images/{local_file.name}"
        old = match.group(0)
        new = f"![{alt}]({rel})"
        updated = updated.replace(old, new)
        records.append({"remote_url": remote_url, "local_path": str(local_file)})

    if not records and img_dir.exists():
        try:
            img_dir.rmdir()
        except OSError:
            pass

    return updated, records


def _scrape_to_markdown(url: str, output_dir: Path, localize_images: bool = True) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = _slug_from_url(url)

    html = _fetch_text(url)
    title = _extract_title(html)
    fragment = _extract_best_fragment(html)
    body_md = _html_fragment_to_markdown(fragment, base_url=url)

    md_path = output_dir / f"{slug}.md"
    header = "\n".join(
        [
            "---",
            f"source_url: {url}",
            f"retrieved_at_utc: {_utc_now_iso()}",
            f"title: {title}",
            f"slug: {slug}",
            "generator_mcp_server: mcp_server_page_scraper.py",
            "---",
            "",
            f"# {title}",
            "",
            f"Source: {url}",
            "",
        ]
    )

    markdown = header + body_md
    image_records: list[dict[str, str]] = []

    if localize_images:
        markdown, image_records = _localize_images(markdown, md_path, slug)

    md_path.write_text(markdown, encoding="utf-8")

    return {
        "status": "ok",
        "source_url": url,
        "output_file": str(md_path),
        "title": title,
        "slug": slug,
        "image_count": len(image_records),
        "images": image_records,
    }


@mcp.tool()
def scrape_page_to_markdown(
    url: str,
    output_dir: str = "analysis/ScrapedPages",
    localize_images: bool = True,
) -> dict[str, Any]:
    """Scrape a generic web page into markdown with optional local image localization."""
    try:
        return _scrape_to_markdown(
            url=url.strip(),
            output_dir=_resolve_path(output_dir),
            localize_images=localize_images,
        )
    except Exception as exc:
        return {
            "status": "error",
            "reason": "scrape_failed",
            "source_url": url,
            "error": str(exc),
        }


@mcp.tool()
def scrape_page_text_only(url: str) -> dict[str, Any]:
    """Scrape a generic page and return extracted markdown text in-memory only."""
    try:
        html = _fetch_text(url.strip())
        title = _extract_title(html)
        fragment = _extract_best_fragment(html)
        body_md = _html_fragment_to_markdown(fragment, base_url=url)
        return {
            "status": "ok",
            "source_url": url,
            "title": title,
            "markdown": body_md,
            "char_count": len(body_md),
        }
    except Exception as exc:
        return {
            "status": "error",
            "reason": "scrape_failed",
            "source_url": url,
            "error": str(exc),
        }


@mcp.tool()
def scrape_pages_batch(
    urls_csv: str,
    output_dir: str = "analysis/ScrapedPages",
    localize_images: bool = True,
) -> dict[str, Any]:
    """Scrape multiple pages from a comma-separated URL list into markdown files."""
    urls = [u.strip() for u in urls_csv.split(",") if u.strip()]
    if not urls:
        return {
            "status": "error",
            "reason": "no_urls_provided",
            "input": urls_csv,
        }

    out = _resolve_path(output_dir)
    results: list[dict[str, Any]] = []
    ok_count = 0

    for url in urls:
        item = scrape_page_to_markdown(url=url, output_dir=str(out), localize_images=localize_images)
        results.append(item)
        if item.get("status") == "ok":
            ok_count += 1

    return {
        "status": "ok",
        "requested": len(urls),
        "succeeded": ok_count,
        "failed": len(urls) - ok_count,
        "output_dir": str(out),
        "results": results,
    }


if __name__ == "__main__":
    mcp.run()

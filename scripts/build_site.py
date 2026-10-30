"""Build only the selected public learning pages; source notes stay unchanged."""
from __future__ import annotations

import argparse
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import re
import shutil
from urllib.parse import quote, unquote, urlsplit, urlunsplit

import markdown
from markdown.extensions.toc import slugify_unicode

ROOT = Path(__file__).resolve().parents[1]
NOTES = "notes/斋藤-深度学习入门"
GITHUB = "https://github.com/glance02/DeepLearning-MuLi-Notes"
ATTR = re.compile(r'''(?P<prefix>\b(?:href|src)\s*=\s*)(?P<q>["'])(?P<url>.*?)(?P=q)''', re.I)
ATTACHMENTS = {".pdf", ".py", ".ipynb", ".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp"}


class PageInfo(HTMLParser):
    def __init__(self, text: str):
        super().__init__()
        self.links: list[str] = []
        self.ids: set[str] = set()
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        for attr in ("href", "src"):
            if attrs.get(attr):
                self.links.append(attrs[attr])


def local_path(page: str, path: str) -> str:
    target = posixpath.normpath(posixpath.join(posixpath.dirname(page), unquote(path)))
    if target == ".." or target.startswith("../") or target.startswith("/"):
        raise ValueError(f"Link leaves the site: {page}: {path}")
    return target


def validate_site(output: Path) -> dict:
    pages = {p.relative_to(output).as_posix(): PageInfo(p.read_text(encoding="utf-8"))
             for p in output.rglob("*.html")}
    errors = []
    count = 0
    for page, info in pages.items():
        for url in info.links:
            parts = urlsplit(url)
            if parts.scheme or parts.netloc:
                continue
            target = local_path(page, parts.path) if parts.path else page
            if not (output / target).is_file():
                errors.append(f"{page}: missing {url}")
            elif parts.fragment and target in pages and unquote(parts.fragment) not in pages[target].ids:
                errors.append(f"{page}: missing anchor {url}")
            count += 1
    if errors:
        raise ValueError("Broken local links:\n" + "\n".join(errors))
    return {"pages": len(pages), "local_links": count}


def note_page(source: str, text: str, note_sources: list[str], titles: dict[str, str]) -> str:
    page = source.removesuffix(".md") + ".html"

    def relative(target):
        return quote(posixpath.relpath(target, posixpath.dirname(page)), safe="/")

    renderer = markdown.Markdown(
        extensions=["tables", "fenced_code", "toc", "pymdownx.arithmatex"],
        extension_configs={"toc": {"slugify": slugify_unicode}, "pymdownx.arithmatex": {"generic": True}},
        output_format="html",
    )
    body = renderer.convert(text)
    navigation = "".join(
        f'<a href="{relative(note.removesuffix(".md") + ".html")}"'
        f'{" aria-current=\"page\"" if note == source else ""}>{html.escape(titles[note])}</a>'
        for note in note_sources
    )
    # Remove the Markdown title, which is already displayed in the page header.
    body = re.sub(r"<h1\b([^>]*)>(.*?)</h1>", r'<span\1 hidden>\2</span>', body, count=1)
    title = html.escape(titles[source])
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · 深度学习手边册</title>
<link rel="stylesheet" href="{relative('assets/teach.css')}">
<link rel="stylesheet" href="{relative('assets/site-notes.css')}">
<script src="{relative('assets/teach.js')}" defer></script>
<script src="{relative('assets/site-math.js')}" defer></script>
<script src="{relative('assets/vendor/mathjax/tex-svg-full.js')}" defer></script></head>
<body><div class="layout"><aside class="sidebar">
<a class="brand" href="{relative('reference/index.html')}"><small>DEEP LEARNING / NOTES</small>深度学习 · 手边册</a>
<p class="side-label">斋藤 · 学习笔记</p><nav class="side-links" aria-label="章节导航">{navigation}</nav>
<p class="side-label">回查与练习</p><nav class="side-links">
<a href="{relative('reference/index.html')}">公式 · 概念 · 代码</a>
<a href="{relative('reference/index.html')}#review">交互短练习</a></nav>
<button class="secondary print-button" data-print type="button">打印当前页</button></aside>
<main class="main reading"><header class="hero"><p class="eyebrow">STUDY NOTES</p><h1>{title}</h1>
<p class="lead">斋藤康毅《深度学习入门》 · 结合自己的代码逐章回顾。</p></header>
<details class="note-toc"><summary>本页目录</summary>{renderer.toc}</details>
<article class="note-content">{body}</article>
<footer class="footer"><a href="{GITHUB}/blob/main/{quote(source, safe='/')}">在 GitHub 阅读 Markdown 原文</a>
 · <a href="{relative('reference/index.html')}">返回手边册</a></footer></main></div></body></html>'''


def build_site(root: Path, output: Path, revision: str = "local") -> dict:
    root, output = root.resolve(), output.resolve()
    if output == root or root.is_relative_to(output):
        raise ValueError("Output must not contain the source repository")
    if output.exists() and any(output.iterdir()):
        raise ValueError(f"Output must be empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    notes = sorted(p.relative_to(root).as_posix() for p in (root / NOTES).rglob("*.md"))
    if not notes:
        raise ValueError("No selected notes found")
    titles = {}
    for note in notes:
        text = (root / note).read_text(encoding="utf-8")
        title = re.search(r"^#\s+(.+)$", text, re.M)
        titles[note] = title[1] if title else Path(note).stem
    pages = {p.relative_to(root).as_posix(): p.read_text(encoding="utf-8")
             for directory in ("lessons", "reference") for p in (root / directory).glob("*.html")}
    for note in notes:
        pages[note] = note_page(note, (root / note).read_text(encoding="utf-8"), notes, titles)
    page_targets = {p: p.removesuffix(".md") + ".html" if p.endswith(".md") else p for p in pages}
    copied = set()

    def copy_asset(target):
        if target not in copied:
            destination = output / target
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / target, destination)
            copied.add(target)

    def rewrite_url(page, url):
        parts = urlsplit(html.unescape(url))
        if parts.scheme or parts.netloc or not parts.path:
            return html.escape(html.unescape(url), quote=True)
        target = local_path(page, parts.path)
        if target in page_targets:
            destination = page_targets[target]
        elif target in page_targets.values():
            destination = target
        else:
            source = root / target
            if not source.exists():
                raise ValueError(f"Missing source: {page}: {url}")
            publish_asset = source.is_file() and (
                target.startswith("assets/") or
                (source.suffix.lower() in ATTACHMENTS and not target.startswith("notes/"))
            )
            if publish_asset:
                copy_asset(target)
                destination = target
            else:
                kind = "tree" if source.is_dir() else "blob"
                return html.escape(urlunsplit(("https", "github.com", f"/glance02/DeepLearning-MuLi-Notes/{kind}/main/{quote(target, safe='/')}", parts.query, parts.fragment)), quote=True)
        relative = posixpath.relpath(destination, posixpath.dirname(page_targets[page]))
        return html.escape(urlunsplit(("", "", quote(relative, safe="/"), parts.query, parts.fragment)), quote=True)

    for page, content in pages.items():
        content = ATTR.sub(lambda m: m["prefix"] + m["q"] + rewrite_url(page, m["url"]) + m["q"], content)
        destination = output / page_targets[page]
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
    copy_asset("assets/vendor/mathjax/LICENSE")
    report = validate_site(output)
    report.update({"revision": revision, "files": sum(p.is_file() for p in output.rglob("*")) + 1})
    (output / "build.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--revision", default="local")
    args = parser.parse_args()
    print(json.dumps(build_site(ROOT, args.output, args.revision), ensure_ascii=False))


if __name__ == "__main__":
    main()

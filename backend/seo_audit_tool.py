#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
seo_audit_tool.py v7.0 – Comprehensive SEO Crawler with on-demand sections
依赖：
  pip install playwright beautifulsoup4 extruct requests tldextract python-Wappalyzer
  playwright install firefox
"""

import argparse, json, re, sys, time
from pathlib import Path
from typing import Any, List
from urllib.parse import urljoin, urlparse

import extruct, requests
from bs4 import BeautifulSoup

UA = "Mozilla/5.0 (compatible; SEO-Audit/7.0; +https://github.com/yourname/seo-audit)"
HEADERS, TIMEOUT = {"User-Agent": UA}, 30

# ─────────── Fetchers ────────────────────────────────────────────────────
def fetch_rendered(url: str, wait_ms: int = 3000):
    from playwright.sync_api import sync_playwright
    t0 = time.time()
    with sync_playwright() as p:
        page = p.firefox.launch(headless=True).new_page(user_agent=UA)
        resp = page.goto(url, wait_until="networkidle", timeout=TIMEOUT * 1000)
        page.wait_for_timeout(wait_ms)
        html = page.content()
    return (
        resp.status if resp else 0,
        page.url if resp else url,
        resp.headers if resp else {},
        html,
        round((time.time() - t0) * 1000, 1),
        None,
    )


def fetch_static(url: str):
    t0 = time.time()
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, stream=True)
    return (
        r.status_code,
        r.url,
        dict(r.headers),
        r.text,
        round((time.time() - t0) * 1000, 1),
        round(r.elapsed.total_seconds() * 1000, 1),
    )

# ─────────── HTML Parser ──────────────────────────────────────────────────
def parse_html(html: str, base: str):
    soup = BeautifulSoup(html, "lxml")

    metas = {
        (m.get("name") or m.get("property") or "").lower(): m.get("content", "")
        for m in soup.find_all("meta") if m.get("content")
    }
    meta_desc = metas.get("description", "")

    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    visible = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
    text_ratio = round(len(visible) / max(len(html), 1) * 100, 2)
    first_para = next((p.get_text(strip=True) for p in soup.find_all("p", limit=1)), "")
    snippet = visible[:200] + ("…" if len(visible) > 200 else "")
    word_cnt = len(visible.split())

    render_mode = "csr"
    if soup.find(id="__NEXT_DATA__") or soup.find(id="__NUXT__"):
        render_mode = "hydrated-ssr" if text_ratio > 5 else "csr-hydrate"
    elif text_ratio > 5:
        render_mode = "ssr/ssg"

    sd_raw = extruct.extract(html, base_url=base, syntaxes=["json-ld", "microdata", "rdfa"])
    s_types = set()
    for blk in sd_raw.get("json-ld", []):
        t = blk.get("@type")
        s_types.update(t if isinstance(t, list) else [t] if t else [])
    for blk in sd_raw.get("microdata", []):
        s_types.update(blk.get("type", []))
    for blk in sd_raw.get("rdfa", []):
        s_types.update(blk.get("type", []))

    heads = [{"tag": h.name, "text": h.get_text(strip=True)} for h in soup.find_all(re.compile(r"h[1-6]"))]
    hcnt = lambda n: sum(1 for h in heads if h["tag"] == f"h{n}")

    links = [a["href"] for a in soup.find_all("a", href=True)]
    host = urlparse(base).netloc
    ext_links = [u for u in links if urlparse(u).netloc and urlparse(u).netloc != host]

    no_alt = [img.get("src", "") for img in soup.find_all("img") if not img.get("alt")]

    nav_links = list(
        dict.fromkeys(
            a.get_text(strip=True)
            for nav in soup.find_all("nav")
            for a in nav.find_all("a", href=True)
            if a.get_text(strip=True)
        )
    )

    forms = [
        {
            "action": f.get("action", ""),
            "method": (f.get("method") or "GET").upper(),
            "inputs": [i.get("name") or i.get("id") or "" for i in f.find_all("input") if i.get("name") or i.get("id")],
        }
        for f in soup.find_all("form")
    ]

    return {
        "title": soup.title.string.strip() if soup.title else "",
        "meta_description": meta_desc,
        "metas": metas,
        "canonical": bool(soup.find("link", rel=lambda v: v and v.lower() == "canonical")),
        "hreflang_count": len(soup.find_all("link", rel=lambda v: v and v.lower() == "alternate")),
        "social_tags_count": sum(1 for m in metas if m.startswith(("og:", "twitter:"))),
        "headings": heads,
        "h1_count": hcnt(1),
        "h2_count": hcnt(2),
        "h3_count": hcnt(3),
        "links_internal_count": len(links) - len(ext_links),
        "links_external_count": len(ext_links),
        "images_missing_alt_count": len(no_alt),
        "text_ratio_percent": text_ratio,
        "word_count": word_cnt,
        "visible_snippet": snippet,
        "first_paragraph": first_para,
        "render_mode": render_mode,
        "structured_data_count": sum(len(v) for v in sd_raw.values()),
        "schema_types": sorted(s_types),
        "structured_data": sd_raw,
        "nav_links": nav_links,
        "forms": forms,
    }

# ─────────── Helpers ─────────────────────────────────────────────────────
def parse_robots(base: str):
    url = urljoin(base, "/robots.txt")
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        lines = r.text.splitlines() if r.status_code == 200 else []
        sitemaps = [ln.split(":", 1)[1].strip() for ln in lines if ln.lower().startswith("sitemap:")]
        return {"status": r.status_code, "sitemaps": sitemaps, "raw": r.text}
    except Exception as e:
        return {"status": None, "error": str(e)}

def detect_security(h: dict):
    l = {k.lower(): v for k, v in h.items()}
    return {
        "hsts": "strict-transport-security" in l,
        "csp": "content-security-policy" in l,
        "other_security_headers": {k: v for k, v in h.items()
                                   if k.lower() in ("referrer-policy", "x-frame-options",
                                                    "x-content-type-options", "x-xss-protection")}
    }

def detect_stack(url: str, html: str):
    try:
        from Wappalyzer import Wappalyzer, WebPage
        resp = requests.Response(); resp._content, resp.url = html.encode(), url
        raw = Wappalyzer.latest().analyze(WebPage.new_from_response(resp))
        return sorted(raw) if isinstance(raw, set) else raw
    except Exception:
        return None

# ─────────── Report builders ─────────────────────────────────────────────
def build_core(rep):
    a, sec = rep["analysis"], rep["security"]
    return {
        "url": rep["url"],
        "status_code": rep["status_code"],
        "response_time_ms": rep["response_time_ms"],
        "ttfb_ms": rep["ttfb_ms"],
        "hsts": sec["hsts"], "csp": sec["csp"],
        "title": a["title"], "meta_description": a["meta_description"],
        "canonical_present": a["canonical"], "hreflang_count": a["hreflang_count"],
        "h1_count": a["h1_count"], "h2_count": a["h2_count"], "h3_count": a["h3_count"],
        "links_internal_count": a["links_internal_count"], "links_external_count": a["links_external_count"],
        "images_missing_alt_count": a["images_missing_alt_count"],
        "text_ratio_percent": a["text_ratio_percent"], "word_count": a["word_count"],
        "first_paragraph": a["first_paragraph"], "visible_snippet": a["visible_snippet"],
        "render_mode": a["render_mode"],
        "structured_data_count": a["structured_data_count"], "schema_types": a["schema_types"][:8],
        "nav_links": a["nav_links"][:8],
        "robots_status": rep["robots"]["status"], "sitemaps_count": len(rep["robots"]["sitemaps"])
    }

def quick_tips(rep):
    a = rep["analysis"]; tips = []
    if not a["meta_description"]: tips.append("❌ 缺 meta description")
    if a["text_ratio_percent"] < 5: tips.append(f"⚠️ 文字占比 {a['text_ratio_percent']}%（疑似 CSR）")
    if not a["canonical"]: tips.append("⚠️ 未检测 canonical")
    if rep["robots"]["status"] != 200: tips.append("⚠️ robots.txt 不可访问")
    if not rep["robots"]["sitemaps"]: tips.append("⚠️ 未声明 Sitemap")
    return tips or ["✅ 核心 SEO 要素齐全"]

# ─────────── Utilities ───────────────────────────────────────────────────
def get_by_path(d: Any, path: str) -> Any:
    """取 dict 的嵌套路径，如 'analysis.metas'"""
    cur = d
    for key in path.split("."):
        if isinstance(cur, dict) and key in cur:
            cur = cur[key]
        else:
            raise KeyError(f"path '{path}' not found")
    return cur

def dumps_safe(obj, **kw):
    """确保 set 可序列化"""
    def default(o):
        if isinstance(o, set): return list(o)
        raise TypeError
    return json.dumps(obj, default=default, ensure_ascii=False, **kw)

# ─────────── Main audit ──────────────────────────────────────────────────
def audit(url: str, render: bool, wait: int):
    status, final, headers, html, elapsed, ttfb = (
        fetch_rendered(url, wait) if render else fetch_static(url)
    )
    base = f"{urlparse(final).scheme}://{urlparse(final).netloc}"
    return {
        "url": final, "status_code": status, "response_time_ms": elapsed, "ttfb_ms": ttfb,
        "headers": headers,
        "analysis": parse_html(html, base),
        "robots": parse_robots(base),
        "security": detect_security(headers),
        "tech_stack": detect_stack(final, html),
    }

# ─────────── CLI ─────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser()
    p.add_argument("url")
    p.add_argument("--no-render", action="store_true")
    p.add_argument("--wait", type=int, default=3000, help="render wait ms")
    p.add_argument("--full", action="store_true", help="print full report")
    p.add_argument("--show", action="append", metavar="PATH", help="show specific section(s)")
    p.add_argument("-o", "--output", help="write full report to file")
    args = p.parse_args()

    rep = audit(args.url, not args.no_render, args.wait)

    # 写文件（始终写完整报告，方便留档）
    if args.output:
        Path(args.output).write_text(dumps_safe(rep, indent=2), encoding="utf-8")

    # 1️⃣ --full 优先
    if args.full:
        print(dumps_safe(rep, indent=2))
    else:
        # 2️⃣ 打印核心
        print(dumps_safe(build_core(rep), indent=2))
        # 3️⃣ 按需展开
        if args.show:
            for path in args.show:
                try:
                    val = get_by_path(rep, path)
                    print(f"\n### {path} ###")
                    print(dumps_safe(val, indent=2))
                except Exception as e:
                    print(f"[WARN] {path}: {e}", file=sys.stderr)

    # 快速提示
    print("\n=== QUICK TIPS ==="); [print("•", t) for t in quick_tips(rep)]

if __name__ == "__main__":
    main()

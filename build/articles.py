#!/usr/bin/env python3
"""One-off: turn the two standalone explainers (old writing/*/index.html) into build fragments.

Reads the ORIGINAL pages from git (HEAD), scopes their CSS under `.art`, drops their dark-mode
blocks (the site is light only), moves the title into the site's header band, and writes
build/src/article-<key>.{en,es}.html. Re-runnable: it always reads from git, never from the
built output.
"""
import re, subprocess, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES = {
    "small-mac": ("writing/small-mac-fast-ai/index.html", "Making a small Mac keep up with a big AI", "Aug 2026"),
    "chasing":   ("writing/chasing-80-tokens/index.html", "Chasing 80 tok/s", "Aug 2026"),
}

def git_show(path):
    return subprocess.run(["git", "show", f"HEAD:{path}"], cwd=ROOT, capture_output=True, text=True, check=True).stdout

def split_rules(css):
    """Yield (prelude, body) for top-level rules; body of @media stays as a string."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    i, n, out = 0, len(css), []
    while i < n:
        j = css.find("{", i)
        if j < 0: break
        pre = css[i:j].strip()
        d, k = 1, j + 1
        while d and k < n:
            d += {"{": 1, "}": -1}.get(css[k], 0); k += 1
        out.append((pre, css[j + 1:k - 1]))
        i = k
    return out

def scope_sel(sel):
    parts = []
    for s in sel.split(","):
        s = s.strip()
        if not s: continue
        if s in (":root", "html", "body"): parts.append(".art")
        elif s.startswith(":root"): parts.append(".art" + s[5:])
        elif s.startswith("*"): parts.append(".art " + s)
        elif s.startswith(":focus"): parts.append(".art " + s)
        else: parts.append(".art " + s)
    return ",".join(parts)

def scope(css):
    out = []
    for pre, body in split_rules(css):
        if pre.startswith("@media"):
            if "prefers-color-scheme" in pre: continue          # light only
            out.append(f"{pre}{{{scope(body)}}}")
        elif pre.startswith("@"):
            out.append(f"{pre}{{{body}}}")
        elif "data-theme" in pre:                                # dark-theme override block
            continue
        else:
            out.append(f"{scope_sel(pre)}{{{body}}}")
    return "\n".join(out)

EXTRA = """
.art{margin:0 auto;background:none;font-size:17px;line-height:1.65;color:var(--ink);font-family:var(--sans)}
.art .aw{max-width:760px;margin:0;padding:0 40px 0 0}
.art header.ahero{padding:6px 0 36px}
.art a{background:none;margin:0;padding:0}
.art h1,.art h2,.art h3{color:var(--ink)}
.art section:last-of-type{border-bottom:0}
.art footer{padding:30px 0 10px;margin:0}
@media (max-width:760px){.art .aw{padding:0 20px}}
"""

def build(key, src, title, when):
    h = git_show(src)
    css = re.search(r"<style[^>]*>(.*?)</style>", h, flags=re.S).group(1)
    body = h[h.index("</style>") + 8:].strip()
    body = body.replace('<div class="wrap" style="padding:0">', '<div>')
    body = body.replace('<div class="wrap">', '<div class="aw">', 1)
    body = re.sub(r'<h1>.*?</h1>\s*', "", body, count=1, flags=re.S)           # title moves to the band
    body = re.sub(r'<span class="kicker">.*?</span></span>\s*|<span class="kicker">.*?</span>\s*', lambda m: m.group(0), body, count=1)
    body = body.replace('href="mtp-moe-explainer.html"', 'href="{{url:article-chasing}}"')
    body = body.replace("&mdash;", ",")                                       # house rule: no dashes
    css = css.replace("header.hero", "header.ahero")                        # site CSS also has a .hero
    body = body.replace('<header class="hero">', '<header class="ahero">')
    scoped = scope(css) + EXTRA
    for lang, back, pub in (("en", "Writing", "In English"), ("es", "Escritos", "En inglés")):
        meta = f'{when} · {pub} · Technical article'
        frag = f'''{{{{sky_defs}}}}
<div class="pband">
{{{{sky_inner}}}}
  <div class="wrap pbw">
  <a class="back" href="{{{{url:writing}}}}">&larr; {back}</a>
  <h1 class="ph1">{title}</h1>
  <div class="pmeta mono">{meta}</div>
  </div>
</div>
<style>
{scoped}
</style>
<div class="wrap page art" style="padding-top:6px">
{body}
</div>
'''
        open(os.path.join(ROOT, f"build/src/article-{key}.{lang}.html"), "w").write(frag)
    print(key, len(scoped), "css bytes;", len(re.findall("[—–]", body)), "dashes left in body")

if __name__ == "__main__":
    for k, (s, t, w) in ARTICLES.items():
        build(k, s, t, w)

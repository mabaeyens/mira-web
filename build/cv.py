#!/usr/bin/env python3
"""Build the CV PDFs (EN, ES) from the markdown CVs kept in Proton Drive.

Usage: python3 build/cv.py
Output: assets/cv/miguel-baeyens-cv-en.pdf and -es.pdf

Public-site edits to the source text: the phone number and the notice-period / availability
lines are dropped, and em/en dashes are rewritten (house rule: no dashes in authored text).
"""
import html, os, re, subprocess, tempfile

SRC = os.path.expanduser("~/Library/CloudStorage/ProtonDrive-miguel.angel@baeyens.es-folder/Lumo/")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FILES = {"en": "CV externo — Analytics & AI.md", "es": "CV en español — Analítica e IA.md"}
RANGE = {"en": "to", "es": "a"}
DROP_H = re.compile(r"^##\s+(Availability|Disponibilidad)\b", re.I)

CSS = """
@page{size:A4;margin:16mm 16mm 15mm}
*{box-sizing:border-box}
body{font:9.6pt/1.42 -apple-system,"Helvetica Neue",Arial,sans-serif;color:#1d2029;margin:0}
h1{font-size:21pt;margin:0 0 2px;letter-spacing:-.01em}
.role{font-size:11.5pt;font-weight:600;color:#B8453B;margin:0 0 4px}
.contact{font-size:8.8pt;color:#555a68;margin:0 0 10px}
h2{font-size:10pt;text-transform:uppercase;letter-spacing:.09em;color:#B8453B;border-bottom:1px solid #d9dce4;
   padding-bottom:3px;margin:14px 0 6px}
h3{font-size:10.2pt;margin:9px 0 0}
.org{font-size:9pt;color:#555a68;margin:0 0 3px}
p{margin:3px 0}
ul{margin:3px 0 3px 15px;padding:0}
li{margin:1.5px 0}
h2,h3{break-after:avoid}h3+*,.org{break-after:avoid}li,p{orphans:3;widows:3}
"""

def clean(s, lang):
    s = re.sub(r"(?<=\w) – (?=\w)", f" {RANGE[lang]} ", s)      # date ranges
    s = re.sub(r"(?<=\d)–(?=\d)", "-", s)
    s = s.replace(" — ", ", ").replace("—", ", ").replace("–", "-")
    return s

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return s

def convert(md, lang):
    md = clean(md, lang)
    md = re.sub(r"\s*(Available with one month's notice\.|Disponibilidad: un mes de preaviso\.)", "", md)
    out, in_ul, skip = [], False, False
    lines = md.split("\n")
    n_h1 = 0
    for ln in lines:
        s = ln.rstrip()
        if s.startswith("## "):
            skip = bool(DROP_H.match(s))
        if skip:
            continue
        if in_ul and not s.startswith("- "):
            out.append("</ul>"); in_ul = False
        if not s.strip():
            continue
        if s.startswith("# "):
            out.append(f"<h1>{inline(s[2:])}</h1>"); n_h1 += 1
        elif s.startswith("## "):
            out.append(f"<h2>{inline(s[3:])}</h2>")
        elif s.startswith("### "):
            out.append(f"<h3>{inline(s[4:])}</h3>")
        elif s.startswith("- "):
            if not in_ul: out.append("<ul>"); in_ul = True
            out.append(f"<li>{inline(s[2:])}</li>")
        elif n_h1 == 1 and re.fullmatch(r"\*\*[^*]+\*\*", s) and "role" not in "".join(out[-1:]):
            out.append(f'<p class="role">{inline(s[2:-2])}</p>')
        elif "@" in s and "|" in s:
            parts = [p.strip() for p in s.split("|")]
            parts = [p for p in parts if not re.match(r"^\+?[\d\s]{9,}$", p)]   # drop the phone number
            out.append('<p class="contact">' + " · ".join(inline(p) for p in parts) + "</p>")
        elif re.match(r"^\*\*[^*]+\*\* \|", s):
            out.append(f'<p class="org">{inline(s)}</p>')
        else:
            out.append(f"<p>{inline(s)}</p>")
    if in_ul: out.append("</ul>")
    return "\n".join(out)

def main():
    os.makedirs(os.path.join(ROOT, "assets/cv"), exist_ok=True)
    for lang, name in FILES.items():
        md = open(SRC + name, encoding="utf-8").read()
        body = convert(md, lang)
        doc = f'<!doctype html><html lang="{lang}"><meta charset="utf-8"><title>Miguel Angel Baeyens de Arce, CV</title><style>{CSS}</style><body>{body}</body></html>'
        with tempfile.TemporaryDirectory() as d:
            h = os.path.join(d, "cv.html"); open(h, "w", encoding="utf-8").write(doc)
            pdf = os.path.join(ROOT, f"assets/cv/miguel-baeyens-cv-{lang}.pdf")
            subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                            f"--print-to-pdf={pdf}", "file://" + h], check=True, capture_output=True)
        print(pdf, len(re.findall("[—–]", doc)), "dashes left")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Static site builder for askmira.es.

Every page is a pair of fragments, build/src/<key>.en.html and build/src/<key>.es.html.
This script wraps each one in the shared head, nav, sky and footer, resolves
{{url:key}} placeholders for the language being built, and writes the result to
the path registered in PAGES. English lives at the site root, Spanish under /es/
(Aura's legal pages keep their historical Spanish paths so store links survive).

Run from the repo root:  python3 build/build.py
"""
import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import hashlib as _hl
def av(name):
    """/assets/<name>?v=<content hash>: a changed stylesheet or script gets a new URL, so phones never keep a stale copy."""
    try:
        h = _hl.md5(open(os.path.join(ROOT, "assets", name), "rb").read()).hexdigest()[:8]
    except OSError:
        return f"/assets/{name}"
    return f"/assets/{name}?v={h}"

SRC = os.path.join(ROOT, "build", "src")
PART = os.path.join(ROOT, "build", "partials")
SITE = "https://askmira.es"
GITHUB = "https://github.com/mabaeyens"

# key -> {lang: path}. A page is built only if both fragments exist.
PAGES = {
    "home": {"en": "/", "es": "/es/"},
    "about": {"en": "/about/", "es": "/es/sobre-mi/"},
    "writing": {"en": "/writing/", "es": "/es/escritos/"},
    "post-mcp-qlik": {"en": "/writing/mcp-qlik/", "es": "/es/escritos/mcp-qlik/"},
    "post-anthropic-extension": {"en": "/writing/anthropic-extension/", "es": "/es/escritos/anthropic-extension/"},
    "article-small-mac": {"en": "/writing/small-mac-fast-ai/", "es": "/es/escritos/small-mac-fast-ai/"},
    "article-chasing": {"en": "/writing/chasing-80-tokens/", "es": "/es/escritos/chasing-80-tokens/"},
    "post-programar": {"en": "/writing/programar/", "es": "/es/escritos/programar/"},
    "post-datos": {"en": "/writing/datos/", "es": "/es/escritos/datos/"},
    "post-strawberry": {"en": "/writing/strawberry/", "es": "/es/escritos/strawberry/"},
    "post-kasparov": {"en": "/writing/kasparov/", "es": "/es/escritos/kasparov/"},
    "post-qlik-llm": {"en": "/writing/qlik-llm/", "es": "/es/escritos/qlik-llm/"},
    "post-promesas": {"en": "/writing/promesas/", "es": "/es/escritos/promesas/"},
    "post-modelos": {"en": "/writing/modelos/", "es": "/es/escritos/modelos/"},
    "post-herramientas": {"en": "/writing/herramientas/", "es": "/es/escritos/herramientas/"},
    "post-mira-launch": {"en": "/writing/mira-launch/", "es": "/es/escritos/mira-launch/"},
    "mira": {"en": "/mira/", "es": "/es/mira/"},
    "mira-privacy": {"en": "/mira/privacy/", "es": "/es/mira/privacidad/"},
    "mira-support": {"en": "/mira/support/", "es": "/es/mira/soporte/"},
    "vera": {"en": "/vera/", "es": "/es/vera/"},
    "vera-privacy": {"en": "/vera/privacy/", "es": "/es/vera/privacidad/"},
    "vera-support": {"en": "/vera/support/", "es": "/es/vera/soporte/"},
    "aura": {"en": "/aura/", "es": "/es/aura/"},
    "aura-pebble": {"en": "/aura/pebble/", "es": "/es/aura/pebble/"},
    "aura-privacy": {"en": "/aura/privacy/", "es": "/aura/privacidad/"},
    "aura-support": {"en": "/aura/support/", "es": "/aura/soporte/"},
}

# Per-page metadata. css: stylesheet under /assets/. current: nav item to mark.
META = {
    "home": {
        "css": "home.css",
        "current": None,
        "en": ("Mira, Vera, Aura: apps that stay on your own devices",
               "Three small, finished apps that stay on the devices you already own: Mira, an AI assistant that runs on your Mac, iPhone and iPad; Vera, a Markdown editor for your git repos; Aura, a weather app for Spain. No accounts, no server of mine."),
        "es": ("Mira, Vera, Aura: apps que se quedan en tus dispositivos",
               "Tres apps pequeñas y terminadas que se quedan en los dispositivos que ya tienes: Mira, un asistente de IA que corre en tu Mac, iPhone e iPad; Vera, un editor de Markdown para tus repos git; Aura, una app del tiempo para España. Sin cuentas y sin un servidor mío."),
    },
}

META["about"] = {
    "css": "inner.css", "current": "about",
    "en": ("About and CV", "Principal Solutions Architect at Qlik in Madrid. The apps I build, my experience, and what I'm learning."),
    "es": ("Sobre mí y mi CV", "Principal Solutions Architect en Qlik, en Madrid. Las apps que construyo, mi experiencia y lo que estoy aprendiendo."),
}
META["writing"] = {
    "css": "inner.css", "current": "writing",
    "en": ("Writing", "Posts I first wrote on LinkedIn, in Spanish, with no feed and no character limit."),
    "es": ("Escritos", "Posts que escribí primero en LinkedIn, sin feed y sin límite de caracteres."),
}
META["post-programar"] = {
    "css": "inner.css", "current": "writing",
    "en": ('I am programming again after 18 years', 'My first program was in BASIC in the late 80s, and Claude Code finally got me back to programming after years away.'),
    "es": ("He vuelto a programar después de 18 años", "Mi primer programa fue en BASIC a finales de los 80. Dieciocho años después volví a programar."),
}

META["post-datos"] = dict(META["post-programar"], en=('My data is public!', 'I keep hearing "my data cannot leave here", and it is almost never true: your email, contracts and sales team already live on someone else\'s servers.'), es=('¡Mis datos son públicos!', 'Hay una frase que escucho mucho: "es que mis datos no pueden salir de aquí".'))
META["post-strawberry"] = dict(META["post-programar"], en=("Strawberries and AI: the r's in strawberry", 'How many R\'s are there in "strawberry"? Most LLMs got it wrong, and the AI is doing exactly what it was designed to do.'), es=('Las fresas y la IA: las r en strawberry', '¿Cuántas R hay en "strawberry"?'))
META["post-kasparov"] = dict(META["post-programar"], en=('AI is not new. It is just new for everyone at once', 'When Deep Blue beat Kasparov in 1997 I found it inevitable, and almost thirty years later the conversation about AI has barely changed.'), es=('La IA no es nueva. Solo es nueva para todos a la vez', 'En mayo de 1997, Deep Blue venció a Kasparov. Un evento fascinante. Recorté la noticia y la pegué en la portada del Manual de Referencia de C++ de McGraw-H'))
META["post-qlik-llm"] = dict(META["post-programar"], en=('Many on-prem customers ask me the same thing: "When does AI come to Qlik Sense on Windows?"', 'The short answer: it is not coming, not like in Cloud, because the compute it requires is impossible to reproduce on-prem.'), es=('Muchos clientes on-prem me preguntan lo mismo: "¿Cuándo llega la IA a Qlik Sense on Windows?"', 'La respuesta corta: no va a llegar. No como en Cloud. La capacidad de cómputo que requiere es imposible de reproducir on-prem.'))
META["post-promesas"] = dict(META["post-programar"], en=('Promises and results', 'In Q1 2026 tech laid off 80,000 people citing AI, yet most AI projects still fail to deliver the promised return.'), es=('Promesas y resultados', 'En el primer trimestre de 2026, el sector tecnológico dejó en la calle a 80.000 personas, principalmente en EEUU. La razón oficial, en la mayoría de los ca'))
META["post-modelos"] = dict(META["post-programar"], en=('The models are not the problem', 'The model is the starting point, not the destination: what decides whether something works is the ecosystem you build around it.'), es=('Los modelos no son el problema', 'Llevo semanas construyendo un agente en local y varias herramientas para que me ayude a programar y con tareas diarias. El modelo razona, genera código, ma'))
META["post-herramientas"] = dict(META["post-programar"], en=('Tools', 'Mira is the local AI I build on top of a model: web search, RAG, a web interface and mobile access, so my data never leaves my laptop.'), es=('Herramientas', 'Llevo varios posts hablando de mi proyecto. Ese proyecto tiene nombre: Mira. Viene de una necesidad concreta: una IA que me acompañe donde yo esté, que cor'))
META["post-mira-launch"] = dict(META["post-programar"], en=('A few weeks ago I named my project: Mira', 'Mira is my vision of running your own local AI on your own hardware, with full control of the environment, open and free.'), es=('Hace unas semanas le puse nombre a mi proyecto: Mira', '¿Qué es Mira? Mi visión de cómo poner en marcha tu IA local en tu propio hardware, con control total del entorno. Mira es mayormente Python. Las apps son S'))

META["post-mcp-qlik"] = dict(META["post-programar"], en=('MCP server for on-prem Qlik Sense', 'I built my own MCP server so an LLM can help me with Qlik Sense: reading is free, and any change needs my approval first.'), es=('Servidor MCP para Qlik Sense on-prem', 'El valor de la IA está en integrarla con las herramientas que utilizamos cada día, y una que uso a diario, claro, es Qlik Sense.'))

META["post-anthropic-extension"] = dict(META["post-programar"], en=('When does AI come to Qlik Sense on Windows? Today.', 'It is still impossible to reproduce on-prem what the cloud does with its compute, but I spent months making it work somehow and today I am publishing the result.'), es=('¿Cuándo llega la IA a Qlik Sense on Windows? Hoy.', 'Una extensión de Qlik Sense on-prem que abre un asistente de IA sobre los datos de tus apps, con modelos cloud o locales.'))

META["article-small-mac"] = dict(META["post-programar"], en=("Making a small Mac keep up with a big AI", "Mira is a private AI assistant that runs entirely on one Mac. Over the holidays I tried to make it faster without making it dumber."), es=('Que un Mac pequeño aguante el ritmo de una IA grande', 'Cómo hice que Mira, mi asistente de IA privado, vaya más rápido en un Mac de 32 GB sin perder calidad: un modelo MoE, decodificación especulativa y mucha medición.'))
META["article-chasing"] = dict(META["post-programar"], en=("Chasing 80 tok/s", "A field guide to native multi-token prediction on a mixture-of-experts model, and an honest ledger of where the speed is still hiding."), es=('A por los 80 tok/s', 'Guía de campo sobre la predicción multi-token nativa en un modelo MoE y un registro honesto de dónde sigue escondida la velocidad hasta los 80 tok/s.'))

def app_meta(app, accent, en, es):
    return {"css": "inner.css", "extra": "app.css", "accent": accent, "app": app, "current": "apps", "en": en, "es": es}


META["mira"] = app_meta("mira", "#9A6A12",
    ("Mira: a local AI assistant for Mac, iPhone and iPad", "A finished AI assistant for Mac, iPhone and iPad. The Mac runs the models and your phone connects to it over your own private network. No cloud, no accounts."),
    ("Mira: un asistente de IA local para Mac, iPhone e iPad", "Un asistente de IA terminado para Mac, iPhone e iPad. El Mac ejecuta los modelos y tu móvil se conecta por tu propia red privada. Sin nube ni cuentas."))
META["vera"] = app_meta("vera", "#17787D",
    ("Vera: a native Markdown editor for your git repos", "A native iPhone, iPad and Mac app for the Markdown in your git repos and iCloud Drive. Free and open source."),
    ("Vera: un editor nativo de Markdown para tus repos git", "Una app nativa para iPhone, iPad y Mac para el Markdown de tus repos git y tu iCloud Drive. Gratis y de código abierto."))
META["aura"] = app_meta("aura", "#1F66B8",
    ("Aura: Spain's weather on every screen you own", "A weather app for Spain on AEMET open data: iPhone, iPad, Apple Watch and Android. No backend, no account, no telemetry."),
    ("Aura: el tiempo en España en todas tus pantallas", "Una app del tiempo para España con datos abiertos de AEMET: iPhone, iPad, Apple Watch y Android. Sin servidores, sin cuenta, sin telemetría."))
META["aura-pebble"] = app_meta("aura", "#1F66B8",
    ("Aura on Pebble: weather watchfaces and watchapps", "Aura Essential, Aura LCD, Aura Sky Weather and Aura Cityscape Weather for the Pebble Time 2. Free and open source."),
    ("Aura en Pebble: esferas y watchapps del tiempo", "Aura Essential, Aura LCD, Aura Sky Weather y Aura Cityscape Weather para el Pebble Time 2. Gratis y de código abierto."))

for _app, _acc, _name in (("mira", "#9A6A12", "Mira"), ("vera", "#17787D", "Vera"), ("aura", "#1F66B8", "Aura")):
    META[_app + "-privacy"] = app_meta(_app, _acc,
        (f"{_name}: privacy policy", f"The {_name} privacy policy."),
        (f"{_name}: política de privacidad", f"La política de privacidad de {_name}."))
    META[_app + "-support"] = app_meta(_app, _acc,
        (f"{_name}: help and support", f"Help and support for {_name}."),
        (f"{_name}: ayuda y soporte", f"Ayuda y soporte para {_name}."))
    for _k in (_app + "-privacy", _app + "-support"):
        META[_k]["current"] = None

UI = {
    "en": {
        "lang": "en", "apps": "Apps", "writing": "Writing", "about": "About",
        "mira_t": "AI assistant that runs on your own Mac", "mira_b": "In beta",
        "vera_t": "Markdown editor for your git repos", "vera_b": "App Store",
        "aura_t": "Weather for Spain, from AEMET data", "aura_b": "App Store",
        "privacy": "Privacy", "support": "Support", "theme": "Switch light or dark theme", "locale": "en_US",
    },
    "es": {
        "lang": "es", "apps": "Apps", "writing": "Escritos", "about": "Sobre mí",
        "mira_t": "Asistente de IA que corre en tu propio Mac", "mira_b": "En beta",
        "vera_t": "Editor de Markdown para tus repos git", "vera_b": "App Store",
        "aura_t": "El tiempo en España, con datos de AEMET", "aura_b": "App Store",
        "privacy": "Privacidad", "support": "Soporte", "theme": "Cambiar tema claro u oscuro", "locale": "es_ES",
    },
}


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def url(key, lang):
    return PAGES[key][lang]


def nav(lang, key, current, solid=False):
    u = UI[lang]
    other = "es" if lang == "en" else "en"

    def cur(name):
        return ' class="cur" aria-current="page"' if current == name else ""

    # The current language is plain text, the other one is the link target.
    switch = (
        '<span class="lang">'
        + (f'<b>EN</b> / <a href="{url(key, "es")}" hreflang="es" lang="es">ES</a>' if lang == "en"
           else f'<a href="{url(key, "en")}" hreflang="en" lang="en">EN</a> / <b>ES</b>')
        + "</span>"
    )
    toggle = (f'<button class="tt" type="button" onclick="miraTheme()" aria-label="{u["theme"]}" title="{u["theme"]}">'
              '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">'
              '<circle cx="10" cy="10" r="7"/><path d="M10 3a7 7 0 0 1 0 14z" fill="currentColor"/></svg></button>')
    dd_cur = " cur" if current == "apps" else ""
    return f"""<div class="bar{' solid' if solid else ''}"><div class="wrap">
  <a class="brand" href="{url('home', lang)}">askmira.es</a>
  <nav aria-label="{'Main' if lang == 'en' else 'Principal'}">
    <div class="dd-wrap">
      <a href="{url('home', lang)}#apps" class="dd-t{dd_cur}">{u['apps']} <svg width="10" height="10" viewBox="0 0 10 10" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M2 3.5l3 3 3-3"/></svg></a>
      <div class="dd">
        <a class="dd-i" href="{url('mira', lang)}"><img src="/assets/icon.png" alt=""><span><b style="color:var(--mira-s)">Mira</b><i>{u['mira_t']}</i></span><em>{u['mira_b']}</em></a>
        <a class="dd-i" href="{url('vera', lang)}"><img src="/vera/assets/icon.png" alt=""><span><b style="color:var(--vera-s)">Vera</b><i>{u['vera_t']}</i></span><em>{u['vera_b']}</em></a>
        <a class="dd-i" href="{url('aura', lang)}"><img src="/aura/assets/icon.png" alt=""><span><b style="color:var(--aura-s)">Aura</b><i>{u['aura_t']}</i></span><em>{u['aura_b']}</em></a>
      </div>
    </div>
    <a href="{url('writing', lang)}"{cur('writing')}>{u['writing']}</a><a href="{url('about', lang)}"{cur('about')}>{u['about']}</a><a href="{GITHUB}">GitHub</a>{switch}{toggle}
  </nav>
</div></div>"""


def foot(lang, inner=False, app="mira"):
    u = UI[lang]
    st = ' style="margin-top:50px"' if inner else ''
    return (f'<div class="wrap"><div class="foot mono"{st}><span>'
            f'<a href="{url(app + "-privacy", lang)}">{u["privacy"]}</a> · '
            f'<a href="{url(app + "-support", lang)}">{u["support"]}</a> · '
            f'<a href="{GITHUB}">GitHub</a></span></div></div>\n<script src="{av('zoom.js')}" defer></script>')


DARK_ACCENT = {"#9A6A12": "#E3A93A", "#17787D": "#46C2C8", "#1F66B8": "#6AAEF2"}

THEME_JS = ("<script>(function(){var d=document.documentElement,t;try{t=localStorage.getItem('mira-theme')}catch(e){}"
            "if(t!=='dark'&&t!=='light')t=matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light';"
            "d.setAttribute('data-theme',t);window.miraTheme=function(){var n=d.getAttribute('data-theme')==='dark'?'light':'dark';"
            "d.setAttribute('data-theme',n);try{localStorage.setItem('mira-theme',n)}catch(e){}"
            "var m=document.querySelector('meta[name=theme-color]');if(m)m.content=n==='dark'?'#121419':'#F1F2F5'}})()</script>")


def head(key, lang):
    m = META[key]
    title, desc = m[lang]
    u = UI[lang]
    other = "es" if lang == "en" else "en"
    canon = SITE + url(key, lang)
    alts = "".join(
        f'<link rel="alternate" hreflang="{l}" href="{SITE}{url(key, l)}">' for l in ("en", "es")
    ) + f'<link rel="alternate" hreflang="x-default" href="{SITE}{url(key, "en")}">'
    t, d = html.escape(title), html.escape(desc, quote=True)
    extra = ""
    if m.get("extra"):
        extra = f'\n<link rel="stylesheet" href="{av(m["extra"])}">\n<style>:root{{--app:{m["accent"]};--app-dk:{DARK_ACCENT.get(m["accent"], m["accent"])}}}</style>'
    return f"""<!DOCTYPE html>
<html lang="{u['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{canon}">
{alts}
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canon}">
<meta property="og:locale" content="{u['locale']}">
<meta property="og:image" content="{SITE}/assets/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#F1F2F5">
{THEME_JS}
<link rel="icon" href="/assets/icon.png" type="image/png">
<link rel="apple-touch-icon" href="/assets/icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{av(m['css'])}">{extra}
<link rel="stylesheet" href="{av('dark.css')}">
</head>"""


# Articles and posts: the language each was first written in. The other language is an AI translation.
ORIGINAL = {k: "es" for k in PAGES if k.startswith("post-")}
ORIGINAL.update({"article-small-mac": "en", "article-chasing": "en"})
# Full publication date of each article or post (LinkedIn publish date for the posts).
PUBDATE = {
    "post-qlik-llm": (2026, 3, 20), "post-strawberry": (2026, 3, 26), "post-kasparov": (2026, 3, 31),
    "post-datos": (2026, 4, 7), "post-promesas": (2026, 4, 21), "post-programar": (2026, 4, 27),
    "post-modelos": (2026, 5, 5), "post-herramientas": (2026, 5, 12), "post-mira-launch": (2026, 7, 10),
    "post-anthropic-extension": (2026, 9, 18), "post-mcp-qlik": (2026, 11, 21),
    "article-small-mac": (2026, 8, 19), "article-chasing": (2026, 8, 19),
}
MONTHS = {
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    "es": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
}
LANGNAME = {"en": {"en": "English", "es": "Spanish"}, "es": {"en": "ingl&eacute;s", "es": "espa&ntilde;ol"}}


def pmeta(key, lang, body):
    """Subheader under the title: full date, where it was first published, original language, AI translation."""
    orig = ORIGINAL.get(key)
    if not orig or key not in PUBDATE:
        return body
    y, m, d = PUBDATE[key]
    li = re.search(r'<a href="([^"]+)">LinkedIn</a>', body)
    parts = []
    if lang == "en":
        parts.append(f"{d} {MONTHS['en'][m - 1]} {y}")
        if li:
            parts.append(f'First published on <a href="{li.group(1)}">LinkedIn</a>')
        else:
            parts.append("Technical article")
        parts.append(f"Originally written in {LANGNAME['en'][orig]}")
        if orig != lang:
            parts.append("Translated to English with AI")
    else:
        parts.append(f"{d} de {MONTHS['es'][m - 1]} de {y}")
        if li:
            parts.append(f'Publicado antes en <a href="{li.group(1)}">LinkedIn</a>')
        else:
            parts.append("Art&iacute;culo t&eacute;cnico")
        parts.append(f"Escrito originalmente en {LANGNAME['es'][orig]}")
        if orig != lang:
            parts.append("Traducido al espa&ntilde;ol con IA")
    line = '<div class="pmeta mono">' + " &middot; ".join(parts) + "</div>"
    return re.sub(r'<div class="pmeta mono">.*?</div>', lambda _: line, body, count=1, flags=re.S)


def render(key, lang):
    body = read(os.path.join(SRC, f"{key}.{lang}.html"))
    body = body.replace("{{sky_defs}}", read(os.path.join(PART, "sky_defs.html")))
    body = body.replace("{{sky}}", read(os.path.join(PART, "sky.html")))
    body = body.replace("{{sky_inner}}", read(os.path.join(PART, "sky_inner.html")))
    body = re.sub(r"\{\{url:([a-z-]+)\}\}", lambda mm: url(mm.group(1), lang), body)
    body = pmeta(key, lang, body)
    left = re.findall(r"\{\{[^}]*\}\}", body)
    if left:
        sys.exit(f"{key}.{lang}: unresolved placeholders {left}")
    return head(key, lang) + "\n<body>\n" + nav(lang, key, META[key]["current"], META[key]["css"] != "home.css") + "\n" + body + "\n" + foot(lang, META[key]["css"] != "home.css", META[key].get("app", "mira")) + "\n</body>\n</html>\n"


def out_path(path):
    return os.path.join(ROOT, path.lstrip("/"), "index.html")


def main():
    built = []
    for key in PAGES:
        if key not in META:
            continue
        for lang in ("en", "es"):
            if not os.path.exists(os.path.join(SRC, f"{key}.{lang}.html")):
                continue
            dest = out_path(url(key, lang))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "w", encoding="utf-8") as f:
                f.write(render(key, lang))
            built.append(os.path.relpath(dest, ROOT))
    print("\n".join(built))


if __name__ == "__main__":
    main()

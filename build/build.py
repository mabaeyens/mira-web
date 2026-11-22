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
    "en": ("He vuelto a programar después de 18 años", "My first program was in BASIC in the late 80s. Eighteen years later I started coding again. Post in Spanish."),
    "es": ("He vuelto a programar después de 18 años", "Mi primer programa fue en BASIC a finales de los 80. Dieciocho años después volví a programar."),
}

META["post-datos"] = dict(META["post-programar"], en=("¡Mis datos son públicos!", "Hay una frase que escucho mucho: \"es que mis datos no pueden salir de aquí\"."), es=("¡Mis datos son públicos!", "Hay una frase que escucho mucho: \"es que mis datos no pueden salir de aquí\"."))
META["post-strawberry"] = dict(META["post-programar"], en=("Las fresas y la IA: las r en strawberry", "¿Cuántas R hay en \"strawberry\"?"), es=("Las fresas y la IA: las r en strawberry", "¿Cuántas R hay en \"strawberry\"?"))
META["post-kasparov"] = dict(META["post-programar"], en=("La IA no es nueva. Solo es nueva para todos a la vez", "En mayo de 1997, Deep Blue venció a Kasparov. Un evento fascinante. Recorté la noticia y la pegué en la portada del Manual de Referencia de C++ de McGraw-H"), es=("La IA no es nueva. Solo es nueva para todos a la vez", "En mayo de 1997, Deep Blue venció a Kasparov. Un evento fascinante. Recorté la noticia y la pegué en la portada del Manual de Referencia de C++ de McGraw-H"))
META["post-qlik-llm"] = dict(META["post-programar"], en=("Muchos clientes on-prem me preguntan lo mismo: \"¿Cuándo llega la IA a Qlik Sense on Windows?\"", "La respuesta corta: no va a llegar. No como en Cloud. La capacidad de cómputo que requiere es imposible de reproducir on-prem."), es=("Muchos clientes on-prem me preguntan lo mismo: \"¿Cuándo llega la IA a Qlik Sense on Windows?\"", "La respuesta corta: no va a llegar. No como en Cloud. La capacidad de cómputo que requiere es imposible de reproducir on-prem."))
META["post-promesas"] = dict(META["post-programar"], en=("Promesas y resultados", "En el primer trimestre de 2026, el sector tecnológico dejó en la calle a 80.000 personas, principalmente en EEUU. La razón oficial, en la mayoría de los ca"), es=("Promesas y resultados", "En el primer trimestre de 2026, el sector tecnológico dejó en la calle a 80.000 personas, principalmente en EEUU. La razón oficial, en la mayoría de los ca"))
META["post-modelos"] = dict(META["post-programar"], en=("Los modelos no son el problema", "Llevo semanas construyendo un agente en local y varias herramientas para que me ayude a programar y con tareas diarias. El modelo razona, genera código, ma"), es=("Los modelos no son el problema", "Llevo semanas construyendo un agente en local y varias herramientas para que me ayude a programar y con tareas diarias. El modelo razona, genera código, ma"))
META["post-herramientas"] = dict(META["post-programar"], en=("Herramientas", "Llevo varios posts hablando de mi proyecto. Ese proyecto tiene nombre: Mira. Viene de una necesidad concreta: una IA que me acompañe donde yo esté, que cor"), es=("Herramientas", "Llevo varios posts hablando de mi proyecto. Ese proyecto tiene nombre: Mira. Viene de una necesidad concreta: una IA que me acompañe donde yo esté, que cor"))
META["post-mira-launch"] = dict(META["post-programar"], en=("Hace unas semanas le puse nombre a mi proyecto: Mira", "¿Qué es Mira? Mi visión de cómo poner en marcha tu IA local en tu propio hardware, con control total del entorno. Mira es mayormente Python. Las apps son S"), es=("Hace unas semanas le puse nombre a mi proyecto: Mira", "¿Qué es Mira? Mi visión de cómo poner en marcha tu IA local en tu propio hardware, con control total del entorno. Mira es mayormente Python. Las apps son S"))

META["post-mcp-qlik"] = dict(META["post-programar"], en=("Servidor MCP para Qlik Sense on-prem", "El valor de la IA está en integrarla con las herramientas que utilizamos cada día, y una que uso a diario, claro, es Qlik Sense."), es=("Servidor MCP para Qlik Sense on-prem", "El valor de la IA está en integrarla con las herramientas que utilizamos cada día, y una que uso a diario, claro, es Qlik Sense."))

META["article-small-mac"] = dict(META["post-programar"], en=("Making a small Mac keep up with a big AI", "Mira is a private AI assistant that runs entirely on one Mac. Over the holidays I tried to make it faster without making it dumber."), es=("Making a small Mac keep up with a big AI", "Mira is a private AI assistant that runs entirely on one Mac. Over the holidays I tried to make it faster without making it dumber."))
META["article-chasing"] = dict(META["post-programar"], en=("Chasing 80 tok/s", "A field guide to native multi-token prediction on a mixture-of-experts model, and an honest ledger of where the speed is still hiding."), es=("Chasing 80 tok/s", "A field guide to native multi-token prediction on a mixture-of-experts model, and an honest ledger of where the speed is still hiding."))

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
        "vera_t": "Markdown editor for your git repos", "vera_b": "In beta",
        "aura_t": "Weather for Spain, from AEMET data", "aura_b": "App Store",
        "privacy": "Privacy", "support": "Support", "theme": "Switch light or dark theme", "locale": "en_US",
    },
    "es": {
        "lang": "es", "apps": "Apps", "writing": "Escritos", "about": "Sobre mí",
        "mira_t": "Asistente de IA que corre en tu propio Mac", "mira_b": "En beta",
        "vera_t": "Editor de Markdown para tus repos git", "vera_b": "En beta",
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
            f'<a href="{GITHUB}">GitHub</a></span></div></div>')


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
        extra = f'\n<link rel="stylesheet" href="/assets/{m["extra"]}">\n<style>:root{{--app:{m["accent"]};--app-dk:{DARK_ACCENT.get(m["accent"], m["accent"])}}}</style>'
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
<link rel="stylesheet" href="/assets/{m['css']}">{extra}
<link rel="stylesheet" href="/assets/dark.css">
</head>"""


def render(key, lang):
    body = read(os.path.join(SRC, f"{key}.{lang}.html"))
    body = body.replace("{{sky_defs}}", read(os.path.join(PART, "sky_defs.html")))
    body = body.replace("{{sky}}", read(os.path.join(PART, "sky.html")))
    body = body.replace("{{sky_inner}}", read(os.path.join(PART, "sky_inner.html")))
    body = re.sub(r"\{\{url:([a-z-]+)\}\}", lambda mm: url(mm.group(1), lang), body)
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

#!/usr/bin/env python3
"""Emit scripts/localized-product-i18n.mjs — run from repo root."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "localized-product-i18n.mjs"


def j(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def mk(es, de, fr, pt, zh, it, hi):
    return {"es": es, "de": de, "fr": fr, "pt": pt, "zh": zh, "it": it, "hi": hi}


def emit_tr(m: dict) -> str:
    return (
        f"{{ es: {j(m['es'])}, de: {j(m['de'])}, fr: {j(m['fr'])}, "
        f"pt: {j(m['pt'])}, zh: {j(m['zh'])}, it: {j(m['it'])}, hi: {j(m['hi'])} }}"
    )


FEATURE_FROM_APP = {
    "es": mk(
        "Identificar",
        "Identifizieren",
        "Identifier",
        "Identificar",
        "识别",
        "Identifica",
        "पहचानें",
    ),
}
# Fix FEATURE - need proper structure per key

FEATURE_FROM_APP = {
    "es": {
        "Identify": "Identificar",
        "Coach": "Coach",
        "My Museum": "Mi Museo",
        "Clock Repair Help": "Ayuda para reparar relojes",
        "Grail Radar": "Grail Radar",
        "Vault": "Bóveda",
        "Wish list": "Lista de deseos",
        "Reminders": "Recordatorios",
        "Export": "Exportar",
        "Import": "Importar",
        "Budget": "Presupuesto",
        "Debt": "Deuda",
    },
    "de": {
        "Identify": "Identifizieren",
        "Coach": "Coach",
        "My Museum": "Mein Museum",
        "Clock Repair Help": "Hilfe bei Uhrenreparatur",
        "Grail Radar": "Grail Radar",
        "Vault": "Tresor",
        "Wish list": "Wunschliste",
        "Reminders": "Erinnerungen",
        "Export": "Exportieren",
        "Import": "Importieren",
        "Budget": "Budget",
        "Debt": "Schulden",
    },
    "fr": {
        "Identify": "Identifier",
        "Coach": "Coach",
        "My Museum": "Mon musée",
        "Clock Repair Help": "Aide à la réparation d'horloges",
        "Grail Radar": "Grail Radar",
        "Vault": "Coffre",
        "Wish list": "Liste de souhaits",
        "Reminders": "Rappels",
        "Export": "Exporter",
        "Import": "Importer",
        "Budget": "Budget",
        "Debt": "Dette",
    },
    "pt": {
        "Identify": "Identificar",
        "Coach": "Coach",
        "My Museum": "O meu museu",
        "Clock Repair Help": "Ajuda para reparar relógios",
        "Grail Radar": "Grail Radar",
        "Vault": "Cofre",
        "Wish list": "Lista de desejos",
        "Reminders": "Lembretes",
        "Export": "Exportar",
        "Import": "Importar",
        "Budget": "Orçamento",
        "Debt": "Dívida",
    },
    "zh": {
        "Identify": "识别",
        "Coach": "Coach",
        "My Museum": "我的博物馆",
        "Clock Repair Help": "钟表维修帮助",
        "Grail Radar": "Grail Radar",
        "Vault": "保险库",
        "Wish list": "心愿单",
        "Reminders": "提醒",
        "Export": "导出",
        "Import": "导入",
        "Budget": "预算",
        "Debt": "债务",
    },
    "it": {
        "Identify": "Identifica",
        "Coach": "Coach",
        "My Museum": "Il mio museo",
        "Clock Repair Help": "Aiuto riparazione orologi",
        "Grail Radar": "Grail Radar",
        "Vault": "Caveau",
        "Wish list": "Lista dei desideri",
        "Reminders": "Promemoria",
        "Export": "Esporta",
        "Import": "Importa",
        "Budget": "Budget",
        "Debt": "Debiti",
    },
    "hi": {
        "Identify": "पहचानें",
        "Coach": "Coach",
        "My Museum": "मेरा म्यूज़ियम",
        "Clock Repair Help": "घड़ी मरम्मत सहायता",
        "Grail Radar": "Grail Radar",
        "Vault": "तिजोरी",
        "Wish list": "इच्छा सूची",
        "Reminders": "रिमाइंडर",
        "Export": "निर्यात",
        "Import": "आयात",
        "Budget": "बजट",
        "Debt": "कर्ज",
    },
}

# --- Shared translation fragments (reused across products) ---
HOWTO_LANGS = mk(
    "Cómo hacerlo: English · Español · 中文 · Deutsch · Français · Português · Italiano · हिन्दी",
    "Anleitung: English · Español · 中文 · Deutsch · Français · Português · Italiano · हिन्दी",
    "Mode d’emploi : English · Español · 中文 · Deutsch · Français · Português · Italiano · हिन्दी",
    "Como fazer: English · Español · 中文 · Deutsch · Français · Português · Italiano · हिन्दी",
    "使用教程：English · Español · 中文 · Deutsch · Français · Português · Italiano · हिन्दी",
    "Guida: English · Español · 中文 · Deutsch · Français · Português · Italiano · हिन्दी",
    "कैसे करें: English · Español · 中文 · Deutsch · Français · Português · Italiano · हिन्दी",
)

OFFICIAL_STORES_TRIAL = mk(
    "Tiendas oficiales · EE. UU. · 14 días gratis en tu teléfono, luego $9.99/mes o $74.99/año.",
    "Offizielle Stores · USA · 14 Tage gratis auf dem Handy, danach $9.99/Mo. oder $74.99/Jahr.",
    "Boutiques officielles · États-Unis · 14 jours gratuits sur votre téléphone, puis 9,99 $/mois ou 74,99 $/an.",
    "Lojas oficiais · EUA · 14 dias grátis no telemóvel, depois $9.99/mês ou $74.99/ano.",
    "官方商店 · 美国 · 手机免费试用 14 天，之后 $9.99/月或 $74.99/年。",
    "Store ufficiali · USA · 14 giorni gratis sul telefono, poi $9.99/mese o $74.99/anno.",
    "आधिकारिक स्टोर · US · 14 free days on your phone, फिर $9.99/माह या $74.99/वर्ष।",
)

UNSCRIBE_PRICING_NOTE = mk(
    "Tiendas oficiales · EE. UU. · Pro $29.99 una vez o $9.99/año.",
    "Offizielle Stores · USA · Pro einmalig $29.99 oder $9.99/Jahr.",
    "Boutiques officielles · États-Unis · Pro 29,99 $ une fois ou 9,99 $/an.",
    "Lojas oficiais · EUA · Pro $29.99 uma vez ou $9.99/ano.",
    "官方商店 · 美国 · Pro 一次性 $29.99 或 $9.99/年。",
    "Store ufficiali · USA · Pro $29.99 una tantum o $9.99/anno.",
    "आधिकारिक स्टोर · US · Pro एक बार $29.99 या $9.99/वर्ष।",
)

CANCEL_IN_STORE = mk(
    "Cancelar en la tienda",
    "In der Store-Abo-Verwaltung kündigen",
    "Annuler dans la boutique",
    "Cancelar na loja",
    "在商店中取消",
    "Annulla nello store",
    "स्टोर में रद्द करें",
)

DATA_ON_PHONE = mk(
    "Los datos permanecen en tu teléfono",
    "Daten bleiben auf Ihrem Handy",
    "Les données restent sur votre téléphone",
    "Os dados ficam no seu telemóvel",
    "数据留在您的手机上",
    "I dati restano sul telefono",
    "डेटा आपके फ़ोन पर रहता है",
)

NO_BANK_LOGIN = mk(
    "Sin inicio de sesión bancario",
    "Kein Bank-Login",
    "Pas de connexion bancaire",
    "Sem início de sessão bancário",
    "无需银行登录",
    "Nessun accesso alla banca",
    "कोई बैंक लॉगिन नहीं",
)

WATCH_HOW = mk(
    "▶ Ver cómo",
    "▶ So geht’s",
    "▶ Voir comment",
    "▶ Ver como",
    "▶ 观看教程",
    "▶ Guarda come",
    "▶ देखें कैसे",
)

ALL_CHAPTERS_ARROW = mk(
    "Todos los capítulos →",
    "Alle Kapitel →",
    "Tous les chapitres →",
    "Todos os capítulos →",
    "全部章节 →",
    "Tutti i capitoli →",
    "सभी अध्याय →",
)

TAP_PHONE = mk(
    "Toca el teléfono para recorrerlo",
    "Tippen Sie aufs Handy für die Tour",
    "Touchez le téléphone pour parcourir",
    "Toque no telemóvel para percorrer",
    "点按手机逐步浏览",
    "Tocca il telefono per scorrere",
    "टूर के लिए फ़ोन पर टैप करें",
)

# Placeholder — STRINGS filled in part 2
STRINGS: dict[str, dict] = {}
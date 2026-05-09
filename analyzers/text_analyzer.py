import re

URGENCY_KEYWORDS_ES = {
    "urgente", "inmediato", "ahora", "bloqueada", "suspendida", "ultimo aviso"
}
URGENCY_KEYWORDS_EN = {
    "urgent", "immediately", "now", "blocked", "suspended", "final notice"
}

CREDENTIAL_KEYWORDS_ES = {
    "usuario", "contrasena", "password", "pin", "codigo", "token"
}
CREDENTIAL_KEYWORDS_EN = {
    "username", "password", "pin", "code", "token", "credentials"
}

FINANCIAL_KEYWORDS_ES = {
    "tarjeta", "cvv", "cuenta bancaria", "transferencia", "pago", "factura"
}
FINANCIAL_KEYWORDS_EN = {
    "card", "cvv", "bank account", "transfer", "payment", "invoice"
}

BRAND_KEYWORDS_ES = {
    "banco", "soporte", "seguridad", "verificacion", "admin", "equipo"
}
BRAND_KEYWORDS_EN = {
    "bank", "support", "security", "verification", "admin", "team"
}

PRIZE_KEYWORDS_ES = {
    "premio", "ganaste", "bono", "regalo", "sorteo"
}
PRIZE_KEYWORDS_EN = {
    "prize", "winner", "bonus", "gift", "lottery"
}

URGENCY_KEYWORDS = URGENCY_KEYWORDS_ES | URGENCY_KEYWORDS_EN
CREDENTIAL_KEYWORDS = CREDENTIAL_KEYWORDS_ES | CREDENTIAL_KEYWORDS_EN
FINANCIAL_KEYWORDS = FINANCIAL_KEYWORDS_ES | FINANCIAL_KEYWORDS_EN
BRAND_KEYWORDS = BRAND_KEYWORDS_ES | BRAND_KEYWORDS_EN
PRIZE_KEYWORDS = PRIZE_KEYWORDS_ES | PRIZE_KEYWORDS_EN

URL_REGEX = re.compile(r"(https?://\S+|www\.\S+)", re.IGNORECASE)


def _add_signal(result, key, hit, weight, reason):
    signal = {
        "key": key,
        "hit": bool(hit),
        "weight": int(weight),
        "reason": reason,
    }
    result["signals"].append(signal)
    if hit:
        result["score"] += weight
        result["reasons"].append(reason)


def _normalize_text(raw_text):
    raw_text = (raw_text or "").strip()
    return raw_text


def _extract_urls(text):
    return URL_REGEX.findall(text or "")


def analyze_text(raw_text):
    result = {
        "score": 0,
        "signals": [],
        "reasons": [],
        "urls": [],
        "text_length": 0,
    }

    clean_text = _normalize_text(raw_text)
    result["text_length"] = len(clean_text)

    if not clean_text:
        _add_signal(result, "empty_text", True, 3, "Texto vacio o faltante")
        return result

    result["urls"] = _extract_urls(clean_text)

    text_lower = clean_text.lower()

    _add_signal(
        result,
        "urgency",
        any(word in text_lower for word in URGENCY_KEYWORDS),
        2,
        "Lenguaje de urgencia o amenaza"
    )

    _add_signal(
        result,
        "credential_request",
        any(word in text_lower for word in CREDENTIAL_KEYWORDS),
        3,
        "Solicitud de credenciales"
    )

    _add_signal(
        result,
        "financial_request",
        any(word in text_lower for word in FINANCIAL_KEYWORDS),
        3,
        "Solicitud de datos financieros"
    )

    _add_signal(
        result,
        "brand_impersonation",
        any(word in text_lower for word in BRAND_KEYWORDS),
        1,
        "Posible suplantacion de marca"
    )

    _add_signal(
        result,
        "prize_bait",
        any(word in text_lower for word in PRIZE_KEYWORDS),
        2,
        "Promesa de premio o beneficio"
    )

    _add_signal(
        result,
        "excessive_caps",
        sum(1 for c in clean_text if c.isalpha() and c.isupper()) >= 25,
        1,
        "Uso excesivo de mayusculas"
    )

    _add_signal(
        result,
        "too_many_links",
        len(result["urls"]) >= 3,
        2,
        "Demasiados enlaces en el texto"
    )

    _add_signal(
        result,
        "shortened_links",
        any(
            re.search(r"(bit\.ly|t\.co|tinyurl\.com|goo\.gl|ow\.ly|cutt\.ly)", u, re.IGNORECASE)
            for u in result["urls"]
        ),
        2,
        "Enlaces acortados detectados"
    )

    return result
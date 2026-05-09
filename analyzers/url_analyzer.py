import re
from urllib.parse import urlparse

import validators

SUSPICIOUS_TLDS = {
    "zip",
    "mov",
    "xyz",
    "top",
    "gq",
    "tk",
    "work",
    "click",
    "cam",
    "support"
}

URL_SHORTENERS = {
    "bit.ly", "t.co", "tinyurl.com", "goo.gl", "ow.ly",
    "is.gd", "buff.ly", "cutt.ly", "rebrand.ly", "adf.ly"
}

SUSPICIOUS_KEYWORDS = {
    "login", "verify", "secure", "account", "update",
    "payment", "invoice", "reset", "bank", "confirm"
}

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

def _normalize_url(raw_url):
    raw_url = (raw_url or "").strip()
    if not raw_url:
        return ""
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', raw_url):
        raw_url = "http://" + raw_url
    return raw_url

def analyze_url(raw_url):
    result = {
        "normalized_url": "",
        "host": "",
        "score": 0,
        "signals": [],
        "reasons": []
    }
    normalized = _normalize_url(raw_url)
    result["normalized_url"] = normalized

    if not normalized:
        _add_signal(result, "empty_url", True, 3, "URL is empty")
        return result
    if not validators.url(normalized):
        _add_signal(result, "invalid_url", True, 3, "URL is not valid")
        return result
    
    parsed = urlparse(normalized)
    host = parsed.hostname or ""
    result["host"] = host
    host_lower = host.lower()
    host_core = host_lower[4:] if host_lower.startswith("www.") else host_lower
    host_parts = [part for part in host_lower.split(".") if part]
    tld = host_parts[-1] if host_parts else ""

    path_query = (parsed.path or "")
    if parsed.query:
        path_query += "?" + parsed.query
    path_query_lower = path_query.lower()

    _add_signal(
        result,
        "has_ip",
        bool(re.match(r"^\d{1,3}(\.\d{1,3}){3}$", host)),
        3,
        "El host es una IP"
    )

    _add_signal(
        result,
        "long_url",
        len(normalized) >= 100,
        2,
        "URL demasiado larga"
    )

    _add_signal(
        result,
        "many_subdomains",
        len(host_parts) >= 4,
        2,
        "Demasiados subdominios"
    )

    _add_signal(
        result,
        "suspicious_tld",
        tld in SUSPICIOUS_TLDS,
        2,
        "TLD sospechoso"
    )

    _add_signal(
        result,
        "has_at_symbol",
        "@" in normalized,
        2,
        "La URL contiene @"
    )

    _add_signal(
        result,
        "many_hyphens",
        host_lower.count("-") >= 3,
        1,
        "Muchos guiones en el dominio"
    )

    _add_signal(
        result,
        "non_standard_port",
        bool(parsed.port) and parsed.port not in (80, 443),
        2,
        "Puerto no estandar"
    )

    _add_signal(
        result,
        "shortener",
        host_core in URL_SHORTENERS,
        3,
        "URL acortada"
    )

    _add_signal(
        result,
        "no_https",
        parsed.scheme != "https",
        1,
        "No usa HTTPS"
    )

    _add_signal(
        result,
        "suspicious_keywords",
        any(word in path_query_lower for word in SUSPICIOUS_KEYWORDS),
        2,
        "Palabras sospechosas en la URL"
    )

    _add_signal(
        result,
        "punycode",
        "xn--" in host_lower,
        3,
        "Dominio con punycode"
    )

    return result
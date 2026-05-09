def _dedupe(items):
    seen = set()
    output = []
    for item in items:
        if item not in seen:
            output.append(item)
            seen.add(item)
    return output


def generate_report(url_result, text_result, risk_result):
    url_block = None
    text_block = None

    if url_result:
        url_block = {
            "normalized_url": url_result.get("normalized_url", ""),
            "host": url_result.get("host", ""),
            "score": url_result.get("score", 0),
            "signals": url_result.get("signals", []),
        }

    if text_result:
        text_block = {
            "score": text_result.get("score", 0),
            "signals": text_result.get("signals", []),
            "urls": text_result.get("urls", []),
            "text_length": text_result.get("text_length", 0),
        }

    report = {
        "risk_level": risk_result.get("risk_level", "bajo"),
        "total_score": risk_result.get("total_score", 0),
        "reasons": _dedupe(risk_result.get("reasons", [])),
        "url": url_block,
        "text": text_block,
    }

    return report
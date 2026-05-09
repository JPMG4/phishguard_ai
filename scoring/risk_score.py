def calculate_risk(score):
    if score >= 8:
        return "alto"
    if score >= 4:
        return "medio"
    return "bajo"


def combine_scores(url_result, text_result):
    total_score = 0
    reasons = []

    if url_result:
        total_score += url_result.get("score", 0)
        reasons.extend(url_result.get("reasons", []))

    if text_result:
        total_score += text_result.get("score", 0)
        reasons.extend(text_result.get("reasons", []))

    risk_level = calculate_risk(total_score)

    return {
        "total_score": total_score,
        "risk_level": risk_level,
        "reasons": reasons,
    }
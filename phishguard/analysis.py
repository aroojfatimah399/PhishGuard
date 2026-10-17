"""Combine ML probability and rule-based indicators into one explainable result."""
from __future__ import annotations

from datetime import datetime

from .indicators import analyze_text, risk_level, rule_score
from .modeling import predict_proba, top_terms

ML_WEIGHT, RULE_WEIGHT = 0.75, 0.25


def analyze_email(subject: str, body: str, bundle: dict, model_name: str | None = None) -> dict:
    model_name = model_name or bundle["best"]
    pipe = bundle["models"][model_name]
    text = f"{subject}\n{body}".strip()
    indicators = analyze_text(text)
    p = predict_proba(pipe, text) if text else 0.0
    rs = rule_score(indicators)
    risk = ML_WEIGHT * p + RULE_WEIGHT * rs
    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "model": model_name, "subject": subject, "text": text,
        "ml_probability": round(p, 4), "rule_score": round(rs, 4),
        "risk_score": round(risk, 4), "risk_level": risk_level(risk),
        "verdict": "Likely phishing" if p >= 0.5 else "Likely legitimate",
        "indicators": [i.to_dict() for i in indicators],
        "_indicator_objs": indicators,
        "top_terms": top_terms(pipe, text) if text else [],
    }

"""PDF / JSON export of a single analysis."""
from __future__ import annotations

import json
import re

from fpdf import FPDF


def _clean(s: str) -> str:
    """Make text safe for core PDF fonts: latin-1, defanged URLs, breakable long tokens."""
    s = re.sub(r"https?://", lambda m: m.group(0).replace("http", "hxxp"), str(s), flags=re.I)
    s = s.encode("latin-1", "replace").decode("latin-1")
    return re.sub(r"(\S{50})", r"\1 ", s)


def build_pdf(result: dict) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    def line(text, size=10, style="", h=6):
        pdf.set_font("Helvetica", style, size)
        pdf.multi_cell(0, h, _clean(text), new_x="LMARGIN", new_y="NEXT")

    line("PhishGuard - Email Analysis Report", 16, "B", 10)
    line(f"Generated: {result['timestamp']}   |   Model: {result['model']}", 9)
    pdf.ln(3)
    line(f"Verdict: {result['verdict']}", 13, "B", 8)
    line(f"Risk level: {result['risk_level']}   (risk score {result['risk_score']:.0%})", 11, "B")
    line(f"ML phishing probability: {result['ml_probability']:.1%}   |   "
         f"Rule-based score: {result['rule_score']:.0%}")
    line("Risk score = 0.75 x ML probability + 0.25 x rule score.", 8)
    pdf.ln(3)
    line("Subject", 11, "B"); line(result["subject"] or "(none)")
    pdf.ln(2)
    line("Suspicious indicators", 11, "B")
    if not result["indicators"]:
        line("None detected by the rules.")
    for ind in result["indicators"]:
        line(f"- {ind['title']} (severity {ind['severity']}/3)", 10, "B")
        line("  " + ind["explanation"], 9)
        for ev in ind["evidence"][:3]:
            line(f'    evidence: "{ev}"', 9)
    pdf.ln(2)
    line("Terms that pushed the model toward 'phishing'", 11, "B")
    line(", ".join(t for t, _ in result["top_terms"]) or "None")
    pdf.ln(2)
    line("Email excerpt (links defanged)", 11, "B")
    line(result["text"][:1500], 9)
    pdf.ln(3)
    line("Automated analysis for educational use - not a substitute for professional judgement.", 8, "I")
    return bytes(pdf.output())


def build_json(result: dict) -> str:
    data = {k: v for k, v in result.items() if not k.startswith("_")}
    return json.dumps(data, indent=2)

"""Explainable, rule-based phishing indicators.

The ML model gives a probability; these rules explain *why* an email looks
suspicious (urgency, credential requests, threats, bad links ...) and give
character spans so the dashboard can highlight the evidence.
"""
from __future__ import annotations

import html
import re
from dataclasses import dataclass, field, asdict
from urllib.parse import urlparse

URL_RE = re.compile(r"(?:https?://|www\.)[^\s<>\"')\]]+", re.I)

# (key, title, severity 1-3, explanation, regex)
RULES = [
    ("urgency", "Urgent / pressure language", 2,
     "Phishing emails rush you so you act before thinking.",
     r"\b(?:urgent(?:ly)?|immediately|right away|act now|as soon as possible|asap|"
     r"within \d+ (?:hours?|days?|minutes?)|final (?:notice|warning)|last chance|"
     r"expires? (?:today|soon|in)|limited time|don'?t delay|time[- ]sensitive)\b"),
    ("credentials", "Request for credentials or sensitive data", 3,
     "Legitimate organisations do not ask you to send passwords, PINs or card data by email.",
     r"\b(?:verify|confirm|update|validate|re-?enter|provide|enter|submit)\b[^.\n]{0,40}"
     r"\b(?:password|passcode|pin|login|credentials?|account (?:details|information)|"
     r"card (?:number|details)|credit card|bank (?:details|account)|security code|"
     r"cvv|otp|one[- ]time (?:code|password))\b|\b(?:cvv|social security number|ssn)\b"),
    ("threat", "Threat of suspension or loss", 3,
     "Threats of account closure are a classic pressure tactic.",
     r"\b(?:account|access|service|card)\b[^.\n]{0,40}\b(?:suspend(?:ed)?|suspension|locked|"
     r"disabled|terminated|closed|deactivated|restricted|blocked)\b|"
     r"\b(?:will be|has been|have been) (?:suspended|locked|disabled|terminated|closed|"
     r"deactivated|restricted|blocked)\b|\blegal action\b|\bpermanently (?:closed|deleted|disabled)\b"),
    ("lure", "Prize, refund or money lure", 2,
     "Unexpected rewards or refunds are used as bait.",
     r"(?:\b(?:you(?:'ve| have)? (?:won|been selected)|winner|prize|lottery|claim your|"
     r"refund|reward|free (?:gift|iphone)|inheritance)\b|\$\s?\d[\d,]{3,})"),
    ("secrecy", "Unusual payment or secrecy request", 3,
     "Gift cards, wire transfers, crypto and secrecy requests are typical of fraud/BEC.",
     r"\b(?:wire transfer|gift cards?|western union|bitcoin|crypto(?:currency)?|"
     r"keep this (?:confidential|secret)|do not (?:tell|share|discuss)|i need a favou?r)\b"),
    ("greeting", "Generic greeting", 1,
     "Mass phishing rarely uses your real name.",
     r"^\s*(?:dear (?:customer|user|member|client|account holder|valued customer|sir|madam|"
     r"sir/madam|friend|winner)|hello (?:customer|user)|attention:?)"),
    ("click", "Pushy call to click or log in", 1,
     "Emails that push you straight to a login page deserve caution.",
     r"\b(?:click (?:here|the link|below)|log ?in (?:here|now|below)|sign ?in (?:here|now|below)|"
     r"follow (?:this|the) link)\b"),
    ("attachment", "Attachment / file download prompt", 1,
     "Unexpected attachments can carry malware or fake login forms.",
     r"\b(?:open|view|download|enable (?:macros|content))\b[^.\n]{0,30}"
     r"\b(?:attached|attachment|\.zip|\.exe|\.docm?x?|\.html?)\b"),
]
_COMPILED = [(k, t, s, e, re.compile(rx, re.I | re.M)) for k, t, s, e, rx in RULES]

SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "buff.ly",
              "rebrand.ly", "cutt.ly", "shorturl.at"}
SUSPICIOUS_TLDS = {"zip", "top", "xyz", "click", "tk", "ml", "ga", "cf", "gq", "work",
                   "support", "icu", "buzz", "country", "loan"}
BRANDS = {"paypal": "paypal.com", "microsoft": "microsoft.com", "apple": "apple.com",
          "amazon": "amazon.com", "google": "google.com", "netflix": "netflix.com",
          "dhl": "dhl.com", "fedex": "fedex.com", "facebook": "facebook.com",
          "instagram": "instagram.com", "linkedin": "linkedin.com", "dropbox": "dropbox.com"}


@dataclass
class Indicator:
    key: str
    title: str
    severity: int
    explanation: str
    evidence: list = field(default_factory=list)
    spans: list = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


def url_reasons(url: str) -> list[str]:
    """Return a list of human-readable reasons a URL looks suspicious."""
    url = url.rstrip(".,;:!?")
    reasons = []
    parsed = urlparse(url if "//" in url else "http://" + url)
    host = (parsed.hostname or "").lower()
    if not host:
        return reasons
    if re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", host):
        reasons.append("uses a raw IP address instead of a domain name")
    if host in SHORTENERS:
        reasons.append("uses a URL shortener that hides the real destination")
    if "@" in parsed.netloc:
        reasons.append("contains '@' to disguise the real host")
    if "xn--" in host:
        reasons.append("uses punycode (possible look-alike characters)")
    if host.count(".") >= 4:
        reasons.append("has an unusually long chain of subdomains")
    if host.count("-") >= 2:
        reasons.append("has many hyphens in the domain")
    if url.lower().startswith("http://"):
        reasons.append("does not use HTTPS")
    if host.rsplit(".", 1)[-1] in SUSPICIOUS_TLDS:
        reasons.append(f"uses a high-abuse top-level domain (.{host.rsplit('.', 1)[-1]})")
    for brand, real in BRANDS.items():
        if brand in host and not (host == real or host.endswith("." + real)):
            reasons.append(f"mentions '{brand}' but is not the real {real} domain")
            break
    return reasons


def analyze_text(text: str) -> list[Indicator]:
    """Run all rules over the email text and return the indicators found."""
    found: list[Indicator] = []
    for key, title, sev, expl, rx in _COMPILED:
        matches = list(rx.finditer(text))
        if matches:
            found.append(Indicator(
                key, title, sev, expl,
                evidence=[m.group(0).strip()[:90] for m in matches[:5]],
                spans=[(m.start(), m.end()) for m in matches]))
    bad_urls, spans, notes = [], [], []
    for m in URL_RE.finditer(text):
        reasons = url_reasons(m.group(0))
        if reasons:
            bad_urls.append(m.group(0).rstrip(".,;:!?"))
            spans.append((m.start(), m.end()))
            notes.append("; ".join(reasons))
    if bad_urls:
        found.append(Indicator(
            "suspicious_link", "Suspicious link(s)", 3,
            "Link problems: " + " | ".join(dict.fromkeys(notes)),
            evidence=bad_urls[:5], spans=spans))
    return found


def rule_score(indicators: list[Indicator]) -> float:
    """0..1 score from summed severities of distinct indicators."""
    return min(1.0, sum(i.severity for i in indicators) / 10.0)


def risk_level(score: float) -> str:
    return "Low" if score < 0.35 else "Medium" if score < 0.65 else "High"


def highlight_html(text: str, indicators: list[Indicator]) -> str:
    """Return HTML of the email with evidence spans highlighted (XSS-safe)."""
    colors = {1: "#fff3a3", 2: "#ffcf8a", 3: "#ff9d9d"}
    spans = sorted(((s, e, i.severity, i.title) for i in indicators for s, e in i.spans))
    out, pos = [], 0
    for s, e, sev, title in spans:
        if s < pos:  # skip overlaps
            continue
        out.append(html.escape(text[pos:s]))
        out.append(f'<mark title="{html.escape(title)}" style="background:{colors[sev]};'
                   f'color:#000;padding:0 2px;border-radius:3px">{html.escape(text[s:e])}</mark>')
        pos = e
    out.append(html.escape(text[pos:]))
    return ('<div style="white-space:pre-wrap;font-family:monospace;font-size:0.9rem;'
            'line-height:1.5">' + "".join(out) + "</div>")

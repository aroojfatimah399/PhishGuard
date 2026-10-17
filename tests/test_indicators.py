from phishguard.indicators import analyze_text, highlight_html, risk_level, rule_score, url_reasons

PHISH = ("URGENT: your account has been suspended. Verify your password within 24 hours: "
         "http://paypal-secure-login.top/verify")
LEGIT = "Hi team, the meeting is Friday at 10:00. Notes: https://www.github.com/org/repo"


def keys(text):
    return {i.key for i in analyze_text(text)}


def test_phishing_triggers_core_indicators():
    k = keys(PHISH)
    assert {"urgency", "credentials", "threat", "suspicious_link"} <= k


def test_legit_email_has_no_indicators():
    assert analyze_text(LEGIT) == []


def test_url_reasons():
    assert any("IP" in r for r in url_reasons("http://192.168.1.5/login"))
    assert any("shortener" in r for r in url_reasons("https://bit.ly/abc"))
    assert any("paypal" in r for r in url_reasons("https://paypal.evil.xyz/login"))
    assert url_reasons("https://www.paypal.com/signin") == []


def test_score_and_levels():
    assert rule_score([]) == 0
    assert rule_score(analyze_text(PHISH)) == 1.0
    assert risk_level(0.1) == "Low" and risk_level(0.5) == "Medium" and risk_level(0.9) == "High"


def test_highlight_escapes_html():
    text = "<script>alert(1)</script> urgent http://1.2.3.4/x"
    out = highlight_html(text, analyze_text(text))
    assert "<script>" not in out and "&lt;script&gt;" in out and "<mark" in out

"""PhishGuard - Streamlit dashboard.   Run:  streamlit run app.py"""
import html
import json
import time
from datetime import datetime
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from phishguard.analysis import analyze_email
from phishguard.examples import EXAMPLES
from phishguard.indicators import highlight_html
from phishguard.modeling import LABELS, load_model, train_and_save
from phishguard.reporting import build_json, build_pdf

ROOT = Path(__file__).parent
MODEL_DIR = ROOT / "models"
GREEN, AMBER, RED = "#3dffa0", "#ffb020", "#ff4d5e"
LEVEL_COLOR = {"Low": GREEN, "Medium": AMBER, "High": RED}
SEV_COLOR = {1: "#ffe08a", 2: AMBER, 3: RED}

st.set_page_config(page_title="PhishGuard", page_icon="🛡️", layout="wide")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=JetBrains+Mono:wght@400;600&display=swap');
.block-container{padding-top:1.4rem;max-width:1200px}
#MainMenu,footer{visibility:hidden}
h1,h2,h3,.hero h1,.verdict{font-family:'Space Grotesk',sans-serif!important;letter-spacing:-.02em}
.kicker,.stat b,.ev,.mh,.mb,.pill,.foot{font-family:'JetBrains Mono',monospace}
.hero{display:grid;grid-template-columns:1.2fr 1fr;gap:2rem;align-items:center;padding:2rem 2.2rem;margin-bottom:1.2rem;
 border:1px solid rgba(61,255,160,.25);border-radius:18px;
 background:radial-gradient(circle at 85% 20%,rgba(61,255,160,.10),transparent 45%),#0d151c;
 box-shadow:0 0 40px rgba(61,255,160,.07)}
.hero h1{font-size:3.2rem;font-weight:700;margin:.2rem 0;line-height:1}
.hero h1 span{color:#3dffa0}
.hero p{font-size:1.05rem;opacity:.8;margin:.6rem 0 1rem}
.kicker{color:#3dffa0;font-size:.78rem;letter-spacing:.18em}
.chip{display:inline-block;margin:0 .5rem .4rem 0;padding:.25rem .7rem;border:1px solid rgba(61,255,160,.35);border-radius:6px;font-size:.78rem;color:#3dffa0;font-family:'JetBrains Mono',monospace}
.mail{position:relative;overflow:hidden;padding:1rem 1.2rem;border-radius:12px;background:#0a0f14;border:1px solid rgba(255,255,255,.1)}
.mh{font-size:.78rem;opacity:.65;margin-bottom:.3rem}
.mb{font-size:.82rem;line-height:1.7;margin-top:.7rem}
.mail mark{background:rgba(255,77,94,.22);color:#ff8a96;border-bottom:1px solid #ff4d5e;padding:0 2px}
.scan{position:absolute;left:0;right:0;height:3px;background:linear-gradient(90deg,transparent,#3dffa0,transparent);box-shadow:0 0 18px #3dffa0;animation:scan 3.2s ease-in-out infinite}
@keyframes scan{0%{top:0}50%{top:100%}100%{top:0}}
.card{background:#111a21;border:1px solid rgba(255,255,255,.08);border-radius:14px;padding:1rem 1.2rem;margin-bottom:.8rem;transition:transform .2s,border-color .2s}
.card:hover{transform:translateY(-3px);border-color:rgba(61,255,160,.45)}
.stat{text-align:center}.stat b{display:block;font-size:1.7rem}
.stat span{opacity:.6;font-size:.72rem;text-transform:uppercase;letter-spacing:.1em}
.ind{border-left:4px solid}
.pill{display:inline-block;padding:.1rem .55rem;border-radius:4px;font-size:.72rem;font-weight:600;color:#0a0f14;margin-left:.5rem}
.ev{display:inline-block;font-size:.78rem;background:rgba(255,255,255,.07);padding:.1rem .5rem;border-radius:5px;margin:.25rem .3rem 0 0;word-break:break-all}
.verdict{font-size:1.7rem;font-weight:700;text-align:center;margin:0}
.gauge{display:block;margin:0 auto;max-width:300px}
.gauge .arc{animation:fill 1.4s ease-out forwards}
@keyframes fill{from{stroke-dashoffset:251.3}}
.step{text-align:center}.step .n{width:42px;height:42px;line-height:42px;border-radius:50%;border:2px solid #3dffa0;color:#3dffa0;font-weight:700;margin:0 auto .5rem;font-family:'JetBrains Mono',monospace}
.stTabs [data-baseweb=tab]{font-weight:600;font-size:1rem}
.stButton>button,.stDownloadButton>button{border-radius:10px;transition:all .2s}
.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-2px);border-color:#3dffa0;color:#3dffa0}
.foot{text-align:center;opacity:.45;font-size:.75rem;margin-top:2rem}
@media(max-width:800px){.hero{grid-template-columns:1fr}.hero h1{font-size:2.3rem}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


@st.cache_resource(show_spinner="Loading model (training on first run)...")
def get_bundle():
    if not (MODEL_DIR / "model.joblib").exists():
        data = ROOT / "data" / "emails.csv"
        data = data if data.exists() else ROOT / "data" / "sample_emails.csv"
        train_and_save(data, MODEL_DIR)
    return load_model(MODEL_DIR)


def get_metrics():
    p = MODEL_DIR / "metrics.json"
    return json.loads(p.read_text()) if p.exists() else None


def load_example(key):
    st.session_state["subject"], st.session_state["body"] = EXAMPLES[key]
    st.session_state.pop("result", None)


def stat(value, label):
    return f'<div class="card stat"><b>{value}</b><span>{label}</span></div>'


def gauge(score, level):
    c = LEVEL_COLOR[level]
    arc = "M20 100 A80 80 0 0 1 180 100"
    return (f'<svg class="gauge" viewBox="0 0 200 125">'
            f'<path d="{arc}" fill="none" stroke="rgba(255,255,255,.1)" stroke-width="16" stroke-linecap="round"/>'
            f'<path class="arc" d="{arc}" fill="none" stroke="{c}" stroke-width="16" stroke-linecap="round" '
            f'stroke-dasharray="251.3" style="stroke-dashoffset:{251.3 * (1 - min(score, 1)):.1f}"/>'
            f'<text x="100" y="92" text-anchor="middle" font-size="34" font-weight="800" fill="{c}">{score:.0%}</text>'
            f'<text x="100" y="114" text-anchor="middle" font-size="10" letter-spacing="2" fill="#8a9a92">RISK SCORE</text></svg>')


def indicator_card(ind):
    c = SEV_COLOR[ind["severity"]]
    label = {1: "LOW", 2: "MEDIUM", 3: "HIGH"}[ind["severity"]]
    ev = "".join(f'<span class="ev">{html.escape(e)}</span>' for e in ind["evidence"])
    return (f'<div class="card ind" style="border-left-color:{c}"><b>{html.escape(ind["title"])}</b>'
            f'<span class="pill" style="background:{c}">{label}</span>'
            f'<div style="opacity:.75;font-size:.88rem;margin-top:.3rem">{html.escape(ind["explanation"])}</div>{ev}</div>')


def cm_chart(cm, name):
    df = pd.DataFrame([{"Actual": a, "Predicted": p, "Count": cm[i][j]}
                       for i, a in enumerate(LABELS) for j, p in enumerate(LABELS)])
    base = alt.Chart(df).encode(x=alt.X("Predicted:N", sort=LABELS, axis=alt.Axis(labelAngle=0)),
                                y=alt.Y("Actual:N", sort=LABELS))
    rect = base.mark_rect(cornerRadius=8).encode(
        color=alt.Color("Count:Q", scale=alt.Scale(range=["#16222b", "#0f9f6e"]), legend=None),
        tooltip=["Actual", "Predicted", "Count"])
    text = base.mark_text(fontSize=22, fontWeight="bold").encode(text="Count:Q", color=alt.value("white"))
    return (rect + text).properties(title=name, height=240)


def metric_chart(metrics):
    rows = [{"Model": n, "Metric": k.title(), "Score": v} for n, r in metrics["models"].items()
            for k, v in r["test"].items() if k != "roc_auc"]
    df = pd.DataFrame(rows)
    lo = max(0.0, round(df["Score"].min() - 0.05, 2))
    return alt.Chart(df).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
        x=alt.X("Metric:N", axis=alt.Axis(labelAngle=0), title=None), xOffset="Model:N",
        y=alt.Y("Score:Q", scale=alt.Scale(domain=[lo, 1.0]), title=f"Score (axis starts at {lo})"),
        color=alt.Color("Model:N", scale=alt.Scale(range=[GREEN, "#7aa2ff"])),
        tooltip=["Model", "Metric", alt.Tooltip("Score:Q", format=".3f")]).properties(height=320)


bundle = get_bundle()
metrics = get_metrics()
st.session_state.setdefault("history", [])

# ---------------- hero ----------------
acc = f"{metrics['models'][metrics['best_model']]['test']['accuracy']:.1%}" if metrics else "n/a"
n_emails = f"{metrics['dataset']['n_total']:,}" if metrics else "n/a"
st.markdown(
    '<div class="hero"><div><div class="kicker">// PHISHING EMAIL DETECTION</div>'
    '<h1>Phish<span>Guard</span></h1>'
    '<p>Paste any email. Get a verdict, a risk score, and the evidence behind it.</p>'
    f'<span class="chip">TEST ACCURACY {acc}</span><span class="chip">{n_emails} EMAILS</span>'
    '<span class="chip">ML + RULES</span></div>'
    '<div class="mail"><div class="scan"></div>'
    '<div class="mh">From: security@paypa1-verify.top</div>'
    '<div class="mh">Subject: <mark>URGENT</mark> account suspended</div>'
    '<div class="mb">Dear Customer, please <mark>verify your password</mark> within <mark>24 hours</mark> '
    'or your account will be <mark>permanently closed</mark>.<br><mark>http://paypa1-verify.top/login</mark></div></div></div>',
    unsafe_allow_html=True)

# ---------------- sidebar ----------------
with st.sidebar:
    st.markdown("### 🛡️ Control panel")
    model_name = st.selectbox("Model", list(bundle["models"]), index=list(bundle["models"]).index(bundle["best"]),
                              help="Default = best cross-validated F1.")
    st.markdown("**Load a sample email**")
    for k in EXAMPLES:
        st.button(("🚨 " if k.startswith("Phishing") else "✅ ") + k.split(": ")[1].capitalize(),
                  on_click=load_example, args=(k,), width="stretch")
    st.markdown("**Legend**  \n🟡 low · 🟠 medium · 🔴 high severity")
    if metrics and "sample_emails" in metrics["dataset"]["path"]:
        st.warning("Trained on the synthetic demo dataset. Retrain on real data (see README).")

tab_an, tab_batch, tab_perf, tab_about = st.tabs(
    ["🔍 Analyze", "📂 Batch scan", "📊 Model performance", "ℹ️ How it works"])

# ---------------- analyze ----------------
with tab_an:
    c1, c2 = st.columns(2, gap="large")
    with c1:
        subject = st.text_input("Subject", key="subject", placeholder="e.g. Your account has been suspended")
        body = st.text_area("Email body", key="body", height=290,
                            placeholder="Paste the email text here (never paste real passwords)...")
        go = st.button("🔎 Scan email", type="primary", width="stretch")
    if go:
        if not (subject.strip() or body.strip()):
            st.error("Please enter a subject or body.")
        else:
            with st.status("Scanning email...", expanded=True) as stt:
                for msg in ["Extracting TF-IDF features", "Running machine-learning classifier",
                            "Checking language patterns and links", "Computing risk score"]:
                    st.write("✔ " + msg)
                    time.sleep(0.3)
                res = analyze_email(subject, body, bundle, model_name)
                stt.update(label="Scan complete", state="complete", expanded=False)
            st.session_state["result"] = res
            st.session_state["history"].append({
                "Time": datetime.now().strftime("%H:%M:%S"), "Subject": (subject or body)[:50],
                "Verdict": res["verdict"], "Risk": res["risk_score"], "Level": res["risk_level"]})
            st.toast(f"{res['verdict']} - {res['risk_level']} risk", icon="🚨" if res["risk_level"] == "High" else "✅")
    res = st.session_state.get("result")
    with c2:
        if not res:
            st.markdown('<div class="card" style="text-align:center;padding:3rem 1rem;opacity:.8">'
                        '📨<br><br>Paste an email or load a sample from the sidebar,<br>then press <b>Scan email</b>.</div>',
                        unsafe_allow_html=True)
        else:
            col = LEVEL_COLOR[res["risk_level"]]
            st.markdown(f'<div class="card">{gauge(res["risk_score"], res["risk_level"])}'
                        f'<p class="verdict" style="color:{col}">{res["verdict"]}</p>'
                        f'<p style="text-align:center;opacity:.7;margin:.2rem 0 0">{res["risk_level"]} risk · model: {res["model"]}</p></div>',
                        unsafe_allow_html=True)
            m1, m2, m3 = st.columns(3)
            m1.markdown(stat(f"{res['ml_probability']:.0%}", "ML probability"), unsafe_allow_html=True)
            m2.markdown(stat(f"{res['rule_score']:.0%}", "Rule score"), unsafe_allow_html=True)
            m3.markdown(stat(len(res["indicators"]), "Indicators"), unsafe_allow_html=True)
            d1, d2 = st.columns(2)
            d1.download_button("⬇️ PDF report", build_pdf(res), "phishguard_report.pdf", "application/pdf", width="stretch")
            d2.download_button("⬇️ JSON", build_json(res), "phishguard_report.json", "application/json", width="stretch")
    if res:
        a, b = st.columns(2, gap="large")
        with a:
            st.markdown("#### Why this verdict?")
            if not res["indicators"]:
                st.success("No rule-based warning signs found.")
            for ind in res["indicators"]:
                st.markdown(indicator_card(ind), unsafe_allow_html=True)
            if res["top_terms"]:
                st.markdown("**Words pushing the model toward phishing:** " + " ".join(f"`{t}`" for t, _ in res["top_terms"]))
        with b:
            st.markdown("#### Evidence highlighted")
            hl = highlight_html(res["text"], res["_indicator_objs"]).replace("\n", "<br>")
            st.markdown(f'<div class="card">{hl}</div>', unsafe_allow_html=True)
            st.caption("Links are shown as text and are not clickable.")
    if st.session_state["history"]:
        st.markdown("#### Session history")
        st.dataframe(pd.DataFrame(st.session_state["history"][::-1]), hide_index=True, width="stretch",
                     column_config={"Risk": st.column_config.ProgressColumn("Risk", min_value=0, max_value=1, format="percent")})

# ---------------- batch ----------------
with tab_batch:
    st.write("Upload a CSV with **subject** and **body** columns (or one **text** column). "
             "If a **label** column (1 = phishing, 0 = legitimate) exists, accuracy is computed.")
    up = st.file_uploader("CSV file", type="csv")
    if up:
        df = pd.read_csv(up)
        df.columns = [c.lower().strip() for c in df.columns]
        if "text" in df.columns and "body" not in df.columns:
            df["body"] = df["text"]
        if "body" not in df.columns:
            st.error("The CSV needs a 'body' (or 'text') column.")
        else:
            df["subject"] = df["subject"].fillna("") if "subject" in df.columns else ""
            df["body"] = df["body"].fillna("").astype(str)
            rows = []
            for s, bd in zip(df["subject"].astype(str), df["body"]):
                r = analyze_email(s, bd, bundle, model_name)
                rows.append({"verdict": r["verdict"], "ml_probability": r["ml_probability"],
                             "rule_score": r["rule_score"], "risk_score": r["risk_score"],
                             "risk_level": r["risk_level"], "indicators": len(r["indicators"])})
            out = pd.concat([df.reset_index(drop=True), pd.DataFrame(rows)], axis=1)
            k1, k2, k3 = st.columns(3)
            k1.markdown(stat(len(out), "Emails scanned"), unsafe_allow_html=True)
            k2.markdown(stat(int((out["ml_probability"] >= 0.5).sum()), "Flagged as phishing"), unsafe_allow_html=True)
            if "label" in out.columns:
                pred = (out["ml_probability"] >= 0.5).astype(int)
                k3.markdown(stat(f"{(pred == out['label'].astype(int)).mean():.1%}", "Accuracy vs labels"), unsafe_allow_html=True)
            st.bar_chart(out["risk_level"].value_counts().reindex(["Low", "Medium", "High"]).fillna(0), color=GREEN)
            st.dataframe(out.drop(columns=["body"]), width="stretch")
            st.download_button("⬇️ Download results CSV", out.to_csv(index=False), "phishguard_batch.csv", "text/csv")

# ---------------- performance ----------------
with tab_perf:
    if not metrics:
        st.info("Run `python train.py` to generate metrics.")
    else:
        d = metrics["dataset"]
        k = st.columns(4)
        for col, (v, l) in zip(k, [(f"{d['n_total']:,}", "Emails"), (f"{d['n_phishing']:,}", "Phishing"),
                                   (f"{d['n_legitimate']:,}", "Legitimate"), (f"{d['n_test']:,}", "Test set")]):
            col.markdown(stat(v, l), unsafe_allow_html=True)
        st.caption(f"`{Path(d['path']).name}` · {d['cv_folds']}-fold CV on training set · best by CV F1: "
                   f"**{metrics['best_model']}** · trained {metrics['trained_at']}")
        g1, g2 = st.columns([3, 2], gap="large")
        g1.markdown("#### Hold-out test metrics (hover for values)")
        g1.altair_chart(metric_chart(metrics), width="stretch")
        rows = [{"Model": n, **{k.replace("_", "-").title(): round(v, 4) for k, v in r["test"].items()},
                 "CV F1": f"{r['cv']['f1']['mean']:.3f} ± {r['cv']['f1']['std']:.3f}"} for n, r in metrics["models"].items()]
        g2.markdown("#### Summary table")
        g2.dataframe(pd.DataFrame(rows).set_index("Model").T, width="stretch")
        st.markdown("#### Confusion matrices")
        cc = st.columns(len(metrics["models"]))
        for col, (n, r) in zip(cc, metrics["models"].items()):
            col.altair_chart(cm_chart(r["confusion_matrix"], n), width="stretch")

# ---------------- about ----------------
with tab_about:
    steps = [("1", "Clean", "Normalise text, drop empty and duplicate emails."),
             ("2", "Vectorise", "TF-IDF turns words and word pairs into numbers."),
             ("3", "Classify", "Logistic Regression and Naive Bayes estimate phishing probability."),
             ("4", "Explain", "Rules flag urgency, credential requests, threats and bad links."),
             ("5", "Score", "Risk = 0.75 × ML probability + 0.25 × rule score.")]
    for col, (n, t, txt) in zip(st.columns(5), steps):
        col.markdown(f'<div class="card step"><div class="n">{n}</div><b>{t}</b>'
                     f'<div style="opacity:.7;font-size:.85rem;margin-top:.3rem">{txt}</div></div>', unsafe_allow_html=True)
    st.markdown("**Limitations:** text-only analysis (no headers, SPF/DKIM or attachments), English only, and accuracy "
                "depends on the training data. Use it as decision support, not as the only line of defence.")

st.markdown('<div class="foot">PHISHGUARD · scikit-learn · Streamlit · for educational use</div>', unsafe_allow_html=True)

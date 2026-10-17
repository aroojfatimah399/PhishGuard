# 🛡️ PhishGuard - Phishing Email Detection System

PhishGuard analyses the text of an email and tells you whether it is likely **legitimate or phishing**,
gives a **risk score**, and **explains why** by highlighting suspicious evidence (urgency, credential requests,
threats, prize lures, bad links). It includes a performance dashboard, batch scanning, and PDF/JSON export.

> **Live demo:**   https://phishguard-aroojfatimah.streamlit.app/  **Video demo:** _add link if not deployed_

## Features
- Paste an email subject + body and get a verdict, ML probability, rule score and combined risk level (Low/Medium/High)
- Explainable output: rule-based indicators with evidence, highlighted email text, top model terms
- Two ML models compared (TF-IDF + Logistic Regression vs. TF-IDF + Multinomial Naive Bayes)
- Leakage-safe evaluation: stratified hold-out test set + 5-fold CV (TF-IDF fitted inside each fold)
- Metrics dashboard: accuracy, precision, recall, F1, ROC-AUC, confusion matrices, model comparison chart
- Batch scanning of a CSV with downloadable results
- Export a single analysis as PDF (links defanged) or JSON
- Unit tests (`pytest`)

## Technologies
Python 3.10+ · scikit-learn · pandas · Streamlit · matplotlib/seaborn · joblib · fpdf2 · pytest · Git/GitHub

## Installation (Windows / VS Code)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```
If PowerShell blocks activation: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.
macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`.
The app opens at http://localhost:8501.

## Usage
1. **Analyze email** tab - paste text or click an example in the sidebar, then **Analyze**.
2. **Batch (CSV)** tab - upload a CSV with `subject`,`body` (optional `label`).
3. **Model performance** tab - see metrics and confusion matrices.
4. Retrain on your own data: `python prepare_dataset.py data/raw/<file>.csv` then `python train.py`.

## Project structure
```
app.py                  Streamlit dashboard
train.py                Train + evaluate, writes models/
prepare_dataset.py      Convert a raw Kaggle-style CSV to subject/body/label
phishguard/             indicators.py (rules) · modeling.py (ML) · analysis.py · reporting.py · examples.py
tools/make_sample_data.py   Synthetic demo data generator
data/                   sample_emails.csv (synthetic) + README
models/                 model.joblib, metrics.json, charts
tests/                  pytest suite
docs/                   FINAL_REPORT.md, ARCHITECTURE.md, SUBMISSION_CHECKLIST.md, DEMO_SCRIPT.md
```

## How the risk score works
`risk = 0.75 × ML probability + 0.25 × rule score`; rule score = min(1, Σ severity of distinct indicators / 10).
Levels: Low < 0.35 ≤ Medium < 0.65 ≤ High. Verdict uses ML probability ≥ 0.5.

## Deploy on Streamlit Community Cloud
1. Push this repo to GitHub (keep `models/` committed).
2. Go to https://share.streamlit.io → **New app** → pick the repo, branch `main`, file `app.py`.
3. Deploy, then paste the URL at the top of this README.

## Testing
```
python -m pytest -q
```

## Limitations
Text-only (no headers/SPF/DKIM/attachments), English-focused, and quality depends on training data.
Use as decision support, not as the only defence.

## References
- Pedregosa et al., *Scikit-learn: Machine Learning in Python*, JMLR 12, 2011
- Streamlit documentation - https://docs.streamlit.io
- Anti-Phishing Working Group (APWG) Phishing Activity Trends Reports - https://apwg.org
- Add the dataset you used (name, author, URL, licence)

# 🛡️ PhishGuard - Phishing Email Detection System

**Student:** [YOUR NAME] · **Program:** Cybersecurity

| | |
|---|---|
| 🌐 **Live demo** | https://phishguard-aroojfatimah.streamlit.app/ |
| 📄 **Report** | [Final Project Report (PDF)](docs/Project%20Final%20Report.pdf) |
| 💻 **Source code** | https://github.com/aroojfatimah399/PhishGuard |

## Project Overview
Phishing emails impersonate trusted organisations to steal passwords, card details or money. PhishGuard analyses
the text of an email and predicts whether it is **legitimate or phishing**. It gives a **risk score** and
**explains why**, listing the suspicious indicators it found and highlighting the evidence in the email.
It combines two machine-learning models trained on 17,522 real emails with rule-based detectors.

## Objectives
1. Train and compare machine-learning classifiers for phishing detection.
2. Make results explainable (indicators, highlighted evidence, influential words).
3. Evaluate rigorously with a hold-out test set and cross-validation, without data leakage.
4. Deliver a deployed, interactive dashboard and a documented, tested codebase.

## Features
- Verdict, ML probability, rule score and combined risk level (Low / Medium / High) for any pasted email
- Explainable output: indicator cards with evidence, highlighted email text, top model terms
- Two models compared: TF-IDF + Logistic Regression and TF-IDF + Multinomial Naive Bayes
- Leakage-safe evaluation: stratified hold-out test set + 5-fold cross-validation (TF-IDF fitted inside each fold)
- Metrics dashboard: accuracy, precision, recall, F1, ROC-AUC, confusion matrices, model comparison chart
- Batch scanning of a CSV with downloadable results
- PDF and JSON export of an analysis (links defanged in the PDF)
- Session history and 10 automated unit tests

## Technologies
Python 3.12 · scikit-learn · pandas · Streamlit · Altair · matplotlib / seaborn · joblib · fpdf2 · pytest · Git / GitHub · Streamlit Community Cloud

## System Workflow / Architecture
```
TRAINING (offline)
Dataset -> Clean (labels, empty, duplicates) -> Stratified 80/20 split
        -> TF-IDF + Logistic Regression | TF-IDF + Naive Bayes
        -> 5-fold CV + hold-out test -> best model by CV F1 -> saved (joblib)

ANALYSIS (live app)
Email text -> ML probability (selected model)
           -> Rule-based indicators (urgency, credentials, threats, lures, links ...)
           -> Risk score = 0.75 x ML probability + 0.25 x rule score
           -> Dashboard: gauge, indicators, highlighted evidence, PDF/JSON export
```
Rule score = min(1, sum of severities of distinct indicators / 10). Levels: Low < 0.35 ≤ Medium < 0.65 ≤ High.
The verdict uses ML probability ≥ 0.5.

## Installation
Requires Python 3.10+ and Git.
```powershell
git clone https://github.com/aroojfatimah399/PhishGuard.git
cd PhishGuard
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```
If PowerShell blocks activation: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.
macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`. The app opens at http://localhost:8501.
A trained model is included, so it runs immediately.

**Retrain on your own data**
```powershell
python prepare_dataset.py data/raw/Phishing_Email.csv
python train.py
```

## Usage
1. **Analyze** tab: paste a subject and body, or load a sample from the sidebar, then press **Scan email**.
2. **Batch scan** tab: upload a CSV with `subject`, `body` (optional `label`) columns.
3. **Model performance** tab: view metrics and confusion matrices.
4. **How it works** tab: the pipeline in five steps.

### Screenshots
| Home | Phishing result |
|---|---|
| ![Home](docs/screenshots/Screenshot 2026-10-17 144101) | ![Phishing result](docs/screenshots/02_phishing_result.png) |

| Indicators and evidence | Legitimate result |
|---|---|
| ![Indicators](docs/screenshots/03_indicators_evidence.png) | ![Legitimate](docs/screenshots/04_legit_result.png) |

| Batch scan | Model performance |
|---|---|
| ![Batch](docs/screenshots/06_batch.png) | ![Performance](docs/screenshots/07_performance.png) |

## Dataset
Public phishing email dataset from Kaggle: **[DATASET NAME]** by [AUTHOR], [KAGGLE URL] (licence: [LICENCE]).
After cleaning: **17,522 emails** (6,544 phishing / 10,978 legitimate), split into 14,017 training and 3,505 test emails.
`data/sample_emails.csv` is a small **synthetic** set used only for demos and tests. No reported result comes from it.

## Testing and Results
Evaluation: 5-fold stratified cross-validation on the training set, then one evaluation on the untouched test set.
The best model was selected by cross-validated F1, never by test score.

| Metric | Logistic Regression | Naive Bayes |
|---|---|---|
| Accuracy | 0.983 | 0.981 |
| Precision | 0.970 | 0.991 |
| Recall | 0.984 | 0.957 |
| F1-score | 0.977 | 0.974 |
| ROC-AUC | 0.997 | 0.999 |
| CV F1 (mean ± std) | 0.979 ± 0.003 | 0.970 ± 0.005 |

Logistic Regression is the default: it has the higher CV F1 and recall, so it misses fewer phishing emails.
Naive Bayes has higher precision, so it raises fewer false alarms.

**Software tests:** 10 pytest tests (rules, URL checks, scoring, HTML escaping, training, leakage-safe pipeline,
PDF/JSON export) all pass.
```
python -m pytest -q
```

## Challenges
- Converting an Excel dataset with its own label names into a clean binary CSV (1,114 empty or duplicate rows removed)
- Avoiding data leakage by keeping TF-IDF inside the cross-validated pipeline
- Handling class imbalance (about 63% legitimate) with balanced class weights and F1 / recall reporting
- Making predictions explainable by combining ML with transparent rules and evidence highlighting
- Handling malicious text safely (HTML escaping, non-clickable links, defanged URLs in PDFs)
- Matching library versions between training and deployment

## Future Improvements
Parse raw `.eml` headers (SPF/DKIM, Reply-To mismatch) · URL reputation lookups and attachment analysis ·
transformer models (BERT) · multilingual support · SHAP/LIME explanations · testing on a second independent dataset ·
user feedback for retraining · browser or email-client extension.

## Limitations
Text-only analysis (no headers, SPF/DKIM or attachments), English only, and accuracy depends on the training data.
The dataset may combine several email sources, so real-world accuracy can be lower than the figures above.
Use it as decision support, not as the only line of defence.

## Conclusion
A lightweight machine-learning approach detects phishing emails with about 98% accuracy on unseen data and,
combined with rule-based indicators and evidence highlighting, explains each decision clearly. The project is open
source, tested and deployed as a public web app.

## Project Structure
```
app.py                  Streamlit dashboard
train.py                Train + evaluate, writes models/
prepare_dataset.py      Convert a raw Kaggle-style CSV to subject/body/label
phishguard/             indicators.py (rules) · modeling.py (ML) · analysis.py · reporting.py · examples.py
tools/                  make_sample_data.py (synthetic demo data)
data/                   sample_emails.csv (synthetic) + dataset instructions
models/                 model.joblib, metrics.json, charts
tests/                  pytest suite
docs/                   Project Final Report.pdf, ARCHITECTURE.md, DEMO_SCRIPT.md, screenshots/
```

## References
1. Pedregosa et al., *Scikit-learn: Machine Learning in Python*, JMLR 12, 2011
2. Streamlit documentation - https://docs.streamlit.io
3. Anti-Phishing Working Group (APWG), Phishing Activity Trends Reports - https://apwg.org
4. [DATASET CITATION: author, title, Kaggle URL]

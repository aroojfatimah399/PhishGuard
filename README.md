# 🛡️ PhishGuard - Phishing Email Detection System

**Student:** [Arooj Fatima] · **Program:** Cybersecurity

| | |
|---|---|
| 🌐 **Live demo** | https://phishguard-aroojfatimah.streamlit.app/ |
| 📄 **Final report** | [Project Final Report (PDF)](docs/Project%20Final%20Report.pdf) |
| 💻 **Source code** | https://github.com/aroojfatimah399/PhishGuard |

## Project Overview
Phishing emails impersonate trusted organisations to steal passwords, card details or money. PhishGuard analyses
the text of an email and predicts whether it is **legitimate or phishing**. It gives a **risk score** and
**explains why**, listing the suspicious indicators it found and highlighting the evidence inside the email.
It combines two machine-learning models trained on 17,522 real emails with rule-based detectors, and is deployed
as a public web application.

## Objectives
1. Train and compare machine-learning classifiers for phishing detection.
2. Make the results explainable (indicators, highlighted evidence, influential words).
3. Evaluate rigorously with a hold-out test set and cross-validation, without data leakage.
4. Deliver a deployed, interactive dashboard and a documented, tested, version-controlled codebase.

## Features
- Verdict, ML probability, rule score and combined risk level (Low / Medium / High) for any pasted email
- Explainable output: indicator cards with evidence, highlighted email text, and the words that influenced the model
- Two models compared: TF-IDF + Logistic Regression and TF-IDF + Multinomial Naive Bayes
- Leakage-safe evaluation: stratified hold-out test set + 5-fold cross-validation (TF-IDF fitted inside each fold)
- Metrics dashboard: accuracy, precision, recall, F1, ROC-AUC, confusion matrices, model comparison chart
- Batch scanning of a CSV with downloadable results
- PDF and JSON export of an analysis (links defanged in the PDF)
- Session history, animated risk gauge and a dark "security console" interface
- 10 automated unit tests

## Technologies
Python 3.12 · scikit-learn · pandas · Streamlit · Altair · matplotlib / seaborn · joblib · fpdf2 · pytest · Git / GitHub · Streamlit Community Cloud

## System Workflow / Architecture
```
TRAINING (offline)
Dataset -> Clean (labels, empty rows, duplicates) -> Stratified 80/20 split
        -> TF-IDF + Logistic Regression | TF-IDF + Naive Bayes
        -> 5-fold CV + hold-out test -> best model by CV F1 -> saved with joblib

ANALYSIS (live app)
Email text -> ML probability (selected model)
           -> Rule-based indicators (urgency, credentials, threats, lures, links ...)
           -> Risk score = 0.75 x ML probability + 0.25 x rule score
           -> Dashboard: gauge, indicators, highlighted evidence, PDF/JSON export
```

**Risk score:** `0.75 × ML probability + 0.25 × rule score`, where the rule score is the sum of the severities of the
distinct indicators found, divided by 10 and capped at 1. Levels: Low < 0.35 ≤ Medium < 0.65 ≤ High.
The verdict (likely phishing or likely legitimate) follows the ML probability at a 0.5 threshold.

## Installation and Setup
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
On macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`.
The app opens at http://localhost:8501. A trained model is included, so it runs immediately.

**Retrain on your own data**
```powershell
python prepare_dataset.py data/raw/Phishing_Email.csv
python train.py
```
`prepare_dataset.py` converts a raw CSV (for example from Kaggle) into the `subject, body, label` format.
`train.py` trains both models, prints the metrics and saves the results to `models/`.

## Usage
1. **Analyze** tab: paste a subject and body, or load a sample email from the sidebar, then press **Scan email**.
2. **Batch scan** tab: upload a CSV with `subject` and `body` columns (and an optional `label` column).
3. **Model performance** tab: view metrics and confusion matrices.
4. **How it works** tab: the pipeline in five steps.
5. Use the sidebar to switch between the two models and download a PDF or JSON report of any analysis.

### Screenshots

**Home page (live app)**

![Home page](docs/screenshots/Screenshot%202026-10-17%20144101.png)

**Phishing email detected: High risk**

![Phishing result](docs/screenshots/Screenshot%202026-10-17%20144351.png)

**Why this verdict: indicators and highlighted evidence**

![Indicators and evidence](docs/screenshots/Screenshot%202026-10-17%20144418.png)

**Legitimate email: Low risk**

![Legitimate result](docs/screenshots/Screenshot%202026-10-17%20144559.png)

**A custom phishing email written for testing (Netflix billing scam)**

![Custom email](docs/screenshots/Screenshot%202026-10-17%20144727.png)

**Batch scan of a CSV file**

![Batch scan](docs/screenshots/Screenshot%202026-10-17%20145027.png)

**Model performance**

![Model performance](docs/screenshots/Screenshot%202026-10-17%20145102.png)

**Confusion matrices**

![Confusion matrices](docs/screenshots/Screenshot%202026-10-17%20145140.png)

**Exported PDF report**

![PDF report](docs/screenshots/Screenshot%202026-10-17%20145231.png)

**How it works**

![How it works](docs/screenshots/Screenshot%202026-10-17%20145306.png)

## Dataset
Public phishing email dataset from Kaggle: **[Phishing Email Detection]** by [Cyber Cop], [https://www.kaggle.com/datasets/subhajournal/phishingemails] .

| Class | Emails |
|---|---|
| Legitimate | 10,978 |
| Phishing | 6,544 |
| **Total (after cleaning)** | **17,522** |

The data was split with stratification into 14,017 training emails and 3,505 test emails.
`data/sample_emails.csv` is a small **synthetic** dataset used only for demos and unit tests. No reported result comes from it.

## Testing and Results
**Method:** 5-fold stratified cross-validation on the training set, then one evaluation on the untouched test set
of 3,505 emails. The best model was selected by cross-validated F1, never by test-set score.

| Metric | Logistic Regression | Naive Bayes |
|---|---|---|
| Accuracy | 0.983 | 0.981 |
| Precision | 0.970 | 0.991 |
| Recall | 0.984 | 0.957 |
| F1-score | 0.977 | 0.974 |
| ROC-AUC | 0.997 | 0.999 |
| CV F1 (mean ± std) | 0.979 ± 0.003 | 0.970 ± 0.005 |

**Confusion matrices (test set)**

| | Legitimate predicted legitimate | Legitimate flagged as phishing | Phishing missed | Phishing caught |
|---|---|---|---|---|
| Logistic Regression | 2,156 | 40 | 21 | 1,288 |
| Naive Bayes | 2,184 | 12 | 56 | 1,253 |

**Discussion:** Logistic Regression is the default model because it has the higher cross-validated F1 and recall: it
misses fewer phishing emails (21 against 56), at the cost of more false alarms (40 against 12). Naive Bayes is the
opposite, with very high precision but more missed attacks. For a security tool, a missed phishing email is usually
costlier than a false alarm, and the dashboard lets the user switch between the two models.

**Software tests:** 10 pytest tests cover the rules, URL checks, scoring, HTML escaping, dataset loading, training,
the leakage-safe pipeline structure, and PDF/JSON export. All pass.
```
python -m pytest -q
```
The deployed app was also tested manually with phishing and legitimate samples, a custom email, a batch CSV and PDF export.

## Challenges
- Converting an Excel dataset with its own label names into a clean binary CSV (1,114 empty or duplicate rows removed)
- Avoiding data leakage by keeping TF-IDF inside the cross-validated pipeline
- Handling class imbalance (about 63% legitimate emails) with balanced class weights and F1 / recall reporting
- Making predictions explainable by combining machine learning with transparent rules and evidence highlighting
- Handling malicious text safely (HTML escaping, non-clickable links, defanged URLs in PDF reports)
- Matching library versions between training and deployment
- Resolving Git and GitHub authentication and push conflicts during deployment

## Future Improvements
- Parse raw `.eml` files to use headers, SPF/DKIM/DMARC results and Reply-To mismatches
- URL reputation lookups and attachment analysis
- Transformer models such as BERT or DistilBERT
- Multilingual support
- SHAP or LIME explanations
- Testing on a second, independent dataset to measure generalisation
- User feedback to retrain the model on wrongly classified emails
- A browser or email-client extension and an API

## Limitations
Text-only analysis (no headers, SPF/DKIM or attachments), English only, and accuracy depends on the training data.
The dataset may combine several email sources, so real-world accuracy can be lower than the figures above.
Use it as decision support, not as the only line of defence.

## Conclusion
A lightweight machine-learning approach detects phishing emails with about 98% accuracy on unseen data. Combined with
rule-based indicators, evidence highlighting and a clear risk score, it explains each decision instead of just
labelling it. The project is open source, tested, documented and deployed as a public web application.

## Project Structure
```
app.py                  Streamlit dashboard
train.py                Train + evaluate, writes models/
prepare_dataset.py      Convert a raw Kaggle-style CSV to subject/body/label
phishguard/             indicators.py (rules) · modeling.py (ML) · analysis.py · reporting.py · examples.py
tools/                  make_sample_data.py (synthetic demo data generator)
data/                   sample_emails.csv (synthetic) + dataset instructions
models/                 model.joblib, metrics.json, charts
tests/                  pytest suite
docs/                   Project Final Report.pdf, ARCHITECTURE.md, DEMO_SCRIPT.md, screenshots/
.streamlit/             Dark theme configuration
```

## References
1. Pedregosa, F. et al. (2011). *Scikit-learn: Machine Learning in Python*. Journal of Machine Learning Research, 12, 2825-2830.
2. Streamlit documentation. https://docs.streamlit.io
3. Anti-Phishing Working Group (APWG). Phishing Activity Trends Reports. https://apwg.org
4. [DATASET CITATION: author, title, Kaggle URL, accessed 17 October 2026]

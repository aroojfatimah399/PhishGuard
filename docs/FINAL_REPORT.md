# PhishGuard: Phishing Email Detection System
**Student:** TODO name · **Course/Program:** Cybersecurity · **Date:** TODO · **GitHub:** TODO · **Live URL / Video:** TODO

## 1. Project Overview
Phishing is one of the most common attack vectors: attackers imitate trusted organisations to steal credentials
or money. PhishGuard is a web application that analyses an email's text and predicts whether it is legitimate or
phishing, shows a risk score, and explains the decision by highlighting suspicious indicators.

## 2. Objectives
1. Train and compare machine-learning classifiers for phishing detection.
2. Provide explainable results (indicators, highlighted evidence, influential terms).
3. Evaluate rigorously (hold-out test set, cross-validation, no data leakage).
4. Deliver an interactive dashboard with reports and a documented, tested codebase.

## 3. Features and Technologies
**Features:** single-email analysis, risk score (Low/Medium/High), rule-based indicators, evidence highlighting,
batch CSV scanning, metrics dashboard, PDF/JSON export.
**Technologies:** Python, scikit-learn (TF-IDF, Logistic Regression, Naive Bayes), pandas, Streamlit,
matplotlib/seaborn, joblib, fpdf2, pytest, Git/GitHub, Streamlit Community Cloud.

## 4. System Workflow / Architecture
Insert the diagram from `docs/ARCHITECTURE.md` (render the Mermaid block at https://mermaid.live and screenshot it).
Explain each stage: dataset → preprocessing → TF-IDF → two models → evaluation → best model saved →
rule indicators + ML probability → combined risk score → dashboard.
Risk score = 0.75 × ML probability + 0.25 × rule score (rules add explainability and catch cues such as bad URLs).

## 5. Installation and Setup
Copy the commands from README.md (venv, `pip install -r requirements.txt`, `streamlit run app.py`).
Describe how to prepare the dataset (`prepare_dataset.py`) and train (`train.py`).

## 6. Usage and Screenshots
TODO: insert screenshots with captions: (a) phishing example result, (b) highlighted email + indicators,
(c) legitimate example result, (d) batch tab, (e) model performance tab, (f) exported PDF.

## 7. Dataset
TODO: name, source URL, licence, size, class balance, cleaning steps (label normalisation, empty/duplicate removal).
Note: the bundled `sample_emails.csv` is synthetic and used only for demos/tests.

## 8. Testing and Results
**Method:** stratified 80/20 split; 5-fold CV on the training set; model chosen by CV F1; test set used once.
**Results (TODO: paste from `python train.py` on the real dataset):**

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | CV F1 |
|---|---|---|---|---|---|---|
| Logistic Regression | TODO | TODO | TODO | TODO | TODO | TODO |
| Naive Bayes | TODO | TODO | TODO | TODO | TODO | TODO |

Insert `models/confusion_*.png` and `models/model_comparison.png`. Discuss false positives vs false negatives
(for phishing, missed phishing emails - false negatives - are the costlier error).
**Software tests:** 10 pytest tests (indicators, URL checks, XSS-safe highlighting, training, leakage-safe
pipeline structure, scoring, PDF/JSON export) - all passing (`python -m pytest -q`).

## 9. Challenges
- Obtaining and cleaning a real labelled dataset (inconsistent labels, duplicates, empty rows).
- Avoiding data leakage by fitting TF-IDF inside cross-validation folds.
- Balancing explainability with accuracy (hybrid ML + rules).
- Safe rendering: HTML-escaping highlighted text and defanging links in PDF reports.
TODO: add your own real challenges.

## 10. Future Improvements
Parse raw `.eml` headers (SPF/DKIM/Reply-To mismatch), URL reputation lookups, transformer models (e.g. BERT),
multilingual support, user feedback loop for retraining, browser/Outlook plug-in, SHAP/LIME explanations.

## 11. Conclusion
TODO: summarise what was built, the measured performance on the real dataset, and what you learned.

## 12. References
1. Pedregosa, F. et al. (2011). Scikit-learn: Machine Learning in Python. JMLR 12, 2825-2830.
2. Streamlit Documentation. https://docs.streamlit.io
3. Anti-Phishing Working Group. Phishing Activity Trends Reports. https://apwg.org
4. TODO: your dataset citation.

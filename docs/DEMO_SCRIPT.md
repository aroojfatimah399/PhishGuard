# 3-4 minute demo video script (backup if deployment fails)
Record with Win+G (Xbox Game Bar) or OBS. Speak over the screen.

1. (0:00) Intro: name, project goal - detect phishing emails and explain why.
2. (0:20) Show GitHub repo and README briefly.
3. (0:40) Terminal: `streamlit run app.py`; dashboard opens.
4. (1:00) Sidebar example "Phishing: bank account suspended" → Analyze. Point out verdict, risk score, indicators, highlighted text, links.
5. (1:50) Example "Legitimate: team meeting" → Analyze. Compare low risk.
6. (2:15) Download the PDF report and open it.
7. (2:35) Batch tab: upload a small CSV, show results.
8. (2:55) Model performance tab: metrics, confusion matrices, LR vs Naive Bayes.
9. (3:25) Run `python -m pytest -q` showing tests pass. Close with limitations and future work.

"""Convert a real phishing-email CSV (e.g. from Kaggle) into PhishGuard's format.

Output columns: subject, body, label   (1 = phishing, 0 = legitimate)

Examples
  python prepare_dataset.py data/raw/Phishing_Email.csv
  python prepare_dataset.py raw.csv --text-col "Email Text" --label-col "Email Type"
  python prepare_dataset.py raw.csv --subject-col subject --text-col body --label-col label
"""
import argparse
from pathlib import Path

import pandas as pd

PHISH = {"1", "phishing", "phishing email", "spam", "phish", "malicious", "fraud", "true", "yes"}
LEGIT = {"0", "legitimate", "legit", "safe email", "ham", "safe", "benign", "not spam", "false", "no"}
TEXT_GUESS = ["email text", "body", "text", "email", "message", "content"]
LABEL_GUESS = ["email type", "label", "class", "type", "target", "category"]
SUBJECT_GUESS = ["subject", "email subject"]


def pick(cols, guesses):
    low = {c.lower().strip(): c for c in cols}
    return next((low[g] for g in guesses if g in low), None)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("input"); ap.add_argument("-o", "--output", default="data/emails.csv")
    ap.add_argument("--text-col"); ap.add_argument("--label-col"); ap.add_argument("--subject-col")
    ap.add_argument("--max-per-class", type=int, default=0, help="optional cap to balance/shrink")
    a = ap.parse_args()

    df = pd.read_excel(a.input) if a.input.lower().endswith((".xlsx", ".xls")) else pd.read_csv(a.input, encoding_errors="replace")
    text_col = a.text_col or pick(df.columns, TEXT_GUESS)
    label_col = a.label_col or pick(df.columns, LABEL_GUESS)
    subj_col = a.subject_col or pick(df.columns, SUBJECT_GUESS)
    if not text_col or not label_col:
        raise SystemExit(f"Could not detect columns. Found: {list(df.columns)}. Use --text-col/--label-col.")
    print(f"Using text={text_col!r} label={label_col!r} subject={subj_col!r}")

    def norm(v):
        s = str(v).strip().lower()
        return 1 if s in PHISH else 0 if s in LEGIT else None

    out = pd.DataFrame({"subject": df[subj_col].fillna("") if subj_col else "",
                        "body": df[text_col].fillna("").astype(str),
                        "label": df[label_col].map(norm)})
    unknown = out["label"].isna().sum()
    out = out.dropna(subset=["label"]); out["label"] = out["label"].astype(int)
    before = len(out)
    out = out[out["body"].str.strip() != ""].drop_duplicates(subset=["subject", "body"])
    if a.max_per_class:
        out = out.groupby("label", group_keys=False).apply(
            lambda g: g.sample(min(len(g), a.max_per_class), random_state=42))
    Path(a.output).parent.mkdir(parents=True, exist_ok=True)
    out.sample(frac=1, random_state=42).to_csv(a.output, index=False)
    print(f"Dropped {unknown} rows with unrecognised labels, {before - len(out)} empty/duplicate rows.")
    print(f"Saved {len(out)} emails to {a.output}\n{out['label'].value_counts().rename({1:'phishing',0:'legitimate'})}")


if __name__ == "__main__":
    main()

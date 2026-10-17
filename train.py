"""Train and evaluate PhishGuard models.

  python train.py                      # uses data/emails.csv if present, else the sample data
  python train.py --data data/emails.csv
"""
import argparse
from pathlib import Path

from phishguard.modeling import train_and_save

ROOT = Path(__file__).parent


def default_data() -> Path:
    real = ROOT / "data" / "emails.csv"
    return real if real.exists() else ROOT / "data" / "sample_emails.csv"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(default_data()))
    ap.add_argument("--out", default=str(ROOT / "models"))
    a = ap.parse_args()
    print(f"Training on {a.data} ...")
    m = train_and_save(a.data, a.out)
    d = m["dataset"]
    print(f"\nDataset: {d['n_total']} emails ({d['n_phishing']} phishing / {d['n_legitimate']} legitimate)")
    print(f"Train {d['n_train']} | Test {d['n_test']} | {d['cv_folds']}-fold CV\n")
    for name, r in m["models"].items():
        t, cv = r["test"], r["cv"]["f1"]
        print(f"{name:20s} CV-F1 {cv['mean']:.3f}±{cv['std']:.3f} | test acc {t['accuracy']:.3f} "
              f"prec {t['precision']:.3f} rec {t['recall']:.3f} F1 {t['f1']:.3f} AUC {t['roc_auc']:.3f}")
    print(f"\nBest model (by CV F1): {m['best_model']}\nSaved to {a.out}")

"""Training, evaluation and loading of the phishing classifiers.

Leakage-safe design: TF-IDF lives *inside* each scikit-learn Pipeline, so during
cross-validation it is re-fitted on each training fold only. A stratified
hold-out test set is never used for model selection.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

LABELS = ["Legitimate", "Phishing"]
SEED = 42


def load_dataset(path) -> pd.DataFrame:
    """Load CSV with columns subject, body, label (1 = phishing, 0 = legitimate)."""
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    if "label" not in df.columns:
        raise ValueError("Dataset needs a 'label' column (1 = phishing, 0 = legitimate).")
    for col in ("subject", "body"):
        df[col] = df[col].fillna("").astype(str) if col in df.columns else ""
    if (df["body"] == "").all() and "text" in df.columns:
        df["body"] = df["text"].fillna("").astype(str)
    df["label"] = df["label"].astype(int)
    df["text"] = (df["subject"] + "\n" + df["body"]).str.strip()
    df = df[df["text"] != ""].drop_duplicates(subset="text").reset_index(drop=True)
    return df[["subject", "body", "text", "label"]]


def build_pipelines() -> dict:
    tfidf = lambda: TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1, 2),
                                    min_df=2, max_df=0.95, sublinear_tf=True)
    return {
        "Logistic Regression": Pipeline([
            ("tfidf", tfidf()),
            ("clf", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=SEED))]),
        "Naive Bayes": Pipeline([
            ("tfidf", tfidf()),
            ("clf", MultinomialNB(alpha=0.1))]),
    }


def _test_metrics(y, pred, proba) -> dict:
    return {"accuracy": accuracy_score(y, pred),
            "precision": precision_score(y, pred, zero_division=0),
            "recall": recall_score(y, pred, zero_division=0),
            "f1": f1_score(y, pred, zero_division=0),
            "roc_auc": roc_auc_score(y, proba)}


def _plot_confusion(cm, name, path):
    fig, ax = plt.subplots(figsize=(4.2, 3.6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False, ax=ax,
                xticklabels=LABELS, yticklabels=LABELS)
    ax.set_xlabel("Predicted"); ax.set_ylabel("Actual"); ax.set_title(f"Confusion matrix - {name}")
    fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)


def _plot_comparison(models: dict, path):
    metrics = ["accuracy", "precision", "recall", "f1"]
    x = np.arange(len(metrics)); w = 0.8 / len(models)
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    for i, (name, res) in enumerate(models.items()):
        vals = [res["test"][m] for m in metrics]
        bars = ax.bar(x + i * w, vals, w, label=name)
        ax.bar_label(bars, fmt="%.3f", fontsize=7)
    ax.set_xticks(x + w * (len(models) - 1) / 2); ax.set_xticklabels([m.title() for m in metrics])
    ax.set_ylim(0, 1.1); ax.set_title("Hold-out test performance"); ax.legend(loc="lower right")
    fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)


def train_and_save(data_path, out_dir, test_size=0.2, seed=SEED) -> dict:
    """Train both models, evaluate with CV + hold-out test, save everything to out_dir."""
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    df = load_dataset(data_path)
    if df["label"].nunique() < 2 or df["label"].value_counts().min() < 10:
        raise ValueError("Need at least 10 emails of each class to train.")
    X_tr, X_te, y_tr, y_te = train_test_split(
        df["text"], df["label"], test_size=test_size, stratify=df["label"], random_state=seed)

    n_splits = int(min(5, y_tr.value_counts().min()))
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    scoring = ["accuracy", "precision", "recall", "f1"]

    fitted, results = {}, {}
    for name, pipe in build_pipelines().items():
        cvres = cross_validate(pipe, X_tr, y_tr, cv=cv, scoring=scoring, n_jobs=1)
        cv_summary = {m: {"mean": float(cvres[f"test_{m}"].mean()),
                          "std": float(cvres[f"test_{m}"].std())} for m in scoring}
        pipe.fit(X_tr, y_tr)
        pred, proba = pipe.predict(X_te), pipe.predict_proba(X_te)[:, 1]
        cm = confusion_matrix(y_te, pred, labels=[0, 1])
        slug = name.lower().replace(" ", "_")
        _plot_confusion(cm, name, out_dir / f"confusion_{slug}.png")
        results[name] = {"cv": cv_summary,
                         "test": {k: float(v) for k, v in _test_metrics(y_te, pred, proba).items()},
                         "confusion_matrix": cm.tolist()}
        fitted[name] = pipe

    best = max(results, key=lambda n: results[n]["cv"]["f1"]["mean"])  # chosen on CV, not test
    _plot_comparison(results, out_dir / "model_comparison.png")
    metrics = {
        "trained_at": datetime.now().isoformat(timespec="seconds"),
        "dataset": {"path": str(data_path), "n_total": int(len(df)),
                    "n_phishing": int((df.label == 1).sum()), "n_legitimate": int((df.label == 0).sum()),
                    "n_train": int(len(X_tr)), "n_test": int(len(X_te)), "cv_folds": n_splits},
        "best_model": best, "models": results}
    joblib.dump({"models": fitted, "best": best}, out_dir / "model.joblib")
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    return metrics


def load_model(model_dir) -> dict:
    return joblib.load(Path(model_dir) / "model.joblib")


def predict_proba(pipe, text: str) -> float:
    return float(pipe.predict_proba([text])[0, 1])


def top_terms(pipe, text: str, n: int = 8) -> list[tuple[str, float]]:
    """Terms in `text` pushing the model hardest toward 'phishing' (explainability)."""
    vec, clf = pipe.named_steps["tfidf"], pipe.named_steps["clf"]
    weights = clf.coef_[0] if hasattr(clf, "coef_") else clf.feature_log_prob_[1] - clf.feature_log_prob_[0]
    row = vec.transform([text])
    names = vec.get_feature_names_out()
    contrib = [(names[i], float(v * weights[i])) for i, v in zip(row.indices, row.data)]
    return sorted([c for c in contrib if c[1] > 0], key=lambda c: -c[1])[:n]

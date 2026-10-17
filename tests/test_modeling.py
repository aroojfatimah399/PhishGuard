from pathlib import Path

import pytest

from phishguard.analysis import analyze_email
from phishguard.modeling import load_dataset, load_model, train_and_save
from phishguard.reporting import build_json, build_pdf

DATA = Path(__file__).parent.parent / "data" / "sample_emails.csv"


@pytest.fixture(scope="module")
def trained(tmp_path_factory):
    out = tmp_path_factory.mktemp("models")
    metrics = train_and_save(DATA, out)
    return metrics, load_model(out)


def test_dataset_loads_clean():
    df = load_dataset(DATA)
    assert set(df.label.unique()) == {0, 1}
    assert df.text.is_unique


def test_training_outputs_metrics(trained):
    metrics, _ = trained
    assert set(metrics["models"]) == {"Logistic Regression", "Naive Bayes"}
    for r in metrics["models"].values():
        assert r["test"]["f1"] > 0.8
        assert sum(map(sum, r["confusion_matrix"])) == metrics["dataset"]["n_test"]


def test_pipeline_has_tfidf_inside(trained):
    _, bundle = trained
    for pipe in bundle["models"].values():
        assert [n for n, _ in pipe.steps] == ["tfidf", "clf"]  # fitted per CV fold -> no leakage


def test_phishing_scores_higher_than_legit(trained):
    _, bundle = trained
    p = analyze_email("URGENT: account suspended", "Verify your password at http://paypal-secure.top/x", bundle)
    l = analyze_email("Meeting notes", "Hi team, see you Friday at 10:00 in Room 204.", bundle)
    assert p["risk_score"] > l["risk_score"] and p["risk_level"] == "High" and l["risk_level"] == "Low"


def test_exports(trained):
    _, bundle = trained
    r = analyze_email("Win $50,000", "Dear winner, claim your prize at http://1.2.3.4/x " + "A" * 200, bundle)
    assert build_pdf(r).startswith(b"%PDF")
    assert '"risk_score"' in build_json(r)

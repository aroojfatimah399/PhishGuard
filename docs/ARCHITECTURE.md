# System workflow / architecture

```mermaid
flowchart TD
    A[Labelled email dataset<br/>subject, body, label] --> B[Preprocessing<br/>normalise labels, drop empty/duplicates]
    B --> C[Stratified split<br/>80% train / 20% test]
    C --> D[Pipeline: TF-IDF 1-2 grams]
    D --> E1[Logistic Regression]
    D --> E2[Multinomial Naive Bayes]
    E1 --> F[5-fold CV on train + hold-out test]
    E2 --> F
    F --> G[Best model by CV F1<br/>saved with joblib]
    H[User pastes email] --> I[Rule-based indicators<br/>urgency, credentials, threats, links]
    H --> J[ML probability]
    G --> J
    I --> K[Risk score = 0.75 ML + 0.25 rules]
    J --> K
    K --> L[Streamlit dashboard<br/>verdict, highlights, PDF/JSON export]
```

**Leakage control:** TF-IDF sits inside each scikit-learn `Pipeline`, so it is refitted on training folds only
during cross-validation; the test set is used once for final reporting and never for model selection.

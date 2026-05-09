import os

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(BASE_DIR, "data", "dataset.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "phishguard_baseline.joblib")


def load_dataset(path):
    df = pd.read_csv(path)

    if "url" not in df.columns:
        df["url"] = ""
    if "text" not in df.columns:
        df["text"] = ""
    if "label" not in df.columns:
        raise ValueError("Missing required column: label")

    df["url"] = df["url"].fillna("")
    df["text"] = df["text"].fillna("")
    df["label"] = df["label"].astype(str)

    combined = (df["url"].astype(str) + " " + df["text"].astype(str)).str.strip()

    return pd.DataFrame({"text": combined, "label": df["label"]})


def train_model(df):
    x = df["text"]
    y = df["label"]

    min_count = y.value_counts().min()
    stratify = y if min_count >= 2 else None
    if stratify is None:
        print("Warning: not stratifying due to low class counts.")

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.3,
        random_state=42,
        stratify=stratify,
    )

    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=5000)),
            ("clf", LogisticRegression(max_iter=1000)),
        ]
    )

    pipeline.fit(x_train, y_train)
    y_pred = pipeline.predict(x_test)

    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy:.3f}")
    print(classification_report(y_test, y_pred, digits=3, zero_division=0))
    print("Confusion matrix:")
    print(confusion_matrix(y_test, y_pred))

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")


def main():
    df = load_dataset(DATA_PATH)
    if df.empty:
        raise ValueError("Dataset is empty")

    train_model(df)


if __name__ == "__main__":
    main()

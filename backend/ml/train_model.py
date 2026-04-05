import pandas as pd
import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

def train():
    print("Loading dataset...")
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), "dataset.csv"))

    print(f"Total examples: {len(df)}")
    print(f"Class distribution:\n{df['label'].value_counts()}")

    X = df["text"].tolist()
    y = df["label"].tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )
    print(f"\nTraining examples: {len(X_train)}")
    print(f"Test examples: {len(X_test)}")

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=5000,
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True,
            min_df=2
        )),
        ("clf", LogisticRegression(
            max_iter=1000,
            C=1.0,
            random_state=42
        ))
    ])

    print("\nTraining model...")
    pipeline.fit(X_train, y_train)

    print("\nEvaluating on test set...")
    y_pred = pipeline.predict(X_test)

    print("\n" + "="*50)
    print("CLASSIFICATION REPORT")
    print("="*50)
    print(classification_report(y_test, y_pred,
        target_names=["benign", "malicious", "suspicious"]))

    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, y_pred))

    model_path = os.path.join(os.path.dirname(__file__), "intent_model.pkl")
    joblib.dump(pipeline, model_path)
    print(f"\nModel saved to: {model_path}")

    vectorizer = pipeline.named_steps["tfidf"]
    classifier = pipeline.named_steps["clf"]
    feature_names = vectorizer.get_feature_names_out()

    print("\nTop 15 words per class:")
    for i, class_name in enumerate(classifier.classes_):
        top_indices = classifier.coef_[i].argsort()[-15:][::-1]
        top_words = [feature_names[j] for j in top_indices]
        print(f"\n{class_name.upper()}: {', '.join(top_words)}")

if __name__ == "__main__":
    train()
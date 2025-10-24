# src/run_experiment.py
import time
import argparse
import pandas as pd
from codecarbon import EmissionsTracker
from sklearn.datasets import load_iris, load_digits, load_wine, load_breast_cancer, make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
from pathlib import Path

# Utils for saving results safely
def save_experiment(row, file_path="data/emission_results.csv"):
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if file_path.exists():
        df = pd.read_csv(file_path)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])
    df.to_csv(file_path, index=False)

# Dataset loader
def get_dataset(name):
    if name == "iris":
        X, y = load_iris(return_X_y=True)
    elif name == "digits":
        X, y = load_digits(return_X_y=True)
    elif name == "wine":
        X, y = load_wine(return_X_y=True)
    elif name == "breast_cancer":
        X, y = load_breast_cancer(return_X_y=True)
    elif name == "synthetic":
        X, y = make_classification(n_samples=500, n_features=20, n_classes=3, random_state=42)
    else:
        raise ValueError(f"Unknown dataset: {name}")
    return train_test_split(X, y, test_size=0.2, random_state=42)

# Model loader
def get_model(name):
    if name == "logreg":
        return LogisticRegression(max_iter=500)
    elif name == "rf":
        return RandomForestClassifier(n_estimators=200)
    elif name == "mlp":
        return MLPClassifier(hidden_layer_sizes=(128,), max_iter=200)
    elif name == "dt":
        return DecisionTreeClassifier()
    elif name == "gb":
        return GradientBoostingClassifier()
    elif name == "svm":
        return SVC()
    elif name == "knn":
        return KNeighborsClassifier()
    elif name == "et":
        return ExtraTreesClassifier()
    else:
        raise ValueError(f"Unknown model: {name}")

# Run a single experiment
def run_experiment(model_name, dataset_name, note=""):
    print(f"Running {model_name} on {dataset_name}...")
    X_train, X_test, y_train, y_test = get_dataset(dataset_name)
    model = get_model(model_name)

    tracker = EmissionsTracker(project_name="AI-Energy-Tracker", measure_power_secs=1)
    tracker.start()
    t0 = time.time()
    model.fit(X_train, y_train)
    duration = time.time() - t0
    emissions_kg = tracker.stop()

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)

    row = {
        "timestamp": pd.Timestamp.now(),
        "model": model_name,
        "dataset": dataset_name,
        "accuracy": float(acc),
        "duration_s": float(duration),
        "emissions_kg": float(emissions_kg),
        "note": note
    }
    save_experiment(row)
    print(f"Saved: {row}")

# CLI or automatic run
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", nargs="*", default=None, help="Models to run")
    parser.add_argument("--dataset", nargs="*", default=None, help="Datasets to run")
    parser.add_argument("--note", default="", help="Optional note for hyperparameters")
    args = parser.parse_args()

    # Define all datasets and models
    all_models = ["logreg", "rf", "mlp", "dt", "gb", "svm", "knn", "et"]
    all_datasets = ["iris", "digits", "wine", "breast_cancer", "synthetic"]

    # Select datasets/models based on CLI args
    selected_models = args.model if args.model else all_models
    selected_datasets = args.dataset if args.dataset else all_datasets

    # Run all combinations safely
    for ds in selected_datasets:
        for m in selected_models:
            try:
                run_experiment(m, ds, note=args.note)
            except Exception as e:
                print(f"Failed {m} on {ds}: {e}")


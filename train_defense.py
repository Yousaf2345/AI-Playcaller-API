import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# ----------------------------------
# Load engineered defensive dataset
# ----------------------------------
df = pd.read_parquet("data/plays_def_features.parquet")

print("Dataset loaded:", df.shape)

# ----------------------------------
# Create simple engineered labels
# ----------------------------------

# ---- PRESSURE MODEL LABEL ----
df["pressure_label"] = df["pressure"]  # already created earlier (sack OR hit OR TFL)


# ---- COVERAGE LABEL ----
# Approximation using pass completion depth:
# (This is a simplified placeholder until you add richer data)

def estimate_coverage(row):
    if row["play_type"] == "run":
        return "Base"
    if row["pass_length"] == "deep":
        return "Cover 3"
    if row["pass_length"] == "short":
        return "Cover 1"
    return "Unknown"

df["coverage_label"] = df.apply(estimate_coverage, axis=1)

# Drop rows with Unknown coverage
df = df[df["coverage_label"] != "Unknown"]


# ---- FRONT LABEL ----
# Very rough approximation based on success metrics
# You will improve this later

def estimate_front(row):
    # 3-man front indicator: fewer QB hits AND fewer TFL
    if row["qb_hit"] == 0 and row["tackled_for_loss"] == 0:
        return "3-man"
    # 4-man fronts typically generate more hits/TFL
    if row["qb_hit"] == 1 or row["tackled_for_loss"] == 1:
        return "4-man"
    return "Unknown"

df["front_label"] = df.apply(estimate_front, axis=1)
df = df[df["front_label"] != "Unknown"]


print("Labels created:")
print(df[["pressure_label", "coverage_label", "front_label"]].head())

# ----------------------------------
# Define features used by ALL models
# ----------------------------------
feature_cols = [
    "down",
    "ydstogo",
    "yardline_100",
    "qtr",
    "score_differential",
    "quarter_seconds_remaining",
]

X = df[feature_cols]

# ----------------------------------------------------------
# Helper function to train + save each defensive model
# ----------------------------------------------------------

def train_and_save(target_col, model_name):
    print(f"\nTraining {model_name} model...")

    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(
        n_estimators=250,
        max_depth=12,
        min_samples_split=20,
        random_state=42
    )

    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)

    print(f"{model_name} accuracy:", round(acc, 3))

    # Make sure folder exists
    os.makedirs("models", exist_ok=True)

    # Save model
    joblib.dump(model, f"models/{model_name}.pkl")
    print(f"Saved: models/{model_name}.pkl")

    return model, acc


# ----------------------------------------------------------
# Train each defensive model
# ----------------------------------------------------------

pressure_model, pressure_acc = train_and_save("pressure_label", "def_pressure_model")

coverage_model, coverage_acc = train_and_save("coverage_label", "def_coverage_model")

front_model, front_acc = train_and_save("front_label", "def_front_model")

print("\n🎉 All defensive models trained and saved successfully!")

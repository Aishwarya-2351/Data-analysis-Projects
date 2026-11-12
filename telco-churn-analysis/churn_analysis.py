"""Telco Customer Churn: cleaning, exploration, churn model, export for Power BI.

Usage:
    python churn_analysis.py <raw_csv> <output_dir>

Outputs (in output_dir):
    churn_clean.csv       cleaned data + bands + churn probability + risk level (load this in Power BI)
    summary_stats.txt     key numbers used in the README and dashboard
    fig_*.png             quick EDA charts
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

RAW, OUT = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
log = []


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    log.append(s)


# ---------------------------------------------------------------- 1. load + clean
df = pd.read_csv(RAW)
say(f"Rows: {len(df)}, columns: {df.shape[1]}")
say("Duplicate customerIDs:", df.customerID.duplicated().sum())

# TotalCharges has blank strings for customers with tenure == 0 (brand-new accounts)
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
blank = df["TotalCharges"].isna()
say("Blank TotalCharges:", int(blank.sum()), "| their tenure values:", sorted(df.loc[blank, "tenure"].unique()))
# They have no billing history yet, so TotalCharges is genuinely 0
df.loc[blank, "TotalCharges"] = 0.0

df["SeniorCitizen"] = df["SeniorCitizen"].map({0: "No", 1: "Yes"})
df["ChurnFlag"] = (df["Churn"] == "Yes").astype(int)

# Tidy 'No internet service' / 'No phone service' into plain "No" for the add-on columns
addons = ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]
for c in addons + ["MultipleLines"]:
    df[c] = df[c].replace({"No internet service": "No", "No phone service": "No"})

# ---------------------------------------------------------------- 2. feature bands
df["TenureBand"] = pd.cut(df["tenure"], [-1, 12, 24, 48, 100],
                          labels=["0-12 months", "13-24 months", "25-48 months", "49+ months"])
df["ChargeBand"] = pd.cut(df["MonthlyCharges"], [0, 35, 70, 90, 200],
                          labels=["Under 35", "35-70", "70-90", "Over 90"])
df["AddOnCount"] = (df[addons] == "Yes").sum(axis=1)
df["AutoPay"] = df["PaymentMethod"].str.contains("automatic").map({True: "Yes", False: "No"})

# ---------------------------------------------------------------- 3. exploration
base = df.ChurnFlag.mean()
say(f"\nOverall churn rate: {base:.1%} ({df.ChurnFlag.sum()} of {len(df)})")
say(f"Monthly revenue from churned customers: {df.loc[df.ChurnFlag == 1, 'MonthlyCharges'].sum():,.0f}"
    f" of {df.MonthlyCharges.sum():,.0f} ({df.loc[df.ChurnFlag == 1, 'MonthlyCharges'].sum() / df.MonthlyCharges.sum():.1%})")
say(f"Avg tenure churned vs retained: {df.loc[df.ChurnFlag == 1, 'tenure'].mean():.1f} vs {df.loc[df.ChurnFlag == 0, 'tenure'].mean():.1f} months")
say(f"Avg monthly charge churned vs retained: {df.loc[df.ChurnFlag == 1, 'MonthlyCharges'].mean():.2f} vs {df.loc[df.ChurnFlag == 0, 'MonthlyCharges'].mean():.2f}")

for col in ["Contract", "TenureBand", "InternetService", "PaymentMethod", "TechSupport",
            "OnlineSecurity", "SeniorCitizen", "ChargeBand", "PaperlessBilling", "AutoPay", "Partner", "Dependents"]:
    t = df.groupby(col, observed=True).ChurnFlag.agg(["count", "mean"]).rename(columns={"mean": "churn_rate"})
    say(f"\nChurn by {col}:\n{t.assign(churn_rate=t.churn_rate.map('{:.1%}'.format)).to_string()}")

sns.set_theme(style="whitegrid")
fig, ax = plt.subplots(1, 3, figsize=(15, 4))
for a, col in zip(ax, ["Contract", "TenureBand", "InternetService"]):
    (df.groupby(col, observed=True).ChurnFlag.mean() * 100).plot.bar(ax=a, color="#2a6fb0")
    a.set_title(f"Churn rate (%) by {col}")
    a.set_xlabel("")
    a.tick_params(axis="x", rotation=20)
plt.tight_layout()
plt.savefig(OUT / "fig_churn_drivers.png", dpi=130)
plt.close()

# ---------------------------------------------------------------- 4. model
feat_cols = ["tenure", "MonthlyCharges", "TotalCharges", "SeniorCitizen", "Partner", "Dependents",
             "PhoneService", "MultipleLines", "InternetService", "Contract", "PaperlessBilling",
             "PaymentMethod", "AddOnCount"] + addons
X = pd.get_dummies(df[feat_cols], drop_first=True)
y = df.ChurnFlag
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, stratify=y, random_state=42)

lr = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, class_weight="balanced"))
rf = RandomForestClassifier(n_estimators=300, min_samples_leaf=5, class_weight="balanced", random_state=42, n_jobs=-1)
results = {}
for name, m in [("Logistic Regression", lr), ("Random Forest", rf)]:
    m.fit(X_tr, y_tr)
    p = m.predict_proba(X_te)[:, 1]
    results[name] = (m, roc_auc_score(y_te, p))
    say(f"\n{name}: ROC-AUC = {results[name][1]:.3f}")
    say(classification_report(y_te, (p >= 0.5).astype(int), target_names=["Retained", "Churned"]))

best_name = max(results, key=lambda k: results[k][1])
best = results[best_name][0]
say(f"Selected model: {best_name} (ROC-AUC {results[best_name][1]:.3f})")

# Feature importance / coefficients for the README
if best_name == "Random Forest":
    imp = pd.Series(best.feature_importances_, index=X.columns).sort_values(ascending=False).head(10)
else:
    imp = pd.Series(best[-1].coef_[0], index=X.columns).sort_values(key=abs, ascending=False).head(10)
say("\nTop 10 drivers:\n" + imp.round(3).to_string())

# Score every customer, then bucket into risk levels (score from a model fit on the train split only)
df["ChurnProbability"] = best.predict_proba(X)[:, 1].round(3)
df["RiskLevel"] = pd.cut(df["ChurnProbability"], [-0.01, 0.4, 0.7, 1.0], labels=["Low", "Medium", "High"])
say("\nRisk level counts:\n" + df.groupby("RiskLevel", observed=True).agg(
    customers=("ChurnFlag", "size"), actual_churn_rate=("ChurnFlag", "mean")).to_string())

# ---------------------------------------------------------------- 5. export
df.to_csv(OUT / "churn_clean.csv", index=False)
(OUT / "summary_stats.txt").write_text("\n".join(log))
say(f"\nSaved to {OUT}")

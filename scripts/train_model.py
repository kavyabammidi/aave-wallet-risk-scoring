# scripts/train_model.py

import pandas as pd
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import os

# 1. Load Data
df = pd.read_csv("data/processed_features.csv")
print(df.columns)
print(df[['wallet', 'health_factor', 'num_liquidations']].head(10))
print(df['health_factor'].isnull().sum(), "/", len(df))

print(df['health_factor'].describe())
print(df['health_factor'].value_counts().head(10))

# 2. Create Weak Labels
# 2. Create Risk Labels using Quantiles
df['health_factor'] = pd.to_numeric(df['health_factor'], errors='coerce').fillna(999)
df['num_liquidations'] = pd.to_numeric(df['num_liquidations'], errors='coerce').fillna(0)

# Compute thresholds based on distribution
hf_low = df['health_factor'].quantile(0.33)
hf_high = df['health_factor'].quantile(0.66)
liq_high = df['num_liquidations'].quantile(0.66)

def label_wallet(row):
    if row['health_factor'] < hf_low or row['num_liquidations'] > liq_high:
        return 'high'
    elif row['health_factor'] < hf_high or row['num_liquidations'] > 0:
        return 'medium'
    else:
        return 'low'

df['risk_label'] = df.apply(label_wallet, axis=1)

print("\n🧪 Risk Label Distribution:")
print(df['risk_label'].value_counts())


# 3. Encode Labels
le = LabelEncoder()
df['label_encoded'] = le.fit_transform(df['risk_label'])

# 4. Prepare Features
X = df.drop(columns=['wallet', 'risk_label', 'label_encoded'])
y = df['label_encoded']

# 5. Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, random_state=42, test_size=0.2)

# 6. Train Model
from xgboost import XGBClassifier

model = XGBClassifier(
    objective='multi:softprob',
    num_class=3,
    eval_metric='mlogloss',
    use_label_encoder=False,
    base_score=0.5,
    random_state=42
)

model.fit(X_train, y_train)

# 7. Evaluate
y_pred = model.predict(X_test)
print("🔍 Classification Report:")
print(classification_report(y_test, y_pred, target_names=le.classes_))

# 8. Risk Score (based on probability of "high" risk class)
probs = model.predict_proba(df[X.columns])
if "high" in le.classes_:
    high_risk_index = list(le.classes_).index("high")
    df['risk_score'] = (probs[:, high_risk_index] * 1000).round(2)
else:
    print("⚠️ 'high' risk class not present in data. Setting risk_score to 0.")
    df['risk_score'] = 0.0


# 9. Export to CSV
os.makedirs("data", exist_ok=True)
df[['wallet', 'risk_label', 'risk_score']].to_csv("data/wallet_risk_scores.csv", index=False)
print("✅ Risk scores saved to data/wallet_risk_scores.csv")

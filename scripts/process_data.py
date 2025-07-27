import json
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import json

with open("data/wallet_health_factors.json") as f:
    health_factor_data = json.load(f)

# Load raw transactions
with open("data/raw_transactions.json", "r") as f:
    raw_data = json.load(f)

# ✅ Load compound wallet data (contains healthFactor)
compound_path = Path("data/compound_wallet_data.json")
if compound_path.exists():
    with open(compound_path, "r") as f:
        compound_data = json.load(f)
else:
    compound_data = {}




wallet_features = []

for wallet, txns in tqdm(raw_data.items(), desc="Processing wallets"):
    features = {
        "wallet": wallet,
        "num_txns": 0,
        "num_deposits": 0,
        "num_borrows": 0,
        "num_repayments": 0,
        "num_liquidations": 0,
        "health_factor": None,
        "unique_assets": set()
    }

    # ✅ Assign health factor from compound data (if available)
    acct_data = compound_data.get(wallet)
   
    # ✅ Load wallet health factor data from wallet_health_factors.json
    health_path = Path("data/wallet_health_factors.json")
    if health_path.exists():
        with open(health_path, "r") as f:
            health_data = json.load(f)
    else:
        health_data = {}


    if not txns:
        features["unique_assets"] = 0
        wallet_features.append(features)
        continue

    for txn in txns:
        features["num_txns"] += 1

        action = (txn.get("action") or txn.get("type") or "").lower()
        asset = txn.get("underlyingAsset") or txn.get("reserve") or txn.get("asset")

        if asset:
            features["unique_assets"].add(asset.lower())

        if "deposit" in action:
            features["num_deposits"] += 1
        elif "borrow" in action:
            features["num_borrows"] += 1
        elif "repay" in action:
            features["num_repayments"] += 1
        elif "liquidation" in action:
            features["num_liquidations"] += 1

    features["unique_assets"] = len(features["unique_assets"])
    wallet_features.append(features)
features["health_factor"] = health_factor_data.get(wallet)
# Convert to DataFrame
df = pd.DataFrame(wallet_features)

# 🧪 Summary of health factor values
print("\n📊 Health Factor Summary:\n", df["health_factor"].describe())

# Risk Label Assignment ✅
def assign_risk_label(row):
    if (
        (row['health_factor'] is not None and row['health_factor'] < 1.0) or
        (row['num_liquidations'] > 0) or
        (row['num_borrows'] > 3 and row['num_repayments'] == 0)
    ):
        return "high"
    return "low"

df['risk_label'] = df.apply(assign_risk_label, axis=1)
print("\n🧪 Risk Label Distribution:\n", df['risk_label'].value_counts())


# Save processed features
Path("data").mkdir(parents=True, exist_ok=True)
df.to_csv("data/processed_features.csv", index=False)
print("\n✅ Processed data saved to data/processed_features.csv")

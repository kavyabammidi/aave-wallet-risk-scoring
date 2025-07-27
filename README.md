# 🛡️ Wallet Risk Scoring from Aave v2 Protocol

This project assigns risk scores (`low`, `medium`, `high`) to DeFi wallets based on their lending/borrowing behavior using the Aave v2 lending protocol.

---

## 📊 Project Summary

### 🔍 Data Collection Method

Wallet data was collected using the [Compound v2 subgraph](https://api.thegraph.com/subgraphs/name/graphprotocol/compound-v2) via The Graph Protocol.

A Python script (`fetch_health_factor.py`) queried the following for each wallet:

- Total supply and borrow balances
- Health factor (`supply / borrow` approximation)
- Number of liquidations (historical risk marker)

The output was saved in `wallet_balances.json`.

---

### 🧠 Feature Selection Rationale

Selected features:

- **`health_factor`**: Represents the collateral-to-borrow ratio and determines the safety of a position.
- **`num_liquidations`**: Number of past liquidation events; a high value indicates risky behavior.

These features are critical for understanding a wallet's on-chain financial health and risk exposure.

---

### 📈 Scoring Method

Wallets are labeled based on the distribution of selected features using quantile thresholds:

```python
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

### ✅ **Current Status**
Data successfully fetched and processed

Risk scoring logic implemented and applied

Output saved to wallet_scores.csv

⚠️ Note: Due to limited wallet variability in the dataset, all current scores are labeled as low risk. The implementation is valid and can scale to more complex datasets.

### HOW TO RUN 

# Step 1: Install dependencies
pip install -r requirements.txt

# Step 2: Fetch data
python scripts/fetch_health_factor.py

# Step 3: Run the scoring logic
python scripts/train_model.py

import requests
import json
import os
import csv
from tqdm import tqdm

GRAPH_API = "https://api.thegraph.com/subgraphs/name/graphprotocol/compound-v2"

def fetch_account_balances(wallet_address):
    query = {
        "query": """
        query ($id: ID!) {
          account(id: $id) {
            tokens {
              symbol
              supplyBalanceUnderlying
              borrowBalanceUnderlying
            }
          }
        }
        """,
        "variables": {
            "id": wallet_address.lower()
        }
    }

    try:
        response = requests.post(GRAPH_API, json=query)
        data = response.json()
        tokens = data.get("data", {}).get("account", {}).get("tokens", [])
        
        total_supply = sum(float(token["supplyBalanceUnderlying"]) for token in tokens)
        total_borrow = sum(float(token["borrowBalanceUnderlying"]) for token in tokens)
        return {
            "wallet": wallet_address,
            "total_supply": total_supply,
            "total_borrow": total_borrow,
            "health_ratio": round(total_supply / total_borrow, 2) if total_borrow > 0 else None
        }
    except Exception as e:
        return {
            "wallet": wallet_address,
            "error": str(e)
        }

import pandas as pd

def main():
    wallets = []
    with open("data/wallets.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            wallets.append(row["wallet"])

    results = []
    for wallet in tqdm(wallets[:100], desc="🔍 Fetching account balances"):
        result = fetch_account_balances(wallet)
        results.append(result)

    # Save raw JSON
    os.makedirs("data", exist_ok=True)
    with open("data/wallet_balances.json", "w") as f:
        json.dump(results, f, indent=2)

    print("✅ Wallet balances saved to data/wallet_balances.json")

    # Convert to CSV
    df = pd.DataFrame(results)
    df.rename(columns={"health_ratio": "health_factor"}, inplace=True)

    # Drop errored entries if any
    df = df[df["health_factor"].notna()]

    df.to_csv("data/processed_wallets.csv", index=False)
    print("✅ Processed CSV saved to data/processed_wallets.csv")

if __name__ == "__main__":
    main()

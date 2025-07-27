import requests
import pandas as pd
import json
import time
from tqdm import tqdm

GRAPH_API = "https://api.thegraph.com/subgraphs/name/graphprotocol/compound-v2"

def load_wallets(csv_path):
    df = pd.read_csv(csv_path)
    return df['wallet_id'].dropna().unique().tolist()

def query_wallet(wallet):
    query = """
    {
      account(id: "%s") {
        id
        tokens {
          symbol
          supplyBalanceUnderlying
          borrowBalanceUnderlying
          lifetimeSupplyInterestAccrued
          lifetimeBorrowInterestAccrued
        }
      }
    }
    """ % wallet.lower()

    response = requests.post(GRAPH_API, json={"query": query})
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed for {wallet} - Status Code: {response.status_code}")
        return None

def main():
    wallets = load_wallets("data/wallets.csv")
    results = {}

    for wallet in tqdm(wallets, desc="Fetching data"):
        data = query_wallet(wallet)
        if data and "data" in data and data["data"].get("account"):
            results[wallet] = data["data"]["account"]
        else:
            print(f"⚠️ No account data for wallet: {wallet}")

        time.sleep(0.5)  # Avoid rate limits

    with open("data/raw_transactions.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("✅ Data saved to data/raw_transactions.json")

if __name__ == "__main__":
    main()

import os
import requests
from dotenv import load_dotenv

# Step 1 — Load .env file
load_dotenv()

# Step 2 — Get API key from environment
api_key = os.getenv("FRED_API_KEY")

# Safety check
if not api_key:
    print("❌ FRED_API_KEY not found in .env")
    exit()

# Step 3 — API request setup
url = "https://api.stlouisfed.org/fred/series/observations"

params = {
    "series_id": "DGS10",   # 10-Year Treasury Yield
    "api_key": api_key,
    "file_type": "json"
}

try:
    # Step 4 — Call API
    response = requests.get(url, params=params, timeout=10)

    print("Status Code:", response.status_code)

    response.raise_for_status()

    data = response.json()
    observations = data.get("observations", [])

    # Step 5 — Validate response
    if not observations:
        print("⚠️ No data returned")
    else:
        print("✅ API key working")

        print("\nLast 5 data points:\n")
        for obs in observations[-5:]:
            print(f"{obs['date']} → {obs['value']}")

except Exception as e:
    print("❌ Error:", e)
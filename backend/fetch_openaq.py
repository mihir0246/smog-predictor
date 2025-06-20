import os
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("OPENAQ_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

print(f"✅ Loaded OPENAQ_API_KEY:", bool(API_KEY))
print(f"✅ Loaded MONGO_URI:", bool(MONGO_URI))

headers = {
    "x-api-key": API_KEY
}

# 🔁 Use only known Delhi locations
delhi_locations = {
    103: "Income Tax Office, Delhi - CPCB",
    50: "Punjabi Bagh, Delhi - DPCC",
    13: "Delhi Technological University, Delhi - CPCB",
    17: "R K Puram, Delhi - DPCC",
    15: "IGI Airport"
}

print("🔎 Fetching latest air quality data from selected Delhi locations...\n")

for loc_id, loc_name in delhi_locations.items():
    url = f"https://api.openaq.org/v3/locations/{loc_id}/latest"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])

        if not results:
            print(f"⚠️ No recent data for {loc_name}\n")
        else:
            print(f"✅ {loc_name} (ID: {loc_id})")
            for m in results[0].get("measurements", []):
                print(f"   - {m['parameter'].upper()}: {m['value']} {m['unit']} at {m['lastUpdated']}")
            print()
        time.sleep(1.5)  # ⏳ Pause to avoid rate-limiting
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching data for {loc_name}")
        print("🛠", str(e), "\n")

print("🏁 Done.")



import os
import requests
import pymongo
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("OPENAQ_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

print(f"✅ Loaded OPENAQ_API_KEY:", bool(API_KEY))
print(f"✅ Loaded MONGO_URI:", bool(MONGO_URI))

# MongoDB Setup
client = pymongo.MongoClient(MONGO_URI)
db = client["air_quality"]
collection = db["delhi_measurements"]
print("✅ Connected to MongoDB")

# OpenAQ Setup
headers = {"x-api-key": API_KEY}
location_ids = {
    "Income Tax Office, Delhi - CPCB": 103,
    "Punjabi Bagh, Delhi - DPCC": 50,
    "Delhi Technological University, Delhi - CPCB": 13,
    "R K Puram, Delhi - DPCC": 17,
}

print("\n🔄 Saving latest measurements for Delhi...")

for name, loc_id in location_ids.items():
    try:
        url = f"https://api.openaq.org/v3/locations/{loc_id}/latest"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if not data.get("results"):
            print(f"⚠️ No data for {name}")
            continue

        for measurement in data["results"][0].get("measurements", []):
            document = {
                "location": name,
                "parameter": measurement["parameter"],
                "value": measurement["value"],
                "unit": measurement["unit"],
                "timestamp": measurement["lastUpdated"]
            }
            # Avoid duplicates
            collection.update_one(
                {
                    "location": document["location"],
                    "parameter": document["parameter"],
                    "timestamp": document["timestamp"]
                },
                {"$set": document},
                upsert=True
            )
            print(f"✅ Saved {document['parameter']} from {name}")
    except Exception as e:
        print(f"❌ Error saving data for {name}")
        print("🛠", str(e))

print("\n🏁 Done.")

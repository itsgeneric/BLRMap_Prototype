import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

print(f"Key loaded: {GOOGLE_KEY[:10]}...{GOOGLE_KEY[-4:] if GOOGLE_KEY else 'NOT FOUND'}\n")

async def test():
    async with httpx.AsyncClient() as client:

        # Test 1: Text Search
        print("=" * 50)
        print("TEST 1: Text Search — 'coffee Bengaluru'")
        r = await client.get(
            "https://maps.googleapis.com/maps/api/place/textsearch/json",
            params={"query": "coffee Bengaluru", "key": GOOGLE_KEY}
        )
        data = r.json()
        print(f"Status: {data.get('status')}")
        print(f"Error:  {data.get('error_message', 'none')}")
        print(f"Results count: {len(data.get('results', []))}")
        if data.get("results"):
            print(f"First result: {data['results'][0]['name']}")

        # Test 2: Autocomplete
        print("\n" + "=" * 50)
        print("TEST 2: Autocomplete — 'Puma Bengaluru'")
        r2 = await client.get(
            "https://maps.googleapis.com/maps/api/place/autocomplete/json",
            params={
                "input": "Puma Bengaluru",
                "key": GOOGLE_KEY,
                "components": "country:in"
            }
        )
        data2 = r2.json()
        print(f"Status: {data2.get('status')}")
        print(f"Error:  {data2.get('error_message', 'none')}")
        print(f"Predictions count: {len(data2.get('predictions', []))}")
        if data2.get("predictions"):
            print(f"First prediction: {data2['predictions'][0]['description']}")

        # Test 3: Nearby Search (no query needed)
        print("\n" + "=" * 50)
        print("TEST 3: Nearby Search — restaurants near Indiranagar")
        r3 = await client.get(
            "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
            params={
                "location": "12.9784,77.6408",
                "radius": 1000,
                "type": "restaurant",
                "key": GOOGLE_KEY
            }
        )
        data3 = r3.json()
        print(f"Status: {data3.get('status')}")
        print(f"Error:  {data3.get('error_message', 'none')}")
        print(f"Results count: {len(data3.get('results', []))}")
        if data3.get("results"):
            print(f"First result: {data3['results'][0]['name']}")

        print("\n" + "=" * 50)
        print("FULL raw response from Test 1 (first 500 chars):")
        print(json.dumps(data, indent=2)[:500])

import asyncio
asyncio.run(test())
import requests
import time
import json

print("=== TEST 1: Homepage ===")
r = requests.get("http://127.0.0.1:8000/")
print(f"Status: {r.status_code}")

print("\n=== TEST 2: Credit Estimate ===")
r = requests.get("http://127.0.0.1:8000/api/credits/estimate?content_type=SHORT_FORM")
print(f"Status: {r.status_code}, Response: {r.json()}")
r = requests.get("http://127.0.0.1:8000/api/credits/estimate?content_type=LONG_FORM")
print(f"Status: {r.status_code}, Response: {r.json()}")

print("\n=== TEST 3: Start Research Job ===")
res = requests.post("http://127.0.0.1:8000/api/research/start", json={
    "topic": "Pakistan Cricket Team",
    "category": "Cricket",
    "content_type": "SHORT_FORM",
    "time_range": "24h"
})
data = res.json()
print(f"Status: {res.status_code}, Job: {data}")

job_id = data["id"]
print(f"\n=== TEST 4: Polling Job {job_id} ===")
for i in range(60):
    time.sleep(3)
    status_res = requests.get(f"http://127.0.0.1:8000/api/research/{job_id}/status")
    status_data = status_res.json()
    status = status_data["status"]
    elapsed = i * 3
    print(f"  [{elapsed}s] Status: {status}")
    if status == "completed":
        print("\n=== SUCCESS! ===")
        sources = status_data.get("sources", [])
        report = status_data.get("final_report", "") or ""
        script = status_data.get("final_script", "") or ""
        print(f"Sources: {len(sources)}")
        print(f"Report length: {len(report)} chars")
        print(f"Script length: {len(script)} chars")
        print(f"\nScript preview (first 500 chars):\n")
        print(script[:500])
        break
    elif status == "failed":
        print("\n=== FAILED ===")
        break
else:
    print("Timed out after 3 minutes")

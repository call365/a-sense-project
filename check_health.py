import requests
import time

url = "https://a-sense-project-zeta.vercel.app/api/health"
print(f"Checking {url}...")

for i in range(5):
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Response:", response.json())
            break
        else:
            print("Response:", response.text)
    except Exception as e:
        print(f"ERROR: {e}")
    time.sleep(2)

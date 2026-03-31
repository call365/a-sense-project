import requests
import time

url = "https://asense.nextfintechai.com/api/health"
print(f"Checking {url}...")

try:
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Response:", response.json())
    else:
        print("Response:", response.text)
except Exception as e:
    print(f"ERROR: {e}")

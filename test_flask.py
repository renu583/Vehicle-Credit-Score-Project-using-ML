import requests

url = "http://127.0.0.1:5001/"  # Change the port if necessary

try:
    response = requests.get(url)
    if response.status_code == 200:
        print("✅ Flask is running successfully on:", url)
    else:
        print(f"⚠️ Flask responded with status code {response.status_code}")
except requests.ConnectionError:
    print("❌ Could not connect to Flask. Is it running?")

import urllib.request
import time
import json

url = "http://127.0.0.1:8000/api/analyze/"
data = json.dumps({"code": "print('hello, world')", "save": False}).encode("utf-8")
headers = {"Content-Type": "application/json"}
req = urllib.request.Request(url, data=data, headers=headers, method="POST")

start = time.time()
try:
    with urllib.request.urlopen(req) as response:
        res = response.read()
        print("Success!", res[:100])
except Exception as e:
    print("Error:", e)
end = time.time()
print(f"API time: {end - start:.4f} seconds")

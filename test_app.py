from fastapi.testclient import TestClient
from server.main import app

import sys
try:
    client = TestClient(app)
    response = client.get("/")
    print("GET / -> Status:", response.status_code)
    if response.status_code != 200:
        print("Response Text:", response.text)
        
    res2 = client.get("/api/v1/latest_version")
    print("GET /api/v1/latest_version -> Status:", res2.status_code)
except Exception as e:
    print("Exception occurred:", type(e).__name__, e)

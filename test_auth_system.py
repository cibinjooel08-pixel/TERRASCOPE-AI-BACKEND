import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.database.db import db_manager

client = TestClient(app)

def test_auth():
    print("==================================================")
    print("RUNNING TERRASCOPE AI AUTHENTICATION TEST SUITE")
    print("==================================================")

    # 1. Test invalid email format on login
    res = client.post("/api/auth/login", json={"email": "random@gmail", "password": "123"})
    print(f"1. Login with invalid email 'random@gmail': status={res.status_code}, response={res.json()}")
    assert res.status_code == 400
    assert "valid email address" in res.json()["detail"].lower()

    res2 = client.post("/api/auth/login", json={"email": "abc", "password": "123"})
    print(f"2. Login with invalid email 'abc': status={res2.status_code}, response={res2.json()}")
    assert res2.status_code == 400

    # 2. Test non-existent user / wrong password
    res3 = client.post("/api/auth/login", json={"email": "nonexistent@gmail.com", "password": "123"})
    print(f"3. Login non-existent user: status={res3.status_code}, response={res3.json()}")
    assert res3.status_code == 401
    assert "invalid email or password" in res3.json()["detail"].lower()

    # 3. Test default seeded demo analyst account (cibinjool08@gmail.com / password123)
    res4 = client.post("/api/auth/login", json={"email": "cibinjool08@gmail.com", "password": "password123"})
    print(f"4. Login seeded user cibinjool08@gmail.com: status={res4.status_code}, user={res4.json().get('user')}")
    assert res4.status_code == 200
    assert res4.json()["success"] is True
    assert res4.json()["user"]["email"] == "cibinjool08@gmail.com"

    # 4. Test registering a new analyst user
    new_email = "test.analyst99@terrascope.ai"
    res5 = client.post("/api/auth/register", json={
        "email": new_email,
        "password": "securepassword123",
        "full_name": "Test Analyst 99"
    })
    print(f"5. Register new analyst user: status={res5.status_code}, user={res5.json().get('user')}")
    assert res5.status_code == 200
    assert res5.json()["user"]["email"] == new_email

    # 5. Test logging in with newly registered user credentials
    res6 = client.post("/api/auth/login", json={"email": new_email, "password": "securepassword123"})
    print(f"6. Login newly registered user: status={res6.status_code}")
    assert res6.status_code == 200

    # 6. Test login with wrong password for registered user
    res7 = client.post("/api/auth/login", json={"email": new_email, "password": "wrongpassword"})
    print(f"7. Login with wrong password for registered user: status={res7.status_code}")
    assert res7.status_code == 401

    print("==================================================")
    print("ALL AUTHENTICATION TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    test_auth()

import httpx
import sys

# Use container internal URL
BASE_URL = "http://127.0.0.1:8001"

def test_backup():
    client = httpx.Client(timeout=30.0)
    
    # 1. Login
    print("Logging in...")
    try:
        resp = client.post(f"{BASE_URL}/login/access-token", data={"username": "admin", "password": "password"})
        if resp.status_code != 200:
            print(f"Login failed: {resp.text}")
            return
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
    except Exception as e:
        print(f"Login error: {e}")
        return

    # 2. Trigger Backup
    print("Triggering backup...")
    try:
        resp = client.post(f"{BASE_URL}/api/backups", headers=headers)
        if resp.status_code != 201:
            print(f"Backup failed: {resp.text}")
            return
        data = resp.json()
        filename = data["filename"]
        print(f"Backup created: {filename}")
    except Exception as e:
        print(f"Backup trigger error: {e}")
        return

    # 3. List Backups
    print("Listing backups...")
    resp = client.get(f"{BASE_URL}/api/backups", headers=headers)
    backups = resp.json()
    found = any(b["filename"] == filename for b in backups)
    if found:
        print("Backup found in list.")
    else:
        print("Backup NOT found in list.")

    # 4. Download Backup (GET check)
    print("Verifying download...")
    download_url = f"{BASE_URL}/api/backups/{filename}"
    # Use GET with stream to avoid downloading content, just check headers/status
    try:
        with client.stream("GET", download_url, headers=headers) as response:
            if response.status_code == 200:
                print("Download link valid.")
            else:
                print(f"Download link invalid: {response.status_code}")
    except Exception as e:
        print(f"Download verification error: {e}")

if __name__ == "__main__":
    test_backup()

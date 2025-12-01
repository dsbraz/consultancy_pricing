import json
import urllib.error
import urllib.request
import urllib.parse
from datetime import date
import time

BASE_URL = "http://localhost:8080"


def make_request(method, endpoint, data=None, params=None):
    url = f"{BASE_URL}{endpoint}"
    if params:
        query_string = urllib.parse.urlencode(params)
        url = f"{url}?{query_string}"

    headers = {"Content-Type": "application/json"}

    if data:
        json_data = json.dumps(data).encode("utf-8")
    else:
        json_data = None

    req = urllib.request.Request(url, data=json_data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode("utf-8")
            return json.loads(response_data)
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
        raise


def verify_transactions():
    print("Starting Transaction Integrity Verification...")

    # 1. Create Professional for testing
    print("\n1. Creating Professional...")
    prof_data = {
        "name": "Transaction Tester",
        "role": "Tester",
        "level": "Senior",
        "hourly_cost": 150.0,
        "pid": f"TRANS{int(time.time())}",
    }
    prof = make_request("POST", "/professionals/", data=prof_data)
    prof_id = prof["id"]
    print(f"Created professional: {prof['name']} (ID: {prof_id})")

    # 2. Test Project Creation Transaction
    print("\n2. Testing Project Creation Transaction...")
    proj_data = {
        "name": "Transaction Project",
        "start_date": date.today().isoformat(),
        "duration_months": 3,
        "tax_rate": 10.0,
        "margin_rate": 20.0,
        "allocations": [{"professional_id": prof_id}],
    }
    proj = make_request("POST", "/projects/", data=proj_data)
    proj_id = proj["id"]
    print(f"Created project: {proj['name']} (ID: {proj_id})")

    # Verify allocations exist
    proj_data = make_request("GET", f"/projects/{proj_id}?include_allocations=true")
    allocations = proj_data.get("allocations", [])
    assert len(allocations) == 1, "Project should have 1 allocation"
    print("Project allocations verified.")

    # 3. Test Offer Creation Transaction
    print("\n3. Testing Offer Creation Transaction...")
    off_data = {
        "name": f"Transaction Offer {int(time.time())}",
        "items": [
            {
                "role": "Tester",
                "level": "Senior",
                "professional_id": prof_id,
                "allocation_percentage": 50,
            }
        ],
    }
    off = make_request("POST", "/offers/", data=off_data)
    off_id = off["id"]
    print(f"Created offer: {off['name']} (ID: {off_id})")

    # Verify items exist
    off_data_check = make_request("GET", f"/offers/{off_id}")
    items = off_data_check.get("items", [])
    assert len(items) == 1, "Offer should have 1 item"
    print("Offer items verified.")

    # 4. Test Project Update Transaction
    print("\n4. Testing Project Update Transaction...")
    update_data = {
        "duration_months": 4  # Changing duration triggers calendar recalculation
    }
    updated_proj = make_request("PATCH", f"/projects/{proj_id}", data=update_data)
    print(f"Updated project duration to: {updated_proj['duration_months']}")

    # Verify timeline updated (indirectly checks if transaction committed correctly)
    timeline = make_request("GET", f"/projects/{proj_id}/timeline")
    assert len(timeline) > 0, "Timeline should exist"
    print("Project update verified.")

    print("\nTransaction verification passed successfully (Happy Path)!")
    print("To verify rollback, you must manually inject a failure in the backend code.")


if __name__ == "__main__":
    try:
        verify_transactions()
    except AssertionError as e:
        print(f"Test failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

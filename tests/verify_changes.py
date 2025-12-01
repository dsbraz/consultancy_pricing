import json
import urllib.error
import urllib.request
import urllib.parse
from datetime import date

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


def test_flow():
    print("Starting verification flow...")

    # 1. Create Professional
    print("\n1. Creating Professional...")
    prof_data = {
        "name": "Test Professional",
        "role": "Developer",
        "level": "Senior",
        "hourly_cost": 100.0,
    }
    prof = make_request("POST", "/professionals/", data=prof_data)
    prof_id = prof["id"]
    print(f"Created professional: {prof['name']} (ID: {prof_id})")

    # 2. Create Project
    print("\n2. Creating Project...")
    proj_data = {
        "name": "Test Project Allocation",
        "start_date": date.today().isoformat(),
        "duration_months": 3,
        "tax_rate": 10.0,
        "margin_rate": 20.0,
        "allocations": [],
    }
    proj = make_request("POST", "/projects/", data=proj_data)
    proj_id = proj["id"]
    print(f"Created project: {proj['name']} (ID: {proj_id})")

    # 3. Add Professional Manually
    print("\n3. Adding Professional Manually...")
    # Calculate expected selling rate: 100 / (1 - 0.2) = 125.0
    alloc_data = make_request(
        "POST", f"/projects/{proj_id}/allocations/", params={"professional_id": prof_id}
    )
    alloc_id = alloc_data["allocation_id"]
    print(f"Added professional. Allocation ID: {alloc_id}")
    print(f"Selling Rate: {alloc_data['selling_hourly_rate']} (Expected: 125.0)")
    assert abs(alloc_data["selling_hourly_rate"] - 125.0) < 0.01

    # 4. Verify Allocation Table Structure
    print("\n4. Verifying Allocation Table...")
    table_data = make_request("GET", f"/projects/{proj_id}/allocation_table")

    # Check if selling_hourly_rate is in allocation object (not weekly)
    allocation = table_data["allocations"][0]
    assert "selling_hourly_rate" in allocation
    assert allocation["selling_hourly_rate"] == 125.0
    print(
        "Allocation table structure correct: selling_hourly_rate is present in allocation object"
    )

    # 5. Update Allocation (Selling Rate and Hours)
    print("\n5. Updating Allocation...")

    # Get a weekly allocation ID
    week_num = list(allocation["weekly_hours"].keys())[0]
    weekly_alloc_id = allocation["weekly_hours"][week_num]["id"]

    updates = [
        {"allocation_id": alloc_id, "selling_hourly_rate": 150.0},
        {"weekly_allocation_id": weekly_alloc_id, "hours_allocated": 20.0},
    ]

    res = make_request("PATCH", f"/projects/{proj_id}/allocations", data=updates)
    print(f"Updated {res['updated_count']} items")

    # Verify updates
    res = make_request("GET", f"/projects/{proj_id}/allocation_table")
    updated_alloc = res["allocations"][0]
    assert updated_alloc["selling_hourly_rate"] == 150.0
    assert updated_alloc["weekly_hours"][week_num]["hours_allocated"] == 20.0
    print("Updates verified successfully")

    # 6. Calculate Price
    print("\n6. Calculating Price...")
    price_data = make_request("GET", f"/projects/{proj_id}/calculate_price")

    # Cost: 20 hours * 100 = 2000
    # Selling: 20 hours * 150 = 3000
    print(f"Total Cost: {price_data['total_cost']} (Expected: 2000.0)")
    print(f"Total Selling: {price_data['total_selling']} (Expected: 3000.0)")

    assert price_data["total_cost"] == 2000.0
    assert price_data["total_selling"] == 3000.0

    # 7. Remove Professional
    print("\n7. Removing Professional...")
    make_request("DELETE", f"/projects/{proj_id}/allocations/{alloc_id}")
    print("Professional removed")

    # Verify removal
    res = make_request("GET", f"/projects/{proj_id}/allocation_table")
    assert len(res["allocations"]) == 0
    print("Removal verified")

    print("\nAll tests passed successfully!")


if __name__ == "__main__":
    try:
        test_flow()
    except AssertionError as e:
        print(f"Test failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

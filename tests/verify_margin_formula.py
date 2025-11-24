import requests
import sys

BASE_URL = "http://localhost:8000"


def verify_margin_formula():
    print("Starting margin formula verification...")

    # 1. Create a test professional
    prof_data = {
        "name": "Test Margin Prof",
        "role": "Dev",
        "level": "Mid",
        "hourly_cost": 100.0,
    }
    resp = requests.post(f"{BASE_URL}/professionals/", json=prof_data)
    if resp.status_code != 200:
        sys.exit(1)
    prof_id = resp.json()["id"]

    # 2. Create a test project
    proj_data = {
        "name": "Test Margin Project",
        "start_date": "2024-01-01",
        "duration_months": 1,
        "tax_rate": 0.0,
        "margin_rate": 0.0,
        "allocations": [],
    }
    resp = requests.post(f"{BASE_URL}/projects/", json=proj_data)
    if resp.status_code != 200:
        sys.exit(1)
    proj_id = resp.json()["id"]

    try:
        # 3. Add professional with Selling Rate = 200
        # Cost = 100, Selling = 200
        # Expected Margin % = 100 / 200 = 50%
        url = f"{BASE_URL}/projects/{proj_id}/allocations/?professional_id={prof_id}&selling_hourly_rate=200.0"
        requests.post(url)

        # 4. Set hours to 10
        resp = requests.get(f"{BASE_URL}/projects/{proj_id}/allocation_table")
        table_data = resp.json()
        alloc = table_data["allocations"][0]
        first_week_key = list(alloc["weekly_hours"].keys())[0]
        weekly_alloc_id = alloc["weekly_hours"][first_week_key]["id"]

        updates = [{"weekly_allocation_id": weekly_alloc_id, "hours_allocated": 10.0}]
        requests.put(f"{BASE_URL}/projects/{proj_id}/allocations", json=updates)

        # 5. Calculate Price
        resp = requests.get(f"{BASE_URL}/projects/{proj_id}/calculate_price")
        price_data = resp.json()

        print(f"Pricing Result: {price_data}")

        # Expected Margin % = (1 - 1000/2000) * 100 = 0.5 * 100 = 50%
        expected_margin_percent = 50.0

        if price_data["final_margin_percent"] == expected_margin_percent:
            print(f"Margin Percent is correct: {price_data['final_margin_percent']}%")
        else:
            print(
                f"Margin Percent MISMATCH! Expected {expected_margin_percent}%, got {price_data['final_margin_percent']}%"
            )
            sys.exit(1)

    finally:
        requests.delete(f"{BASE_URL}/projects/{proj_id}")

    print("Verification successful!")


if __name__ == "__main__":
    verify_margin_formula()

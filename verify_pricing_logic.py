import requests
import sys

BASE_URL = "http://localhost:8000"

def verify_pricing_logic():
    print("Starting pricing logic verification...")

    # 1. Create a test professional
    print("Creating test professional...")
    prof_data = {
        "name": "Test Pricing Prof",
        "role": "Dev",
        "level": "Sen",
        "hourly_cost": 100.0
    }
    resp = requests.post(f"{BASE_URL}/professionals/", json=prof_data)
    if resp.status_code != 200:
        print(f"Failed to create professional: {resp.text}")
        sys.exit(1)
    prof = resp.json()
    prof_id = prof["id"]
    print(f"Professional created with ID: {prof_id}")

    # 2. Create a test project with 10% tax
    print("Creating test project...")
    proj_data = {
        "name": "Test Pricing Project",
        "start_date": "2024-01-01",
        "duration_months": 1,
        "tax_rate": 10.0,
        "margin_rate": 20.0,
        "allocations": []
    }
    resp = requests.post(f"{BASE_URL}/projects/", json=proj_data)
    if resp.status_code != 200:
        print(f"Failed to create project: {resp.text}")
        sys.exit(1)
    project = resp.json()
    proj_id = project["id"]

    try:
        # 3. Add professional to project with fixed selling rate
        print("Adding professional to project...")
        # Selling rate = 200.0
        url = f"{BASE_URL}/projects/{proj_id}/allocations/?professional_id={prof_id}&selling_hourly_rate=200.0"
        resp = requests.post(url)
        if resp.status_code != 200:
            print(f"Failed to add professional: {resp.text}")
            sys.exit(1)
        alloc_resp = resp.json()
        alloc_id = alloc_resp["allocation_id"]

        # 4. Set hours for one week to 10 hours
        print("Setting hours...")
        # Need to find a weekly allocation ID
        resp = requests.get(f"{BASE_URL}/projects/{proj_id}/allocation_table")
        table_data = resp.json()
        weekly_alloc_id = None
        for alloc in table_data["allocations"]:
            if alloc["allocation_id"] == alloc_id:
                # Get first week ID
                first_week_key = list(alloc["weekly_hours"].keys())[0]
                weekly_alloc_id = alloc["weekly_hours"][first_week_key]["id"]
                break
        
        if not weekly_alloc_id:
            print("Could not find weekly allocation ID")
            sys.exit(1)

        updates = [{
            "weekly_allocation_id": weekly_alloc_id,
            "hours_allocated": 10.0
        }]
        resp = requests.put(f"{BASE_URL}/projects/{proj_id}/allocations", json=updates)
        if resp.status_code != 200:
            print(f"Failed to update hours: {resp.text}")
            sys.exit(1)

        # 5. Calculate Price
        print("Calculating price...")
        resp = requests.get(f"{BASE_URL}/projects/{proj_id}/calculate_price")
        if resp.status_code != 200:
            print(f"Failed to calculate price: {resp.text}")
            sys.exit(1)
        
        price_data = resp.json()
        print(f"Pricing Result: {price_data}")

        # Expected values:
        # Hours = 10
        # Cost Rate = 100 -> Total Cost = 1000
        # Selling Rate = 200 -> Total Selling = 2000
        # Margin = Selling - Cost = 2000 - 1000 = 1000
        # Tax Rate = 10% -> Tax = 2000 * 0.10 = 200
        # Final Price = Selling + Tax = 2000 + 200 = 2200

        expected_cost = 1000.0
        expected_selling = 2000.0
        expected_margin = 1000.0
        expected_tax = 200.0
        expected_final = 2200.0

        if price_data["total_cost"] != expected_cost:
            print(f"Mismatch! Cost: {price_data['total_cost']} != {expected_cost}")
            sys.exit(1)
        if price_data["total_selling"] != expected_selling:
            print(f"Mismatch! Selling: {price_data['total_selling']} != {expected_selling}")
            sys.exit(1)
        if price_data["total_margin"] != expected_margin:
            print(f"Mismatch! Margin: {price_data['total_margin']} != {expected_margin}")
            sys.exit(1)
        if price_data["total_tax"] != expected_tax:
            print(f"Mismatch! Tax: {price_data['total_tax']} != {expected_tax}")
            sys.exit(1)
        if price_data["final_price"] != expected_final:
            print(f"Mismatch! Final: {price_data['final_price']} != {expected_final}")
            sys.exit(1)

        print("All pricing calculations match expected values!")

    finally:
        # Cleanup
        print("Cleaning up...")
        requests.delete(f"{BASE_URL}/projects/{proj_id}")
        pass

    print("Verification successful!")

if __name__ == "__main__":
    verify_pricing_logic()

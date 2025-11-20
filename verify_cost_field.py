import requests
import sys

BASE_URL = "http://localhost:8000"

def verify_cost_field():
    print("Starting cost field verification...")

    # 1. Create a test professional
    print("Creating test professional...")
    prof_data = {
        "name": "Test Professional Cost",
        "role": "Developer",
        "level": "Senior",
        "hourly_cost": 123.45
    }
    resp = requests.post(f"{BASE_URL}/professionals/", json=prof_data)
    if resp.status_code != 200:
        print(f"Failed to create professional: {resp.text}")
        sys.exit(1)
    prof = resp.json()
    prof_id = prof["id"]
    print(f"Professional created with ID: {prof_id}, Cost: {prof['hourly_cost']}")

    # 2. Create a test project
    print("Creating test project...")
    proj_data = {
        "name": "Test Project Cost",
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
        # 3. Add professional to project
        print("Adding professional to project...")
        url = f"{BASE_URL}/projects/{proj_id}/allocations/?professional_id={prof_id}"
        resp = requests.post(url)
        if resp.status_code != 200:
            print(f"Failed to add professional: {resp.text}")
            sys.exit(1)
        
        # 4. Verify allocation table data contains hourly_cost
        print("Verifying allocation table data...")
        resp = requests.get(f"{BASE_URL}/projects/{proj_id}/allocation_table")
        if resp.status_code != 200:
            print(f"Failed to get allocation table: {resp.text}")
            sys.exit(1)
        table_data = resp.json()
        
        found = False
        for alloc in table_data["allocations"]:
            if alloc["professional"]["id"] == prof_id:
                found = True
                cost = alloc["professional"]["hourly_cost"]
                print(f"Found professional in table. Cost: {cost}")
                if cost == 123.45:
                    print("Cost matches expected value.")
                else:
                    print(f"Cost MISMATCH! Expected 123.45, got {cost}")
                    sys.exit(1)
                break
        
        if not found:
            print("Professional not found in table!")
            sys.exit(1)

    finally:
        # Cleanup
        print("Cleaning up...")
        requests.delete(f"{BASE_URL}/projects/{proj_id}")
        pass

    print("Verification successful!")

if __name__ == "__main__":
    verify_cost_field()

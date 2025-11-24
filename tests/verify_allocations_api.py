import requests
import sys

BASE_URL = "http://localhost:8000"


def test_allocations():
    print("Starting allocation verification...")

    # 1. Create a test professional
    print("Creating test professional...")
    prof_data = {
        "name": "Test Professional for Alloc",
        "role": "Developer",
        "level": "Senior",
        "hourly_cost": 100.0,
    }
    resp = requests.post(f"{BASE_URL}/professionals/", json=prof_data)
    if resp.status_code != 200:
        print(f"Failed to create professional: {resp.text}")
        sys.exit(1)
    prof = resp.json()
    prof_id = prof["id"]
    print(f"Professional created with ID: {prof_id}")

    # 2. Create a test project
    print("Creating test project...")
    proj_data = {
        "name": "Test Project for Alloc",
        "start_date": "2024-01-01",
        "duration_months": 3,
        "tax_rate": 10.0,
        "margin_rate": 20.0,
        "allocations": [],
    }
    resp = requests.post(f"{BASE_URL}/projects/", json=proj_data)
    if resp.status_code != 200:
        print(f"Failed to create project: {resp.text}")
        sys.exit(1)
    project = resp.json()
    proj_id = project["id"]
    print(f"Project created with ID: {proj_id}")

    try:
        # 3. Add professional to project
        print("Adding professional to project...")

        url = f"{BASE_URL}/projects/{proj_id}/allocations/?professional_id={prof_id}"
        resp = requests.post(url)
        if resp.status_code != 200:
            print(f"Failed to add professional: {resp.text}")
            sys.exit(1)
        alloc_resp = resp.json()
        alloc_id = alloc_resp["allocation_id"]
        print(f"Professional added. Allocation ID: {alloc_id}")

        # 4. Verify allocation exists in table
        print("Verifying allocation in table...")
        resp = requests.get(f"{BASE_URL}/projects/{proj_id}/allocation_table")
        if resp.status_code != 200:
            print(f"Failed to get allocation table: {resp.text}")
            sys.exit(1)
        table_data = resp.json()

        found = False
        for alloc in table_data["allocations"]:
            if alloc["allocation_id"] == alloc_id:
                found = True
                print("Allocation found in table.")
                break

        if not found:
            print("Allocation NOT found in table!")
            sys.exit(1)

        # 5. Remove professional from project
        print("Removing professional from project...")
        resp = requests.delete(f"{BASE_URL}/projects/{proj_id}/allocations/{alloc_id}")
        if resp.status_code != 200:
            print(f"Failed to remove professional: {resp.text}")
            sys.exit(1)
        print("Professional removed.")

        # 6. Verify allocation is gone
        print("Verifying allocation is gone...")
        resp = requests.get(f"{BASE_URL}/projects/{proj_id}/allocation_table")
        if resp.status_code != 200:
            print(f"Failed to get allocation table: {resp.text}")
            sys.exit(1)
        table_data = resp.json()

        found = False
        for alloc in table_data["allocations"]:
            if alloc["allocation_id"] == alloc_id:
                found = True
                break

        if found:
            print("Allocation STILL found in table after deletion!")
            sys.exit(1)
        else:
            print("Allocation successfully removed from table.")

    finally:
        # Cleanup
        print("Cleaning up...")
        requests.delete(f"{BASE_URL}/projects/{proj_id}")
        pass

    print("Verification successful!")


if __name__ == "__main__":
    test_allocations()

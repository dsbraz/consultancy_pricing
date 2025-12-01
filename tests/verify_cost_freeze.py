import requests
import sys

BASE_URL = "http://localhost:8080"


def verify_cost_freeze():
    """
    Verification script for cost freeze functionality.

    This script tests that professional costs are frozen at allocation time:
    1. Creates a professional with Cost A
    2. Allocates them to Project P
    3. Verifies Project P's cost calculation uses Cost A
    4. Updates professional to Cost B
    5. Verifies Project P's cost calculation *still* uses Cost A
    6. Creates a new allocation to Project Q
    7. Verifies Project Q uses Cost B
    """
    print("Starting cost freeze verification...")

    # Step 1: Create a professional with Cost A (100.0)
    print("Creating test professional with hourly_cost = 100.0...")
    prof_data = {
        "pid": "TEST_FREEZE_001",
        "name": "Test Professional Freeze",
        "role": "Developer",
        "level": "Senior",
        "is_template": False,
        "hourly_cost": 100.0,
    }

    resp = requests.post(f"{BASE_URL}/professionals/", json=prof_data)
    if resp.status_code != 200:
        print(f"Failed to create professional: {resp.text}")
        sys.exit(1)

    professional = resp.json()
    prof_id = professional["id"]
    print(
        f"Professional created with ID: {prof_id}, Cost: {professional['hourly_cost']}"
    )

    # Step 2: Create Project P
    print("Creating Project P...")
    project_p_data = {
        "name": "Project P - Cost Freeze Test",
        "start_date": "2024-01-01",
        "duration_months": 1,
        "tax_rate": 10.0,
        "margin_rate": 20.0,
        "allocations": [],
    }

    resp = requests.post(f"{BASE_URL}/projects/", json=project_p_data)
    if resp.status_code != 200:
        print(f"Failed to create project P: {resp.text}")
        sys.exit(1)

    project_p = resp.json()
    project_p_id = project_p["id"]
    print(f"Project P created with ID: {project_p_id}")

    try:
        # Step 3: Add professional to Project P
        print("Adding professional to Project P...")
        url = f"{BASE_URL}/projects/{project_p_id}/allocations/?professional_id={prof_id}&selling_hourly_rate=150.0"
        resp = requests.post(url)
        if resp.status_code != 200:
            print(f"Failed to add professional to project P: {resp.text}")
            sys.exit(1)

        _ = resp.json()
        print("Professional allocated to Project P")

        # Get allocation details to verify cost_hourly_rate
        resp = requests.get(f"{BASE_URL}/projects/{project_p_id}/allocations")
        if resp.status_code != 200:
            print(f"Failed to get allocations: {resp.text}")
            sys.exit(1)

        allocations = resp.json()
        if not allocations:
            print("No allocations found")
            sys.exit(1)

        allocation_p_data = allocations[0]
        frozen_cost_p = allocation_p_data.get("cost_hourly_rate", 0)
        print(f"Frozen cost in Project P allocation: {frozen_cost_p}")

        if frozen_cost_p != 100.0:
            print(f"Mismatch! Expected frozen cost to be 100.0, got {frozen_cost_p}")
            sys.exit(1)

        # Set some hours for calculation
        print("Setting hours for Project P allocation...")
        weekly_alloc_id = allocation_p_data["weekly_allocations"][0]["id"]
        update_data = [
            {"weekly_allocation_id": weekly_alloc_id, "hours_allocated": 40.0}
        ]

        resp = requests.put(
            f"{BASE_URL}/projects/{project_p_id}/allocations", json=update_data
        )
        if resp.status_code != 200:
            print(f"Failed to update hours: {resp.text}")
            sys.exit(1)
        print("Hours set to 40.0")

        # Step 4: Get pricing for Project P (should use Cost A = 100.0)
        print("Calculating pricing for Project P...")
        resp = requests.get(f"{BASE_URL}/projects/{project_p_id}/pricing")
        if resp.status_code != 200:
            print(f"Failed to get pricing: {resp.text}")
            sys.exit(1)

        pricing_p_before = resp.json()
        expected_cost_before = 40.0 * 100.0  # 40 hours * 100.0 cost
        actual_cost_before = pricing_p_before["total_cost"]

        print(f"Total Cost: {actual_cost_before}, Expected: {expected_cost_before}")

        if abs(actual_cost_before - expected_cost_before) > 0.01:
            print(f"Mismatch! Cost: {actual_cost_before} != {expected_cost_before}")
            sys.exit(1)
        print("Project P uses Cost A (100.0)")

        # Step 5: Update professional to Cost B (200.0)
        print("Updating professional hourly_cost to 200.0...")
        update_prof_data = {"hourly_cost": 200.0}

        resp = requests.put(
            f"{BASE_URL}/professionals/{prof_id}", json=update_prof_data
        )
        if resp.status_code != 200:
            print(f"Failed to update professional: {resp.text}")
            sys.exit(1)

        updated_prof = resp.json()
        print(f"Professional updated: Cost={updated_prof['hourly_cost']}")

        # Step 6: Verify Project P still uses Cost A
        print("Re-calculating pricing for Project P (should still use Cost A)...")
        resp = requests.get(f"{BASE_URL}/projects/{project_p_id}/pricing")
        if resp.status_code != 200:
            print(f"Failed to get pricing: {resp.text}")
            sys.exit(1)

        pricing_p_after = resp.json()
        actual_cost_after = pricing_p_after["total_cost"]

        print(
            f"Total Cost: {actual_cost_after}, Expected: {expected_cost_before} (unchanged)"
        )

        if abs(actual_cost_after - expected_cost_before) > 0.01:
            print(
                f"Mismatch! Cost changed: {actual_cost_after} != {expected_cost_before}"
            )
            print(
                "COST FREEZE FAILED - Project P cost changed when professional cost changed!"
            )
            sys.exit(1)
        print("Project P STILL uses Cost A (100.0) - COST FREEZE WORKING!")

        # Step 7: Create Project Q
        print("Creating Project Q...")
        project_q_data = {
            "name": "Project Q - Cost Freeze Test",
            "start_date": "2024-01-01",
            "duration_months": 1,
            "tax_rate": 10.0,
            "margin_rate": 20.0,
            "allocations": [],
        }

        resp = requests.post(f"{BASE_URL}/projects/", json=project_q_data)
        if resp.status_code != 200:
            print(f"Failed to create project Q: {resp.text}")
            sys.exit(1)

        project_q = resp.json()
        project_q_id = project_q["id"]
        print(f"Project Q created with ID: {project_q_id}")

        # Add professional to Project Q
        print("Adding professional to Project Q...")
        url = f"{BASE_URL}/projects/{project_q_id}/allocations/?professional_id={prof_id}&selling_hourly_rate=300.0"
        resp = requests.post(url)
        if resp.status_code != 200:
            print(f"Failed to add professional to project Q: {resp.text}")
            sys.exit(1)

        print("Professional allocated to Project Q")

        # Get allocation details for Project Q
        resp = requests.get(f"{BASE_URL}/projects/{project_q_id}/allocations")
        if resp.status_code != 200:
            print(f"Failed to get allocations: {resp.text}")
            sys.exit(1)

        allocations_q = resp.json()
        allocation_q_data = allocations_q[0]
        frozen_cost_q = allocation_q_data.get("cost_hourly_rate", 0)
        print(f"Frozen cost in Project Q allocation: {frozen_cost_q}")

        if frozen_cost_q != 200.0:
            print(
                f"Mismatch! Expected frozen cost to be 200.0 (new cost), got {frozen_cost_q}"
            )
            sys.exit(1)

        # Set hours for Project Q
        weekly_alloc_q_id = allocation_q_data["weekly_allocations"][0]["id"]
        update_data_q = [
            {"weekly_allocation_id": weekly_alloc_q_id, "hours_allocated": 40.0}
        ]

        resp = requests.put(
            f"{BASE_URL}/projects/{project_q_id}/allocations", json=update_data_q
        )
        if resp.status_code != 200:
            print(f"Failed to update hours: {resp.text}")
            sys.exit(1)

        # Step 8: Verify Project Q uses Cost B
        print("Calculating pricing for Project Q (should use Cost B = 200.0)...")
        resp = requests.get(f"{BASE_URL}/projects/{project_q_id}/pricing")
        if resp.status_code != 200:
            print(f"Failed to get pricing: {resp.text}")
            sys.exit(1)

        pricing_q = resp.json()
        expected_cost_q = 40.0 * 200.0  # 40 hours * 200.0 cost
        actual_cost_q = pricing_q["total_cost"]

        print(f"Total Cost: {actual_cost_q}, Expected: {expected_cost_q}")

        if abs(actual_cost_q - expected_cost_q) > 0.01:
            print(f"Mismatch! Cost: {actual_cost_q} != {expected_cost_q}")
            sys.exit(1)
        print("Project Q uses Cost B (200.0)")

        # Cleanup
        print("Cleaning up...")
        requests.delete(f"{BASE_URL}/projects/{project_q_id}")

    finally:
        # Cleanup Project P and Professional
        requests.delete(f"{BASE_URL}/projects/{project_p_id}")
        requests.delete(f"{BASE_URL}/professionals/{prof_id}")

    print("Verification successful!")


if __name__ == "__main__":
    verify_cost_freeze()

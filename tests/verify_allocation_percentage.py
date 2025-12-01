import requests
import datetime

BASE_URL = "http://localhost:8080"


def verify_allocation_percentage():
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    # 1. Create a professional
    prof_data = {
        "name": f"Test Prof Percentage {timestamp}",
        "role": "Developer",
        "level": "Senior",
        "hourly_cost": 100.0,
        "pid": f"PROF{timestamp}",
    }
    resp = requests.post(f"{BASE_URL}/professionals/", json=prof_data)
    if resp.status_code != 200:
        print(f"Create professional failed: {resp.status_code} - {resp.text}")
    assert resp.status_code == 200
    prof_id = resp.json()["id"]
    print(f"Created professional with ID: {prof_id}")

    # 2. Create an offer with 50% allocation
    offer_data = {
        "name": f"Half Time Offer {timestamp}",
        "items": [
            {
                "role": "Developer",
                "level": "Senior",
                "quantity": 1,
                "allocation_percentage": 50.0,
                "professional_id": prof_id,
            }
        ],
    }
    resp = requests.post(f"{BASE_URL}/offers/", json=offer_data)
    if resp.status_code != 200:
        print(f"Create offer failed: {resp.text}")
    assert resp.status_code == 200
    offer_id = resp.json()["id"]
    print(f"Created offer with ID: {offer_id}")

    # 3. Create a project
    project_data = {
        "name": f"Percentage Project {timestamp}",
        "start_date": datetime.date.today().isoformat(),
        "duration_months": 1,
        "tax_rate": 10.0,
        "margin_rate": 20.0,
    }
    resp = requests.post(f"{BASE_URL}/projects/", json=project_data)
    assert resp.status_code == 200
    project_id = resp.json()["id"]
    print(f"Created project with ID: {project_id}")

    # 4. Apply offer
    resp = requests.post(
        f"{BASE_URL}/projects/{project_id}/offers", json={"offer_id": offer_id}
    )
    if resp.status_code != 200:
        print(f"Apply offer failed: {resp.status_code} - {resp.text}")
    assert resp.status_code == 200
    print("Applied offer")

    # 5. Get allocation table
    resp = requests.get(f"{BASE_URL}/projects/{project_id}/allocation_table")
    assert resp.status_code == 200
    data = resp.json()

    # 6. Verify hours
    allocations = data["allocations"]
    assert len(allocations) == 1
    allocation = allocations[0]

    # Check weekly hours
    weeks = allocation["weekly_hours"]
    for week_num, week_data in weeks.items():
        hours_allocated = week_data["hours_allocated"]
        available_hours = week_data["available_hours"]

        # Formula: available_hours * percentage
        expected_hours = available_hours * 0.5

        print(
            f"Week {week_num}: Allocated {hours_allocated}, Available {available_hours}, Expected {expected_hours}"
        )
        assert abs(hours_allocated - expected_hours) < 0.01, (
            f"Week {week_num} mismatch: got {hours_allocated}, expected {expected_hours}"
        )

    print("Verification successful!")


if __name__ == "__main__":
    try:
        verify_allocation_percentage()
    except Exception:
        import traceback

        traceback.print_exc()
        exit(1)

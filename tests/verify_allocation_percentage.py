import requests
import datetime

BASE_URL = "http://localhost:8000"

def verify_allocation_percentage():
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    
    # 1. Create a professional
    prof_data = {
        "name": f"Test Prof Percentage {timestamp}",
        "role": "Developer",
        "level": "Senior",
        "hourly_cost": 100.0
    }
    resp = requests.post(f"{BASE_URL}/professionals/", json=prof_data)
    assert resp.status_code == 200
    prof_id = resp.json()["id"]
    print(f"Created professional with ID: {prof_id}")

    # 2. Create a template with 50% allocation
    template_data = {
        "name": f"Half Time Template {timestamp}",
        "items": [
            {
                "role": "Developer",
                "level": "Senior",
                "quantity": 1,
                "allocation_percentage": 50.0,
                "professional_id": prof_id
            }
        ]
    }
    resp = requests.post(f"{BASE_URL}/templates/", json=template_data)
    if resp.status_code != 200:
        print(f"Create template failed: {resp.text}")
    assert resp.status_code == 200
    template_id = resp.json()["id"]
    print(f"Created template with ID: {template_id}")

    # 3. Create a project
    project_data = {
        "name": f"Percentage Project {timestamp}",
        "start_date": datetime.date.today().isoformat(),
        "duration_months": 1,
        "tax_rate": 10.0,
        "margin_rate": 20.0
    }
    resp = requests.post(f"{BASE_URL}/projects/", json=project_data)
    assert resp.status_code == 200
    project_id = resp.json()["id"]
    print(f"Created project with ID: {project_id}")

    # 4. Apply template
    resp = requests.post(f"{BASE_URL}/projects/{project_id}/apply_template/{template_id}")
    assert resp.status_code == 200
    print("Applied template")

    # 5. Get allocation table
    resp = requests.get(f"{BASE_URL}/projects/{project_id}/allocation_table")
    assert resp.status_code == 200
    data = resp.json()
    
    # 6. Verify hours
    allocations = data["allocations"]
    assert len(allocations) == 1
    allocation = allocations[0]
    
    # Check weekly hours
    # Assuming standard week is 40h, 50% should be 20h
    # Note: available_hours might be less if there are holidays, but let's check the logic
    # The logic is min(40 * percentage/100, available_hours)
    
    weeks = allocation["weekly_hours"]
    for week_num, week_data in weeks.items():
        hours_allocated = week_data["hours_allocated"]
        available_hours = week_data["available_hours"]
        
        # User requirement: if week has 32h and 50%, it should be 16h.
        # Formula: available_hours * percentage
        expected_hours = available_hours * 0.5
        
        print(f"Week {week_num}: Allocated {hours_allocated}, Available {available_hours}, Expected {expected_hours}")
        assert abs(hours_allocated - expected_hours) < 0.01, f"Week {week_num} mismatch: got {hours_allocated}, expected {expected_hours}"

    print("Verification successful!")

if __name__ == "__main__":
    try:
        verify_allocation_percentage()
    except Exception as e:
        print(f"Verification failed: {e}")
        exit(1)

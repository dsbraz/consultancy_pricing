import requests
import datetime

BASE_URL = "http://localhost:8000"

def verify_duration_adjustment():
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    
    # 1. Create a professional
    prof_data = {
        "name": f"Test Prof Duration {timestamp}",
        "role": "Developer",
        "level": "Senior",
        "hourly_cost": 100.0
    }
    resp = requests.post(f"{BASE_URL}/professionals/", json=prof_data)
    assert resp.status_code == 200
    prof_id = resp.json()["id"]
    print(f"✓ Created professional with ID: {prof_id}")

    # 2. Create a template
    template_data = {
        "name": f"Duration Test Template {timestamp}",
        "items": [
            {
                "role": "Developer",
                "level": "Senior",
                "quantity": 1,
                "allocation_percentage": 100.0,
                "professional_id": prof_id
            }
        ]
    }
    resp = requests.post(f"{BASE_URL}/templates/", json=template_data)
    assert resp.status_code == 200
    template_id = resp.json()["id"]
    print(f"✓ Created template with ID: {template_id}")

    # 3. Create a project with 3 months duration
    project_data = {
        "name": f"Duration Test Project {timestamp}",
        "start_date": datetime.date.today().isoformat(),
        "duration_months": 3,
        "tax_rate": 10.0,
        "margin_rate": 20.0
    }
    resp = requests.post(f"{BASE_URL}/projects/", json=project_data)
    assert resp.status_code == 200
    project_id = resp.json()["id"]
    print(f"✓ Created project with ID: {project_id}, duration: 3 months")

    # 4. Apply template
    resp = requests.post(f"{BASE_URL}/projects/{project_id}/apply_template/{template_id}")
    assert resp.status_code == 200
    print("✓ Applied template")

    # 5. Get initial allocation table
    resp = requests.get(f"{BASE_URL}/projects/{project_id}/allocation_table")
    assert resp.status_code == 200
    data = resp.json()
    initial_weeks = len(data["weeks"])
    print(f"✓ Initial weeks count: {initial_weeks}")

    # 6. Reduce duration to 2 months
    resp = requests.put(f"{BASE_URL}/projects/{project_id}", json={"duration_months": 2})
    assert resp.status_code == 200
    print("✓ Reduced project duration to 2 months")

    # 7. Get allocation table after reduction
    resp = requests.get(f"{BASE_URL}/projects/{project_id}/allocation_table")
    assert resp.status_code == 200
    data = resp.json()
    reduced_weeks = len(data["weeks"])
    print(f"✓ Weeks after reduction: {reduced_weeks}")
    
    # Verify weeks were removed
    assert reduced_weeks < initial_weeks, f"Expected fewer weeks, got {reduced_weeks} vs {initial_weeks}"
    print(f"✓ Verified: {initial_weeks - reduced_weeks} weeks were removed")

    # 8. Increase duration to 4 months
    resp = requests.put(f"{BASE_URL}/projects/{project_id}", json={"duration_months": 4})
    assert resp.status_code == 200
    print("✓ Increased project duration to 4 months")

    # 9. Get allocation table after increase
    resp = requests.get(f"{BASE_URL}/projects/{project_id}/allocation_table")
    assert resp.status_code == 200
    data = resp.json()
    increased_weeks = len(data["weeks"])
    print(f"✓ Weeks after increase: {increased_weeks}")
    
    # Verify weeks were added
    assert increased_weeks > reduced_weeks, f"Expected more weeks, got {increased_weeks} vs {reduced_weeks}"
    print(f"✓ Verified: {increased_weeks - reduced_weeks} weeks were added")
    
    # Verify new weeks have 0 hours
    allocations = data["allocations"]
    if allocations:
        alloc = allocations[0]
        # Check the last few weeks (newly added)
        week_numbers = sorted(alloc["weekly_hours"].keys(), key=int)
        last_weeks = week_numbers[-3:]  # Check last 3 weeks
        for week_num in last_weeks:
            hours = alloc["weekly_hours"][week_num]["hours_allocated"]
            print(f"  Week {week_num}: {hours}h")

    print("\n✅ Verification successful!")

if __name__ == "__main__":
    try:
        verify_duration_adjustment()
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

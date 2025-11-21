import requests
import datetime

BASE_URL = "http://localhost:8000"

def test_delete_professional():
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    
    # 1. Create two professionals
    prof1_data = {
        "name": f"Test Prof Delete 1 {timestamp}",
        "role": "Developer",
        "level": "Senior",
        "hourly_cost": 100.0,
        "pid": f"DEL001_{timestamp}"
    }
    resp = requests.post(f"{BASE_URL}/professionals/", json=prof1_data)
    prof1_id = resp.json()["id"]
    print(f"✓ Created professional 1 with ID: {prof1_id}")

    prof2_data = {
        "name": f"Test Prof Delete 2 {timestamp}",
        "role": "Designer",
        "level": "Junior",
        "hourly_cost": 80.0,
        "pid": f"DEL002_{timestamp}"
    }
    resp = requests.post(f"{BASE_URL}/professionals/", json=prof2_data)
    prof2_id = resp.json()["id"]
    print(f"✓ Created professional 2 with ID: {prof2_id}")

    # 2. Create a project
    project_data = {
        "name": f"Delete Test Project {timestamp}",
        "start_date": datetime.date.today().isoformat(),
        "duration_months": 2,
        "tax_rate": 10.0,
        "margin_rate": 20.0
    }
    resp = requests.post(f"{BASE_URL}/projects/", json=project_data)
    project_id = resp.json()["id"]
    print(f"✓ Created project with ID: {project_id}")

    # 3. Add both professionals to the project
    resp = requests.post(f"{BASE_URL}/projects/{project_id}/allocations/?professional_id={prof1_id}")
    assert resp.status_code == 200
    alloc1_id = resp.json()["allocation_id"]
    print(f"✓ Added professional 1, allocation ID: {alloc1_id}")

    resp = requests.post(f"{BASE_URL}/projects/{project_id}/allocations/?professional_id={prof2_id}")
    assert resp.status_code == 200
    alloc2_id = resp.json()["allocation_id"]
    print(f"✓ Added professional 2, allocation ID: {alloc2_id}")

    # 4. Get allocation table - should have 2 professionals
    resp = requests.get(f"{BASE_URL}/projects/{project_id}/allocation_table")
    data = resp.json()
    print(f"✓ Allocation table has {len(data['allocations'])} professionals")
    assert len(data['allocations']) == 2

    # 5. Delete professional 1
    resp = requests.delete(f"{BASE_URL}/projects/{project_id}/allocations/{alloc1_id}")
    assert resp.status_code == 200
    result = resp.json()
    print(f"✓ Delete response: {result['message']}")

    # 6. Get allocation table again - should have 1 professional
    resp = requests.get(f"{BASE_URL}/projects/{project_id}/allocation_table")
    data = resp.json()
    print(f"✓ After delete, allocation table has {len(data['allocations'])} professionals")
    assert len(data['allocations']) == 1
    assert data['allocations'][0]['allocation_id'] == alloc2_id
    print(f"✓ Remaining professional: {data['allocations'][0]['professional']['name']}")

    print("\n✅ Delete functionality works correctly!")

if __name__ == "__main__":
    try:
        test_delete_professional()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

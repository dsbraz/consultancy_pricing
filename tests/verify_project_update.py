import requests
import sys

BASE_URL = "http://localhost:8080"

def verify_project_update():
    print("Starting project update verification...")

    # 1. Create a test project
    proj_data = {
        "name": "Test Update Project",
        "start_date": "2024-01-01",
        "duration_months": 3,
        "tax_rate": 10.0,
        "margin_rate": 30.0,
        "allocations": [],
    }
    resp = requests.post(f"{BASE_URL}/projects/", json=proj_data)
    if resp.status_code != 200:
        print(f"Failed to create project: {resp.text}")
        sys.exit(1)
    proj_id = resp.json()["id"]
    print(f"Created project {proj_id}")

    try:
        # 2. Update the project
        update_data = {
            "name": "Updated Project Name",
            "duration_months": 6,
            "tax_rate": 15.0,
            "margin_rate": 40.0
        }
        resp = requests.patch(f"{BASE_URL}/projects/{proj_id}", json=update_data)
        if resp.status_code != 200:
            print(f"Failed to update project: {resp.text}")
            sys.exit(1)
        
        updated_proj = resp.json()
        
        # 3. Verify updates
        errors = []
        if updated_proj["name"] != update_data["name"]:
            errors.append(f"Name mismatch: expected {update_data['name']}, got {updated_proj['name']}")
        if updated_proj["duration_months"] != update_data["duration_months"]:
            errors.append(f"Duration mismatch: expected {update_data['duration_months']}, got {updated_proj['duration_months']}")
        if updated_proj["tax_rate"] != update_data["tax_rate"]:
            errors.append(f"Tax rate mismatch: expected {update_data['tax_rate']}, got {updated_proj['tax_rate']}")
        if updated_proj["margin_rate"] != update_data["margin_rate"]:
            errors.append(f"Margin rate mismatch: expected {update_data['margin_rate']}, got {updated_proj['margin_rate']}")
            
        if errors:
            print("Verification FAILED:")
            for e in errors:
                print(f"  - {e}")
            sys.exit(1)
            
        print("Project updates verified successfully.")

    finally:
        # Cleanup
        requests.delete(f"{BASE_URL}/projects/{proj_id}")

    print("Verification script completed successfully!")

if __name__ == "__main__":
    verify_project_update()

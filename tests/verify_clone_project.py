import requests
import sys

BASE_URL = "http://localhost:8080"


def verify_clone_project():
    print("Verifying Project Cloning...")

    # 1. Create a project
    project_data = {
        "name": "Project to Clone",
        "start_date": "2024-01-01",
        "duration_months": 3,
        "tax_rate": 10,
        "margin_rate": 30,
        "allocations": [],
    }
    response = requests.post(f"{BASE_URL}/projects/", json=project_data)
    if response.status_code != 200:
        print(f"Failed to create project: {response.text}")
        sys.exit(1)
    project_id = response.json()["id"]
    print(f"Created project {project_id}")

    # 2. Add a professional (assuming professional ID 1 exists, if not create one)
    # First check for professionals
    profs = requests.get(f"{BASE_URL}/professionals/").json()
    if not profs:
        # Create a professional if none exist
        prof_data = {
            "pid": "TEST001",
            "name": "Test Prof",
            "role": "Dev",
            "level": "Senior",
            "hourly_cost": 100,
        }
        prof_res = requests.post(f"{BASE_URL}/professionals/", json=prof_data)
        prof_id = prof_res.json()["id"]
    else:
        prof_id = profs[0]["id"]

    # Add allocation
    alloc_res = requests.post(
        f"{BASE_URL}/projects/{project_id}/allocations/?professional_id={prof_id}"
    )
    if alloc_res.status_code != 200:
        print(f"Failed to add allocation: {alloc_res.text}")
        sys.exit(1)
    print("Added allocation")

    # 3. Clone the project
    clone_res = requests.post(f"{BASE_URL}/projects/{project_id}/clone")
    if clone_res.status_code != 200:
        print(f"Failed to clone project: {clone_res.text}")
        sys.exit(1)

    cloned_project = clone_res.json()
    cloned_id = cloned_project["id"]
    print(f"Cloned project created: {cloned_id}")

    # 4. Verify Clone Data
    if cloned_project["name"] != f"Cópia de {project_data['name']}":
        print(f"ERROR: Incorrect cloned name: {cloned_project['name']}")
        sys.exit(1)

    if cloned_project["start_date"] != project_data["start_date"]:
        print("ERROR: Incorrect start date")
        sys.exit(1)

    # Verify allocations in clone
    clone_details = requests.get(
        f"{BASE_URL}/projects/{cloned_id}/allocation_table"
    ).json()
    if len(clone_details["allocations"]) != 1:
        print(
            f"ERROR: Clone should have 1 allocation, found {len(clone_details['allocations'])}"
        )
        sys.exit(1)

    print("Clone verification successful!")

    # Cleanup
    requests.delete(f"{BASE_URL}/projects/{project_id}")
    requests.delete(f"{BASE_URL}/projects/{cloned_id}")
    print("Cleanup done.")


if __name__ == "__main__":
    verify_clone_project()

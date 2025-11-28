import requests
import sys

BASE_URL = "http://localhost:8080"


def verify_full_flow():
    print("Starting Full Flow Verification...")

    # 2. Create Professionals
    print("Creating Professionals...")
    prof1_resp = requests.post(
        f"{BASE_URL}/professionals/",
        json={
            "name": "Dev 1",
            "role": "Developer",
            "level": "Senior",
            "is_template": False,
            "hourly_cost": 100.0,
            "pid": "DEV001",
        },
    )
    if prof1_resp.status_code != 200:
        print(f"Failed to create professional 1: {prof1_resp.text}")
        sys.exit(1)
    prof1 = prof1_resp.json()

    prof2_resp = requests.post(
        f"{BASE_URL}/professionals/",
        json={
            "name": "PM 1",
            "role": "Project Manager",
            "level": "Senior",
            "is_template": False,
            "hourly_cost": 150.0,
            "pid": "PM001",
        },
    )
    if prof2_resp.status_code != 200:
        print(f"Failed to create professional 2: {prof2_resp.text}")
        sys.exit(1)
    prof2 = prof2_resp.json()

    # 3. Create Offer
    print("Creating Offer...")
    offer_resp = requests.post(
        f"{BASE_URL}/offers/",
        json={
            "name": "Standard Squad",
            "items": [
                {
                    "role": "Developer",
                    "level": "Senior",
                    "quantity": 2,
                    "professional_id": prof1["id"],
                    "allocation_percentage": 100.0,
                },
                {
                    "role": "Project Manager",
                    "level": "Senior",
                    "quantity": 1,
                    "professional_id": prof2["id"],
                    "allocation_percentage": 100.0,
                },
            ],
        },
    )
    if offer_resp.status_code != 200:
        print(f"Failed to create offer: {offer_resp.text}")
        sys.exit(1)
    offer = offer_resp.json()
    print("Offer Response:", offer)

    # 4. Create Project
    print("Creating Project...")
    project_resp = requests.post(
        f"{BASE_URL}/projects/",
        json={
            "name": "New App",
            "start_date": "2024-01-01",
            "duration_months": 3,
            "tax_rate": 10.0,
            "margin_rate": 20.0,
        },
    )
    if project_resp.status_code != 200:
        print(f"Failed to create project: {project_resp.text}")
        sys.exit(1)
    project = project_resp.json()
    print("Project Response:", project)

    # 5. Apply Offer
    print("Applying Offer...")
    apply_resp = requests.post(
        f"{BASE_URL}/projects/{project['id']}/offers", json={"offer_id": offer["id"]}
    )
    if apply_resp.status_code != 200:
        print(f"Failed to apply offer: {apply_resp.text}")
        sys.exit(1)
    apply_res = apply_resp.json()
    print("Allocations added:", apply_res["allocations"])

    # 6. Calculate Price
    print("Calculating Price...")
    try:
        price_resp = requests.get(f"{BASE_URL}/projects/{project['id']}/pricing")
        if price_resp.status_code != 200:
            print(f"Failed to calculate price: {price_resp.text}")
            sys.exit(1)
        price_res = price_resp.json()
        print("Price Result:", price_res)

        # Validation
        assert price_res["total_cost"] > 0
        assert price_res["final_price"] > price_res["total_cost"]
        print("✅ Verification Successful!")

    except Exception as e:
        print(f"Error calculating price: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        verify_full_flow()
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

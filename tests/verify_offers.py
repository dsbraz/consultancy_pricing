import json
import urllib.error
import urllib.request
import urllib.parse
from datetime import date

BASE_URL = "http://localhost:8080"


def make_request(method, endpoint, data=None, params=None):
    url = f"{BASE_URL}{endpoint}"
    if params:
        query_string = urllib.parse.urlencode(params)
        url = f"{url}?{query_string}"

    headers = {"Content-Type": "application/json"}

    if data:
        json_data = json.dumps(data).encode("utf-8")
    else:
        json_data = None

    req = urllib.request.Request(url, data=json_data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode("utf-8")
            return json.loads(response_data)
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
        raise


def test_offer_flow():
    print("Starting Offer Verification Flow...")

    # 1. Create Specific Professional
    print("\n1. Creating Specific Professional...")
    prof_data = {
        "name": "Offer Specialist",
        "role": "Architect",
        "level": "Principal",
        "hourly_cost": 200.0,
        "pid": "SPEC001",
    }
    prof = make_request("POST", "/professionals/", data=prof_data)
    prof_id = prof["id"]
    print(f"Created professional: {prof['name']} (ID: {prof_id})")

    # 2a. Create Template Professional
    print("\n2a. Creating Template Professional...")
    tmpl_data = {
        "name": "Template Developer Junior",
        "role": "Developer",
        "level": "Junior",
        "hourly_cost": 100.0,
        "pid": "TMPL001",
        "is_template": True,
    }
    tmpl = make_request("POST", "/professionals/", data=tmpl_data)
    tmpl_id = tmpl["id"]
    print(f"Created template: {tmpl['name']} (ID: {tmpl_id})")

    # 2b. Create Offer with Specific Professional and Template
    print("\n2b. Creating Offer with Specific Professional and Template...")
    off_data = {
        "name": "Specialist Team Offer",
        "items": [
            {"role": "Architect", "level": "Principal", "professional_id": prof_id},
            {"role": "Developer", "level": "Junior", "professional_id": tmpl_id},
        ],
    }
    off = make_request("POST", "/offers/", data=off_data)
    off_id = off["id"]
    print(f"Created offer: {off['name']} (ID: {off_id})")

    # 3. Create Project
    print("\n3. Creating Project...")
    proj_data = {
        "name": "Offer Test Project",
        "start_date": date.today().isoformat(),
        "duration_months": 2,
        "tax_rate": 10.0,
        "margin_rate": 20.0,
        "allocations": [],
    }
    proj = make_request("POST", "/projects/", data=proj_data)
    proj_id = proj["id"]
    print(f"Created project: {proj['name']} (ID: {proj_id})")

    # 4. Apply Offer
    print("\n4. Applying Offer...")
    res = make_request("POST", f"/projects/{proj_id}/offers", data={"offer_id": off_id})
    print(f"Offer applied. Allocations: {res['allocations']}")

    # 5. Verify Allocations
    print("\n5. Verifying Allocations...")
    proj_data = make_request("GET", f"/projects/{proj_id}?include_allocations=true")
    allocations = proj_data.get("allocations", [])

    found_specialist = False
    found_template = False

    for alloc in allocations:
        p = alloc["professional"]
        if p["id"] == prof_id:
            found_specialist = True
            print(f"Found Specialist: {p['name']}")
            expected_rate = 250.0
            if abs(alloc["selling_hourly_rate"] - expected_rate) < 0.01:
                print(f"Selling Rate Correct: {alloc['selling_hourly_rate']}")
            else:
                print(
                    f"Selling Rate Incorrect: {alloc['selling_hourly_rate']} (Expected {expected_rate})"
                )

        elif p["id"] == tmpl_id:
            found_template = True
            print(f"Found Template: {p['name']} (ID: {p['id']} - Matches Original)")

    assert found_specialist, "Specific professional not found in allocations"
    assert found_template, "Template not found in allocations"

    print("\nOffer verification passed successfully!")


if __name__ == "__main__":
    try:
        test_offer_flow()
    except AssertionError as e:
        print(f"Test failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

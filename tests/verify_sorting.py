import requests

import sys

BASE_URL = "http://localhost:8080"


def verify_sorting():
    print("Running sorting verification against Docker environment...")

    # 1. Verify Professionals Sorting
    print("\n1. Verifying Professionals Sorting...")
    try:
        resp = requests.get(f"{BASE_URL}/professionals/")
        if resp.status_code != 200:
            print(f"❌ Failed to fetch professionals. Status: {resp.status_code}")
            return False

        profs = resp.json()
        names = [p["name"] for p in profs]

        # Check if sorted
        if names == sorted(names, key=str.lower):
            print(f"✅ Professionals are sorted correctly ({len(names)} items)")
        else:
            print("❌ Professionals are NOT sorted!")
            print(f"First 5 names: {names[:5]}")
            return False

    except Exception as e:
        print(f"❌ Error verifying professionals: {e}")
        return False

    # 2. Verify Offers Sorting
    print("\n2. Verifying Offers Sorting...")
    try:
        resp = requests.get(f"{BASE_URL}/offers/")
        if resp.status_code != 200:
            print(f"❌ Failed to fetch offers. Status: {resp.status_code}")
            return False

        offers = resp.json()
        names = [o["name"] for o in offers]

        if names == sorted(names, key=str.lower):
            print(f"✅ Offers are sorted correctly ({len(names)} items)")
        else:
            print("❌ Offers are NOT sorted!")
            print(f"First 5 names: {names[:5]}")
            return False

    except Exception as e:
        print(f"❌ Error verifying offers: {e}")
        return False

    # 3. Verify Projects Sorting
    print("\n3. Verifying Projects Sorting...")
    try:
        resp = requests.get(f"{BASE_URL}/projects/")
        if resp.status_code != 200:
            print(f"❌ Failed to fetch projects. Status: {resp.status_code}")
            return False

        projects = resp.json()
        names = [p["name"] for p in projects]

        if names == sorted(names, key=str.lower):
            print(f"✅ Projects are sorted correctly ({len(names)} items)")
        else:
            print("❌ Projects are NOT sorted!")
            print(f"First 5 names: {names[:5]}")
            return False

    except Exception as e:
        print(f"❌ Error verifying projects: {e}")
        return False

    return True


if __name__ == "__main__":
    success = verify_sorting()
    if success:
        print("\n🎉 All sorting tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Sorting tests failed!")
        sys.exit(1)

import requests
import os

# Test CSV import functionality
BASE_URL = "http://localhost:8080"

def verify_csv_import():
    """Test importing professionals from CSV file"""
    
    # Create a test CSV file
    csv_content = """pid,name,role,level,is_template,hourly_cost
PROF001,Test Professional 1,Desenvolvedor,Sênior,false,150.00
PROF002,Test Professional 2,Designer,Pleno,false,120.00
VAC001,Test Vacancy,Desenvolvedor,Júnior,true,80.00"""
    
    csv_file_path = "/tmp/test_professionals.csv"
    with open(csv_file_path, 'w') as f:
        f.write(csv_content)
    
    print("Testing CSV import...")
    
    # Upload CSV file
    with open(csv_file_path, 'rb') as f:
        files = {'file': ('test_professionals.csv', f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/professionals/import-csv", files=files)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Import successful!")
        print(f"   Created: {result['created']}")
        print(f"   Updated: {result['updated']}")
        print(f"   Errors: {result['errors']}")
        if result['error_details']:
            print(f"   Error details: {result['error_details']}")
    else:
        print(f"\n❌ Import failed!")
    
    # Clean up
    os.remove(csv_file_path)
    
    # Verify professionals were created
    print("\nFetching all professionals...")
    response = requests.get(f"{BASE_URL}/professionals/")
    professionals = response.json()
    
    print(f"Total professionals: {len(professionals)}")
    for prof in professionals:
        if prof['name'].startswith('Test'):
            print(f"  - [{prof.get('pid')}] {prof['name']}: {prof['role']} ({prof['level']}) - R$ {prof['hourly_cost']}")
    
    # Test update by importing again with modified data
    print("\n\nTesting update functionality...")
    csv_content_updated = """pid,name,role,level,is_template,hourly_cost
PROF001,Test Professional 1,Desenvolvedor,Pleno,false,130.00
PROF002,Test Professional 2,Designer,Sênior,false,160.00"""
    
    with open(csv_file_path, 'w') as f:
        f.write(csv_content_updated)
    
    with open(csv_file_path, 'rb') as f:
        files = {'file': ('test_professionals.csv', f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/professionals/import-csv", files=files)
    
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Response: {result}")
    print(f"\n✅ Update test completed!")
    print(f"   Created: {result['created']}")
    print(f"   Updated: {result['updated']}")
    
    # Clean up
    os.remove(csv_file_path)

    # Test uniqueness constraint
    print("\n\nTesting uniqueness constraint...")
    try:
        # Try to create a professional with an existing ID manually
        duplicate_prof = {
            "pid": "PROF001",
            "name": "Duplicate Professional",
            "role": "Tester",
            "level": "Junior",
            "is_template": False,
            "hourly_cost": 100.0
        }
        response = requests.post(f"{BASE_URL}/professionals/", json=duplicate_prof)
        if response.status_code == 500: # IntegrityError usually returns 500 unless handled
             print("✅ Uniqueness constraint verified (Server returned 500 as expected for IntegrityError)")
        else:
             print(f"⚠️ Unexpected status code for duplicate ID: {response.status_code}")
             print(response.text)
    except Exception as e:
        print(f"Error testing uniqueness: {e}")

if __name__ == "__main__":
    verify_csv_import()

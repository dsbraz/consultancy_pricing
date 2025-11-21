import requests
import os

# Test CSV import functionality
BASE_URL = "http://localhost:8000/api"

def test_csv_import():
    """Test importing professionals from CSV file"""
    
    # Create a test CSV file
    csv_content = """name,role,level,is_vacancy,hourly_cost
Test Professional 1,Desenvolvedor,Sênior,false,150.00
Test Professional 2,Designer,Pleno,false,120.00
Test Vacancy,Desenvolvedor,Júnior,true,80.00"""
    
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
            print(f"  - {prof['name']}: {prof['role']} ({prof['level']}) - R$ {prof['hourly_cost']}")
    
    # Test update by importing again with modified data
    print("\n\nTesting update functionality...")
    csv_content_updated = """name,role,level,is_vacancy,hourly_cost
Test Professional 1,Desenvolvedor,Pleno,false,130.00
Test Professional 2,Designer,Sênior,false,160.00"""
    
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

if __name__ == "__main__":
    test_csv_import()

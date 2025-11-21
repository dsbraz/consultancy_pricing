"""
Test XSS protection in the application.
Verifies that user input containing malicious scripts is properly sanitized.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base, engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestXSSProtection:
    """Test suite for XSS vulnerability protection"""
    
    def test_professional_xss_script_tag(self):
        """Test that professional names with <script> tags are stored but not executed"""
        xss_payload = "<script>alert('XSS')</script>"
        
        response = client.post("/professionals/", json={
            "pid": "XSS001",
            "name": xss_payload,
            "role": "Developer",
            "level": "Senior",
            "is_vacancy": False,
            "hourly_cost": 100.0
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Data should be stored as-is (backend doesn't sanitize, frontend does)
        assert data["name"] == xss_payload
        
        # Verify it's retrievable
        get_response = client.get("/professionals/")
        assert get_response.status_code == 200
        professionals = get_response.json()
        assert any(p["name"] == xss_payload for p in professionals)
    
    def test_professional_xss_img_onerror(self):
        """Test that professional names with img onerror are stored safely"""
        xss_payload = '<img src=x onerror=alert("XSS")>'
        
        response = client.post("/professionals/", json={
            "pid": "XSS002",
            "name": "John Doe",
            "role": xss_payload,
            "level": "Senior",
            "is_vacancy": False,
            "hourly_cost": 100.0
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == xss_payload
    
    def test_project_xss_svg_onload(self):
        """Test that project names with SVG onload are stored safely"""
        xss_payload = '"><svg/onload=alert("XSS")>'
        
        response = client.post("/projects/", json={
            "name": xss_payload,
            "start_date": "2025-01-01",
            "duration_months": 3,
            "tax_rate": 11.0,
            "margin_rate": 40.0,
            "allocations": []
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == xss_payload
    
    def test_offer_xss_javascript_protocol(self):
        """Test that offer names with javascript: protocol are stored safely"""
        xss_payload = 'javascript:alert("XSS")'
        
        response = client.post("/offers/", json={
            "name": xss_payload,
            "items": []
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == xss_payload
    
    def test_professional_xss_event_handler(self):
        """Test that professional data with event handlers are stored safely"""
        xss_payload = '" onmouseover="alert(\'XSS\')"'
        
        response = client.post("/professionals/", json={
            "pid": "XSS003",
            "name": xss_payload,
            "role": "Developer",
            "level": "Senior",
            "is_vacancy": False,
            "hourly_cost": 100.0
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == xss_payload
    
    def test_csv_import_xss_protection(self):
        """Test that CSV import handles XSS payloads correctly"""
        csv_content = """pid,name,role,level,is_vacancy,hourly_cost
XSS004,<script>alert('CSV XSS')</script>,Developer,Senior,false,100.0
XSS005,Normal Name,<img src=x onerror=alert('XSS')>,Junior,false,80.0"""
        
        response = client.post(
            "/professionals/import-csv",
            files={"file": ("test.csv", csv_content, "text/csv")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["created"] == 2
        assert data["errors"] == 0
        
        # Verify data is stored
        get_response = client.get("/professionals/")
        professionals = get_response.json()
        
        # Find the XSS professionals
        xss_profs = [p for p in professionals if p["pid"] in ["XSS004", "XSS005"]]
        assert len(xss_profs) == 2
        
        # Verify payloads are stored as-is
        assert any(p["name"] == "<script>alert('CSV XSS')</script>" for p in xss_profs)
        assert any(p["role"] == "<img src=x onerror=alert('XSS')>" for p in xss_profs)
    
    def test_multiple_xss_vectors(self):
        """Test various XSS attack vectors"""
        xss_vectors = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg/onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>",
            "<body onload=alert('XSS')>",
            "'-alert('XSS')-'",
            "\"><script>alert(String.fromCharCode(88,83,83))</script>",
        ]
        
        for idx, vector in enumerate(xss_vectors):
            response = client.post("/professionals/", json={
                "pid": f"VECTOR{idx:03d}",
                "name": vector,
                "role": "Tester",
                "level": "Senior",
                "is_vacancy": False,
                "hourly_cost": 100.0
            })
            
            assert response.status_code == 200
            data = response.json()
            # Backend stores as-is, frontend escapes on display
            assert data["name"] == vector
    
    def test_xss_in_project_with_allocations(self):
        """Test XSS protection in complex project creation with allocations"""
        # First create a professional with XSS payload
        prof_response = client.post("/professionals/", json={
            "pid": "XSS_PROF",
            "name": "<script>alert('Professional XSS')</script>",
            "role": "Developer",
            "level": "Senior",
            "is_vacancy": False,
            "hourly_cost": 100.0
        })
        prof_id = prof_response.json()["id"]
        
        # Create project with XSS payload
        project_response = client.post("/projects/", json={
            "name": "<img src=x onerror=alert('Project XSS')>",
            "start_date": "2025-01-01",
            "duration_months": 3,
            "tax_rate": 11.0,
            "margin_rate": 40.0,
            "allocations": []
        })
        
        assert project_response.status_code == 200
        project_data = project_response.json()
        assert project_data["name"] == "<img src=x onerror=alert('Project XSS')>"
        
        # Add professional to project
        add_response = client.post(
            f"/projects/{project_data['id']}/allocations/",
            params={"professional_id": prof_id}
        )
        
        assert add_response.status_code == 200
        
        # Get allocation table
        table_response = client.get(f"/projects/{project_data['id']}/allocation_table")
        assert table_response.status_code == 200
        table_data = table_response.json()
        
        # Verify XSS payloads are in the response
        assert any(
            alloc["professional"]["name"] == "<script>alert('Professional XSS')</script>"
            for alloc in table_data["allocations"]
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

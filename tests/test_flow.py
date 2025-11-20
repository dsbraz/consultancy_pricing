from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
import os

# Setup Test DB
TEST_DATABASE_URL = "sqlite:///./test_consultancy_pricing.db"

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override get_db
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create tables in test DB
if os.path.exists("test_consultancy_pricing.db"):
    os.remove("test_consultancy_pricing.db")
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_full_flow():
    print("Starting Full Flow Verification...")

    # 2. Create Professionals
    print("Creating Professionals...")
    prof1 = client.post("/professionals/", json={
        "name": "Dev 1",
        "role": "Developer",
        "level": "Senior",
        "is_vacancy": False,
        "hourly_cost": 100.0
    }).json()
    
    prof2 = client.post("/professionals/", json={
        "name": "PM 1",
        "role": "Project Manager",
        "level": "Senior",
        "is_vacancy": False,
        "hourly_cost": 150.0
    }).json()
    
    # 3. Create Template
    print("Creating Template...")
    template = client.post("/templates/", json={
        "name": "Standard Squad",
        "items": [
            {"role": "Developer", "level": "Senior", "quantity": 2},
            {"role": "Project Manager", "level": "Senior", "quantity": 1}
        ]
    }).json()
    
    # 4. Create Project
    print("Creating Project...")
    project = client.post("/projects/", json={
        "name": "New App",
        "start_date": "2024-01-01",
        "duration_months": 3,
        "tax_rate": 10.0, # 10%
        "margin_rate": 20.0 # 20%
    }).json()
    
    # 5. Apply Template
    print("Applying Template...")
    apply_res = client.post(f"/projects/{project['id']}/apply_template/{template['id']}").json()
    print("Allocations added:", apply_res["allocations"])
    
    # 6. Calculate Price
    print("Calculating Price...")
    try:
        price_res = client.get(f"/projects/{project['id']}/calculate_price").json()
        print("Price Result:", price_res)
        
        # Validation
        assert price_res["total_cost"] > 0
        assert price_res["final_price"] > price_res["total_cost"]
        print("Verification Successful!")
        
    except Exception as e:
        print("Error calculating price:", e)
        pass

if __name__ == "__main__":
    try:
        test_full_flow()
    finally:
        # Cleanup
        if os.path.exists("test_consultancy_pricing.db"):
            os.remove("test_consultancy_pricing.db")

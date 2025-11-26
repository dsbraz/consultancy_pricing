"""
Verification script for PNG export functionality.
Tests exporting a project to PNG format against running server.
"""

import requests
import sys
from io import BytesIO
from PIL import Image
import datetime

BASE_URL = "http://localhost:8080"


def verify_png_export():
    print("Starting PNG Export Verification...")

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    # Create a professional
    print("\n1. Creating professional...")
    prof_data = {
        "pid": f"TEST-PNG-{timestamp}",
        "name": "Maria Santos",
        "role": "Designer",
        "level": "Pleno",
        "is_template": False,
        "hourly_cost": 80.0,
    }
    prof_response = requests.post(f"{BASE_URL}/professionals/", json=prof_data)
    if prof_response.status_code != 200:
        print(f"❌ Failed to create professional: {prof_response.text}")
        sys.exit(1)
    professional = prof_response.json()
    print(f"✅ Professional created: {professional['name']}")

    # Create a project
    print("\n2. Creating project...")
    project_data = {
        "name": f"Proposta Teste PNG {timestamp}",
        "start_date": "2025-02-01",
        "duration_months": 3,
        "tax_rate": 11.0,
        "margin_rate": 40.0,
    }
    proj_response = requests.post(f"{BASE_URL}/projects/", json=project_data)
    if proj_response.status_code != 200:
        print(f"❌ Failed to create project: {proj_response.text}")
        sys.exit(1)
    project = proj_response.json()
    project_id = project["id"]
    print(f"✅ Project created: {project['name']}")

    # Add professional to project
    print("\n3. Adding professional to project...")
    add_prof_response = requests.post(
        f"{BASE_URL}/projects/{project_id}/allocations/?professional_id={professional['id']}"
    )
    if add_prof_response.status_code != 200:
        print(f"❌ Failed to add professional: {add_prof_response.text}")
        sys.exit(1)
    print("✅ Professional added to project")

    # Get allocation table to allocate hours
    print("\n4. Allocating hours...")
    alloc_table = requests.get(f"{BASE_URL}/projects/{project_id}/allocation_table")
    if alloc_table.status_code != 200:
        print(f"❌ Failed to get allocation table: {alloc_table.text}")
        sys.exit(1)
    alloc_data = alloc_table.json()

    # Update some weekly hours
    updates = []
    if len(alloc_data["allocations"]) > 0:
        allocation = alloc_data["allocations"][0]
        weekly_hours = allocation["weekly_hours"]

        # Set hours for first 3 weeks
        week_numbers = sorted(weekly_hours.keys(), key=int)[:3]
        for week_num_str in week_numbers:
            weekly_alloc = weekly_hours[week_num_str]
            available = weekly_alloc["available_hours"]
            hours_to_allocate = min(available * 0.75, 35.0)
            updates.append(
                {
                    "weekly_allocation_id": weekly_alloc["id"],
                    "hours_allocated": hours_to_allocate,
                }
            )

    if updates:
        update_response = requests.put(
            f"{BASE_URL}/projects/{project_id}/allocations", json=updates
        )
        if update_response.status_code != 200:
            print(f"❌ Failed to update allocations: {update_response.text}")
            sys.exit(1)
        print(f"✅ Hours allocated for {len(updates)} weeks")

    # Calculate pricing
    print("\n5. Calculating pricing...")
    calc_response = requests.get(f"{BASE_URL}/projects/{project_id}/calculate_price")
    if calc_response.status_code != 200:
        print(f"❌ Failed to calculate price: {calc_response.text}")
        sys.exit(1)
    pricing = calc_response.json()
    print(f"✅ Pricing calculated: R$ {pricing['final_price']:,.2f}")

    # Export to PNG
    print("\n6. Exporting to PNG...")
    export_response = requests.get(f"{BASE_URL}/projects/{project_id}/export_png")
    if export_response.status_code != 200:
        print(f"❌ Failed to export: {export_response.text}")
        sys.exit(1)

    if export_response.headers["content-type"] != "image/png":
        print(f"❌ Wrong content type: {export_response.headers['content-type']}")
        sys.exit(1)

    if "attachment" not in export_response.headers["content-disposition"]:
        print("❌ Missing attachment header")
        sys.exit(1)

    print("✅ PNG file downloaded")

    # Load and verify PNG content
    print("\n7. Verifying PNG content...")
    png_bytes = BytesIO(export_response.content)
    image = Image.open(png_bytes)

    # Verify image properties
    if image.format != "PNG":
        print(f"❌ Wrong image format: {image.format}")
        sys.exit(1)
    print(f"✅ Image format verified: {image.format}")

    width, height = image.size
    print(f"✅ Image dimensions: {width}x{height} pixels")

    if width < 800 or height < 600:
        print(f"❌ Image too small: {width}x{height}")
        sys.exit(1)
    print("✅ Image size adequate for commercial proposals")

    # Verify file size is reasonable (not too small, not too large)
    file_size = len(export_response.content)
    if file_size < 10000:  # Less than 10KB
        print(f"❌ File too small: {file_size} bytes")
        sys.exit(1)
    if file_size > 5000000:  # More than 5MB
        print(f"❌ File too large: {file_size} bytes")
        sys.exit(1)
    print(f"✅ File size reasonable: {file_size:,} bytes")

    # Optional: Save the file for manual inspection
    output_filename = f"test_proposta_{timestamp}.png"
    with open(output_filename, "wb") as f:
        f.write(export_response.content)
    print(f"✅ PNG saved for manual inspection: {output_filename}")

    print("\n" + "=" * 60)
    print("✅ PNG EXPORT VERIFICATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"\nPlease manually review the generated PNG file:")
    print(f"  {output_filename}")
    print("\nVerify that it contains:")
    print("  - Project name")
    print("  - Professional names, roles, and levels")
    print("  - Selling rates")
    print("  - Total hours per professional")
    print("  - Total project hours")
    print("  - Final price")
    print("  - Tax amount")


if __name__ == "__main__":
    try:
        verify_png_export()
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

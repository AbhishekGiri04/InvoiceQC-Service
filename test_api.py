"""Simple test script to demonstrate API functionality"""
import requests
import json

API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_validate_json():
    """Test JSON validation endpoint"""
    print("Testing /validate-json endpoint...")
    
    sample_invoices = [
        {
            "invoice_number": "TEST001",
            "invoice_date": "2024-05-22",
            "seller_name": "Test Seller Corp",
            "buyer_name": "Test Buyer Ltd",
            "currency": "EUR",
            "net_total": 100.0,
            "tax_amount": 19.0,
            "gross_total": 119.0,
            "line_items": []
        },
        {
            "invoice_number": "TEST002",
            "invoice_date": "2024-05-23",
            "seller_name": "Another Seller",
            "buyer_name": None,  # Missing buyer - should fail validation
            "currency": "USD",
            "net_total": 200.0,
            "tax_amount": 40.0,
            "gross_total": 240.0,
            "line_items": []
        }
    ]
    
    response = requests.post(
        f"{API_URL}/validate-json",
        json=sample_invoices
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_extract_and_validate():
    """Test PDF extraction and validation endpoint"""
    print("Testing /extract-and-validate endpoint...")
    
    # Upload a sample PDF
    with open("pdfs/sample_pdf_1.pdf", "rb") as f:
        files = {"files": ("sample_pdf_1.pdf", f, "application/pdf")}
        response = requests.post(
            f"{API_URL}/extract-and-validate",
            files=files
        )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

if __name__ == "__main__":
    print("=" * 60)
    print("Invoice QC Service API Test")
    print("=" * 60 + "\n")
    
    try:
        test_health()
        test_validate_json()
        test_extract_and_validate()
        
        print("=" * 60)
        print("All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API server.")
        print("Please start the server with: uvicorn invoice_qc.api.main:app --reload")
    except Exception as e:
        print(f"ERROR: {e}")

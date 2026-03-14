"""
API Test Script for CoreInventory FastAPI Backend
Run this after starting the server: python main.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Test results tracking
results = []

# Global token storage
auth_token = None


def get_headers():
    """Get headers with authorization if token exists"""
    headers = {"Content-Type": "application/json"}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    return headers


def test_endpoint(method, endpoint, data=None, description="", use_auth=False):
    """Test an API endpoint and print results"""
    url = f"{BASE_URL}{endpoint}"
    headers = get_headers() if use_auth else {"Content-Type": "application/json"}
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=5)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=5)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=5)
        else:
            response = requests.request(method, url, json=data, headers=headers, timeout=5)
        
        status = "✅ PASS" if response.status_code < 400 else "❌ FAIL"
        results.append({
            "status": status,
            "method": method,
            "endpoint": endpoint,
            "status_code": response.status_code,
            "description": description
        })
        
        print(f"\n{status} {method} {endpoint}")
        print(f"   Status Code: {response.status_code}")
        print(f"   Description: {description}")
        if response.text and len(response.text) < 200:
            try:
                print(f"   Response: {json.dumps(response.json(), indent=2)}")
            except:
                print(f"   Response: {response.text[:100]}")
        return response
        
    except requests.exceptions.ConnectionError:
        status = "❌ FAIL"
        results.append({
            "status": status,
            "method": method,
            "endpoint": endpoint,
            "status_code": "Connection Error",
            "description": description
        })
        print(f"\n{status} {method} {endpoint}")
        print(f"   Error: Cannot connect to server. Is it running on port 8000?")
        return None
    except Exception as e:
        status = "❌ FAIL"
        results.append({
            "status": status,
            "method": method,
            "endpoint": endpoint,
            "status_code": str(e),
            "description": description
        })
        print(f"\n{status} {method} {endpoint}")
        print(f"   Error: {str(e)}")
        return None


def run_all_tests():
    """Run all API endpoint tests"""
    print("=" * 60)
    print("COREINVENTORY API TEST SUITE")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print("Make sure the server is running: python main.py")
    print("=" * 60)
    
    # 1. Root Endpoint
    test_endpoint("GET", "/", description="Root endpoint - API health check")
    
    # 2. Auth Endpoints
    print("\n" + "-" * 60)
    print("AUTHENTICATION ENDPOINTS")
    print("-" * 60)
    
    # Signup
    signup_data = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "testpassword123"
    }
    test_endpoint("POST", "/api/auth/signup", data=signup_data, 
                  description="Register a new user")
    
    # Login
    login_data = {
        "email": "testuser@example.com",
        "password": "testpassword123"
    }
    login_response = test_endpoint("POST", "/api/auth/login", data=login_data, 
                  description="Login with credentials")
    
    # Extract JWT token from login response
    global auth_token
    if login_response and login_response.status_code == 200:
        try:
            login_json = login_response.json()
            auth_token = login_json.get("access_token")
            print(f"   JWT Token extracted: {auth_token[:20]}..." if auth_token else "   No token found")
        except:
            print("   Could not extract token from response")
    
    # 3. Warehouse Endpoints
    print("\n" + "-" * 60)
    print("WAREHOUSE ENDPOINTS")
    print("-" * 60)
    
    warehouse_data = {
        "name": "Main Warehouse",
        "location": "New York"
    }
    test_endpoint("POST", "/api/warehouses/add", data=warehouse_data, 
                  description="Add a new warehouse")
    
    test_endpoint("GET", "/api/warehouses/all", 
                  description="Get all warehouses")
    
    # 4. Product Endpoints
    print("\n" + "-" * 60)
    print("PRODUCT ENDPOINTS")
    print("-" * 60)
    
    product_data = {
        "name": "Wireless Mouse",
        "sku": "WM-001",
        "category": "Electronics",
        "unit": "pieces",
        "stock": 100
    }
    test_endpoint("POST", "/api/products/add", data=product_data, 
                  description="Add a new product")
    
    # Add another product
    product_data2 = {
        "name": "Mechanical Keyboard",
        "sku": "KB-001",
        "category": "Electronics",
        "unit": "pieces",
        "stock": 50
    }
    test_endpoint("POST", "/api/products/add", data=product_data2, 
                  description="Add another product")
    
    # Get all products
    response = test_endpoint("GET", "/api/products/all", 
                             description="Get all products")
    
    # Update product (if we have products)
    update_data = {
        "name": "Wireless Mouse Pro",
        "sku": "WM-001-PRO",
        "category": "Electronics",
        "unit": "pieces",
        "stock": 150
    }
    test_endpoint("PUT", "/api/products/update/1", data=update_data, 
                  description="Update product with ID 1")
    
    # 5. Stock Endpoints
    print("\n" + "-" * 60)
    print("STOCK ENDPOINTS")
    print("-" * 60)
    
    stock_data = {
        "product_id": 1,
        "warehouse_id": 1,
        "quantity": 50
    }
    test_endpoint("POST", "/api/stock/add", data=stock_data, 
                  description="Add stock for product in warehouse")
    
    test_endpoint("GET", "/api/stock/all", 
                  description="Get all stock entries")
    
    # 6. Receipt Endpoints
    print("\n" + "-" * 60)
    print("RECEIPT ENDPOINTS")
    print("-" * 60)
    
    receipt_data = {
        "product_id": 1,
        "warehouse_id": 1,
        "quantity": 20
    }
    test_endpoint("POST", "/api/receipts/add", data=receipt_data, 
                  description="Add receipt (increases stock)")
    
    test_endpoint("GET", "/api/receipts/all", 
                  description="Get all receipts")
    
    # 7. Delivery Endpoints
    print("\n" + "-" * 60)
    print("DELIVERY ENDPOINTS")
    print("-" * 60)
    
    delivery_data = {
        "product_id": 1,
        "warehouse_id": 1,
        "quantity": 5
    }
    test_endpoint("POST", "/api/deliveries/add", data=delivery_data, 
                  description="Add delivery (decreases stock)")
    
    test_endpoint("GET", "/api/deliveries/all", 
                  description="Get all deliveries")
    
    # 8. Transfer Endpoints
    print("\n" + "-" * 60)
    print("TRANSFER ENDPOINTS")
    print("-" * 60)
    
    # Add another warehouse for transfer
    warehouse_data2 = {
        "name": "Secondary Warehouse",
        "location": "Los Angeles"
    }
    test_endpoint("POST", "/api/warehouses/add", data=warehouse_data2, 
                  description="Add second warehouse for transfer")
    
    # Add stock to second warehouse
    stock_data2 = {
        "product_id": 1,
        "warehouse_id": 2,
        "quantity": 30
    }
    test_endpoint("POST", "/api/stock/add", data=stock_data2, 
                  description="Add stock to warehouse 2")
    
    # Transfer stock
    transfer_data = {
        "product_id": 1,
        "from_warehouse": 1,
        "to_warehouse": 2,
        "quantity": 10
    }
    test_endpoint("POST", "/api/transfers/transfer", data=transfer_data, 
                  description="Transfer stock between warehouses")
    
    test_endpoint("GET", "/api/transfers/all", 
                  description="Get all transfers")
    
    # 9. Stock Adjustments
    print("\n" + "-" * 60)
    print("STOCK ADJUSTMENT ENDPOINTS")
    print("-" * 60)
    
    adjustment_data = {
        "product_id": 1,
        "warehouse_id": 1,
        "counted_quantity": 75,
        "reason": "Physical count correction"
    }
    test_endpoint("POST", "/api/adjustments/add", data=adjustment_data, 
                  description="Create stock adjustment")
    
    test_endpoint("GET", "/api/adjustments/all", 
                  description="Get all adjustments")
    
    # 10. Stock Ledger
    print("\n" + "-" * 60)
    print("STOCK LEDGER ENDPOINTS")
    print("-" * 60)
    
    test_endpoint("GET", "/api/ledger/all", 
                  description="Get all ledger entries")
    
    test_endpoint("GET", "/api/ledger/product/1", 
                  description="Get ledger for product 1")
    
    # 11. Dashboard
    print("\n" + "-" * 60)
    print("DASHBOARD ENDPOINTS")
    print("-" * 60)
    
    test_endpoint("GET", "/api/dashboard/kpis", 
                  description="Get dashboard KPIs")
    
    test_endpoint("GET", "/api/dashboard/low-stock?threshold=20", 
                  description="Get low stock products")
    
    # 12. Search
    print("\n" + "-" * 60)
    print("SEARCH ENDPOINTS")
    print("-" * 60)
    
    test_endpoint("GET", "/api/search/products?q=laptop", 
                  description="Search products")
    
    test_endpoint("GET", "/api/search/categories", 
                  description="Get all categories")
    
    test_endpoint("GET", "/api/search/stock?warehouse_id=1", 
                  description="Filter stock by warehouse")
    
    test_endpoint("GET", "/api/search/movements/receipt", 
                  description="Get receipt movements")
    
    # 13. Profile
    print("\n" + "-" * 60)
    print("PROFILE ENDPOINTS")
    print("-" * 60)
    
    test_endpoint("GET", "/api/profile/me", 
                  description="Get user profile (requires auth)", use_auth=True)
    
    profile_update = {"name": "Updated User"}
    test_endpoint("PUT", "/api/profile/update", data=profile_update, 
                  description="Update user profile (requires auth)", use_auth=True)
    
    test_endpoint("POST", "/api/profile/logout", 
                  description="Logout user")
    
    # 14. Product Delete (run last)
    print("\n" + "-" * 60)
    print("DELETE ENDPOINTS")
    print("-" * 60)
    
    # Note: This might fail if foreign key constraints exist
    test_endpoint("DELETE", "/api/products/delete/2", 
                  description="Delete product with ID 2")
    
    # Print Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if "PASS" in r["status"])
    failed = sum(1 for r in results if "FAIL" in r["status"])
    
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed > 0:
        print("\nFailed Tests:")
        for r in results:
            if "FAIL" in r["status"]:
                print(f"  - {r['method']} {r['endpoint']}: {r['status_code']}")
    
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()

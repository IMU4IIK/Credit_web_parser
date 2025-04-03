"""
Test script to validate API endpoints for Credit Card Parser
"""
import requests
import json
import os

# Base URL for the API
BASE_URL = "http://localhost:5000/api"

def test_card_types():
    """Test the card-types endpoint"""
    print("\n=== Testing Card Types API ===")
    response = requests.get(f"{BASE_URL}/card-types")
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        print("Card Types:")
        for card_type in response.json():
            print(f"- {card_type}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def test_countries():
    """Test the countries endpoint"""
    print("\n=== Testing Countries API ===")
    response = requests.get(f"{BASE_URL}/countries")
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        print("Countries:")
        for country in response.json():
            print(f"- {country}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def test_validate_card():
    """Test the validate-card endpoint"""
    print("\n=== Testing Card Validation API ===")
    # Test a valid Visa card
    print("Testing valid Visa card...")
    valid_card = {"card_number": "4111111111111111"}
    response = requests.post(f"{BASE_URL}/validate-card", json=valid_card)
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        print(f"Result: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    
    # Test an invalid card
    print("\nTesting invalid card...")
    invalid_card = {"card_number": "1234567890123456"}
    response = requests.post(f"{BASE_URL}/validate-card", json=invalid_card)
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        print(f"Result: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def test_parse_endpoint():
    """Test the parse endpoint with a sample file"""
    print("\n=== Testing Parse API ===")
    if not os.path.exists("credit_cards.txt"):
        print("Error: Sample file 'credit_cards.txt' not found")
        return
    
    files = {'file': open('credit_cards.txt', 'rb')}
    data = {
        'country_filter': '',  # No country filter
        'card_type_filter': 'Visa'  # Filter for Visa cards only
    }
    
    print(f"Sending request with filters: {data}")
    response = requests.post(f"{BASE_URL}/parse", files=files, data=data)
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        result = response.json()
        print(f"Records found: {result['record_count']}")
        print(f"Filters applied: {result['filters_applied']}")
        print("Sample data (first record):")
        if result['data']:
            print(json.dumps(result['data'][0], indent=2))
        print(f"Data truncated: {result['truncated']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    print("Testing Credit Card Parser API Endpoints")
    print("=======================================")
    
    try:
        # Test all endpoints
        test_card_types()
        test_countries()
        test_validate_card()
        test_parse_endpoint()
        
        print("\n=======================================")
        print("API Testing Complete")
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the server. Make sure the application is running.")
    except Exception as e:
        print(f"\nError during testing: {str(e)}")
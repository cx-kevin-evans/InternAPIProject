import sys
import requests
import argparse
import time
import json

# Standard global variables
base_url = None
tenant_name = None
auth_url = None
iam_base_url = None
api_key = None
auth_token = None
token_expiration = 0 # initialize so we have to authenticate
debug = False

def generate_auth_url():
    global iam_base_url
        
    try:
        if debug:
            print("Generating authentication URL...")
        
        if iam_base_url is None:
            iam_base_url = base_url.replace("ast.checkmarx.net", "iam.checkmarx.net")
            if debug:
                print(f"Generated IAM base URL: {iam_base_url}")
        
        temp_auth_url = f"{iam_base_url}/auth/realms/{tenant_name}/protocol/openid-connect/token"
        
        if debug:
            print(f"Generated authentication URL: {temp_auth_url}")
        
        return temp_auth_url
    except AttributeError:
        print("Error: Invalid base_url provided")
        sys.exit(1)

def authenticate():
    global auth_token, token_expiration

    # if the token hasn't expired then we don't need to authenticate
    if time.time() < token_expiration - 60:
        if debug:
            print("Token still valid.")
        return
    
    if debug:
        print("Authenticating with API key...")
        
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        'grant_type': 'refresh_token',
        'client_id': 'ast-app',
        'refresh_token': api_key
    }
    
    try:
        response = requests.post(auth_url, headers=headers, data=data)
        response.raise_for_status()
        
        json_response = response.json()
        auth_token = json_response.get('access_token')
        if not auth_token:
            print("Error: Access token not found in the response.")
            sys.exit(1)
        
        expires_in = json_response.get('expires_in')
        
        if not expires_in:
            expires_in = 600

        token_expiration = time.time() + expires_in

        if debug:
            print("Authenticated successfully.")
      
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during authentication: {e}")
        sys.exit(1)

def get_user_activity():
    """
    Prompts the user to continue or exit the script.
    """
    active = ""
    while active not in ["yes", "no"]:
        active = input("Do you want to perform another action? (yes/no): ").lower()
        if active not in ["yes", "no"]:
            print("Invalid input. Please enter 'yes' or 'no'.")
    return active

def get_user_action():
    """
    Prompts the user to choose whether an action.
    """
    action = ""
    while action not in ["list", "create", "delete"]:
        action = input("Do you want to get a list of custom states, create a custom state, or delete a custom state? (list/create/delete): ")
        if action not in ["list", "create", "delete"]:
            print("Invalid input. Please enter 'list', 'create', or 'delete'.")
    return action

def get_state_list():
    # Get a list of the custom states via API
    url = f"{base_url}/api/custom-states/"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Accept": "application/json; version=1.0",
    }

    # make the API call
    try:
        response = requests.request("GET", url, headers=headers)

        if (response.status_code == 200):
            custom_states = response.json()
            if not custom_states:
                print("No custom states found.")
                return
            
            print("Custom States:")
            for state in custom_states:
                # print(f"ID: {state['id']}, Name: {state['name']}, Type: {state['type']}, IsAllowed: {state['isAllowed']}")
                print(state)
        else:
            print(f"Response status code: {response.status_code}")
            print("url: " + url)
            print("response text: " + response.text)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching custom states: {e}")
        if debug:
            print("Response status code:", response.status_code)
        sys.exit(1)


def debug_custom_state_creation():
    """Comprehensive debugging for the custom state creation API"""
    
    print("=== DEBUGGING CUSTOM STATE CREATION ===")
    
    # 1. First, let's verify the GET endpoint works
    print("\n1. Testing GET endpoint first...")
    get_url = f"{base_url}/api/custom-states/"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Accept": "application/json; version=1.0"
    }
    
    try:
        get_response = requests.get(get_url, headers=headers)
        print(f"GET Status: {get_response.status_code}")
        if get_response.status_code == 200:
            print("✓ GET endpoint works - API base URL and auth are correct")
        else:
            print(f"✗ GET endpoint failed: {get_response.text}")
            return
    except Exception as e:
        print(f"✗ GET request failed: {e}")
        return
    
    # 2. Debug the exact URL being constructed
    print(f"\n2. URL Construction Debug:")
    print(f"base_url: '{base_url}'")
    print(f"Full GET URL: '{get_url}'")
    
    # 3. Try different POST URL variations
    print(f"\n3. Testing POST URL variations...")
    
    post_urls = [
        f"{base_url}/api/custom-states",      # No trailing slash
        f"{base_url}/api/custom-states/",     # With trailing slash
        f"{base_url}/api/custom-states/create", # Explicit create endpoint
    ]
    
    payload = {"name": "debug-test"}
    post_headers = {
        "Authorization": f"Bearer {auth_token}",
        "Accept": "application/json; version=1.0",
        "Content-Type": "application/json"
    }
    
    for url in post_urls:
        print(f"\nTrying POST to: {url}")
        try:
            response = requests.post(url, headers=post_headers, json=payload)
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text[:150]}...")
            
            if response.status_code != 404:
                print(f"  *** NON-404 RESPONSE FOUND! ***")
                
        except Exception as e:
            print(f"  Error: {e}")
    
    # 4. Check if it's a permissions issue by examining response headers
    print(f"\n4. Detailed POST attempt analysis...")
    url = f"{base_url}/api/custom-states/"
    
    try:
        response = requests.post(url, headers=post_headers, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        # Check if server returned any helpful headers
        if 'Allow' in response.headers:
            print(f"Allowed Methods: {response.headers['Allow']}")
        if 'WWW-Authenticate' in response.headers:
            print(f"Auth Issue: {response.headers['WWW-Authenticate']}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # 5. Test with OPTIONS to see what methods are allowed
    print(f"\n5. Testing OPTIONS request...")
    try:
        options_response = requests.options(url, headers={"Authorization": f"Bearer {auth_token}"})
        print(f"OPTIONS Status: {options_response.status_code}")
        print(f"OPTIONS Headers: {dict(options_response.headers)}")
        if 'Allow' in options_response.headers:
            print(f"Allowed Methods: {options_response.headers['Allow']}")
    except Exception as e:
        print(f"OPTIONS Error: {e}")
    
    print(f"\n=== DEBUG COMPLETE ===")

def create_custom_state():
    # make a new custom state via API
    state_name = input("Enter the name of the new custom state: ")
    url = f"{base_url}/api/custom-states/"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Accept": "application/json; version=1.0",  # Fixed: Added version=1.0
        "Content-Type": "application/json"
    }
    payload = {
        "name": state_name
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        
        # Check for successful creation (201) or other success codes
        if response.status_code in [200, 201]:
            print(f"Custom state '{state_name}' created successfully.")
            # Print the response if it contains useful info
            try:
                result = response.json()
                if result:
                    print("Response:", result)
            except:
                pass
        else:
            print(f"Failed to create custom state. Response status code: {response.status_code}")
            print("Response text:", response.text)
            if debug:
                print(f"URL: {url}")
                print(f"Headers: {headers}")
                print(f"Payload: {payload}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while creating the custom state: {e}")
        sys.exit(1)

def delete_custom_state(state_id):
    url = f"{base_url}/api/custom-states/{state_id}"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Accept": "*/*; version=1.0"
    }

    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 204:
            print(f"Custom state with ID '{state_id}' deleted successfully.")
        elif response.status_code == 404:
            print(f"Custom state with ID '{state_id}' not found.")
        else:
            print(f"Failed to delete custom state. Response status code: {response.status_code}")
            if debug:
                print("Response text:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while deleting the custom state: {e}")
        if debug:
            print("Exception details:", e)
        sys.exit(1)
    print("Not implemented yet")

def main():
    global base_url
    global tenant_name
    global debug
    global auth_url
    global auth_token
    global iam_base_url
    global api_key

    # Parse and handle various CLI flags
    parser = argparse.ArgumentParser(description='Export a CxOne scan workflow as a CSV file')
    parser.add_argument('--base_url', required=True, help='Region Base URL')
    parser.add_argument('--iam_base_url', required=False, help='Region IAM Base URL')
    parser.add_argument('--tenant_name', required=True, help='Tenant name')
    parser.add_argument('--api_key', required=True, help='API key for authentication')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')

    # Set up various global variables
    args = parser.parse_args()
    base_url = args.base_url
    tenant_name = args.tenant_name
    debug = args.debug
    if args.iam_base_url:
        iam_base_url = args.iam_base_url
    api_key = args.api_key
    auth_url = generate_auth_url()

    authenticate()

    # main script logic
    active = "yes"
    while active == "yes":
        action = get_user_action()
        if action == "list":
            get_state_list()
        elif action == "create":
            debug_custom_state_creation() 
            #create_custom_state()
        elif action == "delete":
            delete_custom_state()
        active = get_user_activity()


if __name__ == "__main__":
    main()

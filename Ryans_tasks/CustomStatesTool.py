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

def create_custom_state():
    # make a new custom state via API
    state_name = input("Enter the name of the new custom state: ")
    url = f"{base_url}/api/custom-states"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Accept": "application/json",
    }
    payload = {
        "name": state_name
    }

    try:
        response = requests.request("POST", url, headers=headers, json=payload)
        if response.status_code == 201:
            print(f"Custom state '{state_name}' created successfully.")
        else:
            print(f"Failed to create custom state. Response status code: {response.status_code}")
            if debug:
                print("Response text:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while creating the custom state: {e}")
        if debug:
            print("Response status code:", response.status_code)
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
            create_custom_state()
        elif action == "delete":
            delete_custom_state()
        active = get_user_activity()


if __name__ == "__main__":
    main()

import argparse
import requests

def get_access_token(region, tenantName, apiKey):
    """
    Generates an access token using the provided API key.
    """
    if region == "":
        url = "https://iam.checkmarx.net/auth/realms/" + tenantName + "/protocol/openid-connect/token"
    else:
        url = "https://" + region + ".iam.checkmarx.net/auth/realms/" + tenantName + "/protocol/openid-connect/token"
    payload = 'grant_type=refresh_token&client_id=ast-app&refresh_token=' + apiKey 
    headers = {   'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code != 200:
        raise Exception(f"Failed to get access token: {response.text}")
        
    return response.json().get("access_token")

def get_user_action():
    """
    Prompts the user to choose whether to update fields in an existing project or create a new project.
    """
    action = ""
    while action not in ["update", "create"]:
        action = input("Do you want to update fields in an existing project or create a new project? (update/create): ")
        if action not in ["update", "create"]:
            print("Invalid input. Please enter 'update' or 'create'.")
    return action

def update_fields():
    print("not implemented yet")

def create_project():
    print("not implemented yet")

def main():
    # Obtain command line arguments
    parser = argparse.ArgumentParser(description='Export a CxOne scan workflow as a CSV file')
    parser.add_argument('--region', required=True, help='Region for the API endpoint (e.g., us, eu)')
    parser.add_argument('--tenant_name', required=True, help='Tenant name')
    parser.add_argument('--api_key', required=True, help='API key for authentication')

    # Set up various global variables
    args = parser.parse_args()
    region = args.region
    tenantName = args.tenant_name
    apiKey = args.api_key

    # Determine is user wants to update fields or create new project
    accessToken = get_access_token(region, tenantName, apiKey)
    action = get_user_action()
    if action == "update":
        update_fields()
    elif action == "create":
        create_project()
    else:
        print("Invalid action selected.")


if __name__ == "__main__":
    main()


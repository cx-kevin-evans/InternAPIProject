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

def update_fields(accessToken, region):
    """
    Updates fields in an existing project based on user input.
    """

    # fetch project ID + update fields
    projectId = input("Please provide the project ID. ")
    print("Now please provide the data for the fields you want to update.")
    print("WARNING: This will overwrite existing project tags and groups.")
    projectName = input("Project Name: ")
    repoUrl = input("Repository URL: ")
    mainBranch = input("Main Branch: ")

    # set up request components
    if region == "":
        url = f"https://ast.checkmarx.net/api/projects/{projectId}"
    else:
        url = f"https://{region}.ast.checkmarx.net/api/projects/{projectId}"

    headers = {
    "Authorization": f"Bearer {accessToken}",
    "Accept": "application/json; version=1.0",
    "Content-Type": "application/json; version=1.0"
    }

    payload = {
        "name": projectName,
        "repoUrl": repoUrl,
        "mainBranch": mainBranch
    }

    # make the request to update the project
    response = requests.request("PUT", url, headers=headers, json=payload)
    if response.status_code != 204:
        print(f"Failed to update project: {response.text}")
        print(f"Response status code: {response.status_code}")
    else:
        print(f"Project {projectName} updated successfully with ID: {projectId}")
        print("You can now run a scan on this project.")

def create_project(accessToken, region):
    """
    Creates a new project based on user input.
    """
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
        update_fields(accessToken, region)
    elif action == "create":
        create_project(accessToken, region)


if __name__ == "__main__":
    main()


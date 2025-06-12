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

def get_user_activity():
    """
    Prompts the user to continue or exit the script.
    """
    active = ""
    while active not in ["yes", "no"]:
        active = input("Do you want to update/create another project? (yes/no): ").lower()
        if active not in ["yes", "no"]:
            print("Invalid input. Please enter 'yes' or 'no'.")
    return active

def update_url_and_branch(accessToken, region, projectId, repoUrl, mainBranch):
    """
    Updates the repository URL and main branch of an existing project.
    """

    if region == "":
        url = "https://ast.checkmarx.net/api/configuration/project"
    else:
        url = f"https://{region}.ast.checkmarx.net/api/configuration/project"
    headers = {
    "Authorization": f"Bearer {accessToken}",
    "Accept": "application/json; version=1.0",
    "Content-Type": "application/json; version=1.0"
    }
    params = {
        "project-id" : projectId
    }
    payload = [
            {
                "key": "scan.config.microengines.repoUrl",
                "name": "repoUrl",
                "category": "microengines",
                "originLevel": "Project",
                "value": repoUrl,
                "valueType": "String",
                # "valueTypeParams": "string",
                "allowOverride": True
            },
            {
                "key": "scan.handler.git.branch",
                "name": "branch",
                "category": "git",
                "originLevel": "Project",
                "value": mainBranch,
                "valueType": "String",
                # "valueTypeParams": "string",
                "allowOverride": True
            }
    ]
    

    # make the request to update the url and branch
    response = requests.request("PATCH", url, headers=headers, params=params, json=payload)
    if response.status_code != 204:
        return False
    else:
        return True

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
    }

    # make the request to update the project
    response = requests.request("PUT", url, headers=headers, json=payload)
    if response.status_code != 204:
        print(f"Failed to update project: {response.text}")
        print(f"Response status code: {response.status_code}")
    else:
        if update_url_and_branch(accessToken, region, projectId, repoUrl, mainBranch):
            print(f"Project {projectName} updated successfully with ID: {projectId}")
            print("You can now run a scan on this project.")
        else:
            print(f"Failed to update project URL and branch.")

    # test printing: viewing configuration data
    # get_project_configuration(accessToken, region, projectId)
    

def create_project(accessToken, region):
    """
    Creates a new project based on user input.
    """

    # fetch project data from user
    print("Please provide the data for the new project.")
    projectName = input("Project Name: ")
    repoUrl = input("Repository URL: ")
    mainBranch = input("Main Branch: ")

    # set up request components
    if region == "":
        url = "https://ast.checkmarx.net/api/projects/"
    else:
        url = f"https://{region}.ast.checkmarx.net/api/projects/"
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

    # make the request to create the project
    response = requests.request("POST", url, headers=headers, json=payload)
    if response.status_code != 201: 
        print(f"Failed to create project: {response.text}")
        print(f"Response status code: {response.status_code}")
    else:
        projectId = response.json().get("id")
        if update_url_and_branch(accessToken, region, projectId, repoUrl, mainBranch):
            print(f"Project {projectName} created successfully with ID: {projectId}")
            print("You can now run a scan on this project.")
        else:
            print(f"Failed to update project URL and branch.")
        

def get_project_configuration(accessToken, region, projectId):
    """
    Test method to look at project configuration data.
    """
    if region == "":
        url = "https://ast.checkmarx.net/api/configuration/project"
    else:
        url = f"https://{region}.ast.checkmarx.net/api/configuration/project"
    headers = {
    "Authorization": f"Bearer {accessToken}",
    "Accept": "application/json; version=1.0",
    "Content-Type": "application/json; version=1.0"
    }
    params = {
        "project-id" : projectId
    }

    response = requests.request("GET", url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Failed to retrieve project configuration: {response.text}")
        print(f"Response status code: {response.status_code}")
    else:
        print("Project configuration retrieved successfully.")
        print("Configuration Data:", response.json())



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
    active = "yes"
    while active == "yes":
        action = get_user_action()
        if action == "update":
            update_fields(accessToken, region)
        elif action == "create":
            create_project(accessToken, region)
        active = get_user_activity()


if __name__ == "__main__":
    main()


import requests
import argparse

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

def randomize(list):
    """
    Returns random project from the list of projects.
    """
    import random
    if not list:
        raise Exception("No projects found in the tenant's account.")
    
    random_project = random.choice(list)
    print(f"Randomly selected project: {random_project['name']} (ID: {random_project['id']})")
    return random_project
    
def retrieve_projects(region, accessToken):
    """
    Retrieves a list of projects from the tenant's account.
    """
    if region == "":
        url = "https://ast.checkmarx.net/api/projects/"
    else:
        url = f"https://{region}.ast.checkmarx.net/api/projects/"

    headers = {
        'Authorization': f'Bearer {accessToken}',
        'Accept': '*/*; version=1.0'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve projects: {response.text}")

    # save the projects list from the response
    projects = response.json().get("projects")
    return projects


def main():
    # Obtain command line arguments
    parser = argparse.ArgumentParser(description='Performs scan on random project in tenant\'s account')
    parser.add_argument('--region', required=True, help='Region for the API endpoint (e.g., us, eu)')
    parser.add_argument('--tenant_name', required=True, help='Tenant name')
    parser.add_argument('--api_key', required=True, help='API key for authentication')


    # Set up various global variables
    args = parser.parse_args()
    region = args.region
    tenantName = args.tenant_name
    apiKey = args.api_key

    accessToken = get_access_token(region, tenantName, apiKey)
    list = retrieve_projects(region, accessToken)
    randomize(list)





if __name__ == "__main__":
    main()
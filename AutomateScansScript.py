import requests
import argparse
import random

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

def run_scan(
    region,
    access_token,
    project_id,
    scan_type="upload",
    handler=None,
    tags=None,
    config=None
):
    """
    Runs a scan on a Checkmarx AST project.

    Parameters:
        region (str): API region (e.g., 'us', 'eu', or '')
        access_token (str): JWT access token
        project_id (str): Project UUID
        scan_type (str): 'upload' or 'git'
        handler (dict): Handler info (for upload/git)
        tags (dict): Scan tags
        config (list): List of scan config dicts
    """
    if region == "":
        url = "https://ast.checkmarx.net/api/scans/"
    else:
        url = f"https://{region}.ast.checkmarx.net/api/scans/"

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': '*/*; version=1.0',
        'Content-Type': 'application/json'
    }

    if handler is None:
        handler = {}
    if tags is None:
        tags = {"ScanTag01": "", "ScanSeverity": "high"}
    if config is None:
        config = [
            {
                "type": "sast",
                "value": {
                    "incremental": "false",
                    "presetName": "Checkmarx Default",
                    "engineVerbose": "false"
                }
            },
            {
                "type": "sca",
                "value": {
                    "lastSastScanTime": "",
                    "exploitablePath": "false"
                }
            }
        ]

    scan_payload = {
        "project": {"id": project_id},
        "type": scan_type,
        "handler": handler,
        "tags": tags,
        "config": config
    }

    print("DEBUG: Scan payload:", scan_payload)
    response = requests.post(url, json=scan_payload, headers=headers)
    if response.status_code not in (200, 201):
        raise Exception(f"Failed to start scan: {response.status_code} {response.text}")
    return response.json()

def determine_scan_parameters(project):
    """
    Determines the scan_type and handler for a given project.
    Returns (scan_type, handler)
    """
    origin = project.get("origin")
    repo_url = project.get("repoUrl")
    main_branch = project.get("mainBranch")

    if origin and repo_url and main_branch:
        # Git-based project
        scan_type = "git"
        handler = {
            "repoUrl": repo_url,
            "branch": main_branch
            # Optionally: "credentials": {...}
        }
    else:
        # Default to upload (manual/migrated project)
        scan_type = "upload"
        handler = {}  # For upload, you need to provide an uploadurl if you want to scan new code
    return scan_type, handler

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
    project = randomize(list)
    scan_type, handler = determine_scan_parameters(project)
    scan_result = run_scan(region, accessToken, project["id"], scan_type=scan_type, handler=handler)
    print(scan_result)

if __name__ == "__main__":
    main()
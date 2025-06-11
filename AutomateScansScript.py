import requests
import argparse
import random

def get_access_token(region, tenantName, apiKey):
    if region == "":
        url = "https://iam.checkmarx.net/auth/realms/" + tenantName + "/protocol/openid-connect/token"
    else:
        url = "https://" + region + ".iam.checkmarx.net/auth/realms/" + tenantName + "/protocol/openid-connect/token"
    payload = 'grant_type=refresh_token&client_id=ast-app&refresh_token=' + apiKey 
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code != 200:
        raise Exception(f"Failed to get access token: {response.text}")
    return response.json().get("access_token")

def randomize(projects):
    if not projects:
        raise Exception("No projects found in the tenant's account.")
    random_project = random.choice(projects)
    print(f"Randomly selected project: {random_project['name']} (ID: {random_project['id']})")
    return random_project

def retrieve_projects(region, accessToken):
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
    projects = response.json().get("projects")
    return projects

def get_project_configuration(region, access_token, project_id):
    if region == "":
        url = f"https://ast.checkmarx.net/api/configuration/project/{project_id}"
    else:
        url = f"https://{region}.ast.checkmarx.net/api/configuration/project/{project_id}"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': '*/*; version=1.0'
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to get project configuration: {response.status_code} {response.text}")
    return response.json()

def filter_git_projects(region, access_token, projects):
    git_projects = []
    for p in projects:
        try:
            config = get_project_configuration(region, access_token, p["id"])
            repo_url = config.get("repoUrl")
            main_branch = config.get("mainBranch")
            if repo_url and repo_url.strip() and main_branch and main_branch.strip():
                p["_repoUrl"] = repo_url
                p["_mainBranch"] = main_branch
                git_projects.append(p)
        except Exception as e:
            print(f"Could not get config for project {p['name']}: {e}")
    return git_projects

def run_scan(region, access_token, project_id, scan_type, handler=None, tags=None, config=None):
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

def main():
    parser = argparse.ArgumentParser(description='Performs scan on random Git-based project in tenant\'s account')
    parser.add_argument('--region', required=True, help='Region for the API endpoint (e.g., us, eu)')
    parser.add_argument('--tenant_name', required=True, help='Tenant name')
    parser.add_argument('--api_key', required=True, help='API key for authentication')
    args = parser.parse_args()
    region = args.region
    tenantName = args.tenant_name
    apiKey = args.api_key

    accessToken = get_access_token(region, tenantName, apiKey)
    projects = retrieve_projects(region, accessToken)
    git_projects = filter_git_projects(region, accessToken, projects)
    if not git_projects:
        print("No Git-based projects with valid repo URL and main branch found in your account.")
        return
    project = randomize(git_projects)
    handler = {
        "repoUrl": project["_repoUrl"],
        "branch": project["_mainBranch"]
    }
    print("Detected Git-based project. Running scan...")
    scan_result = run_scan(region, accessToken, project["id"], scan_type="git", handler=handler)
    print("Scan started successfully!")
    print(scan_result)

if __name__ == "__main__":
    main()

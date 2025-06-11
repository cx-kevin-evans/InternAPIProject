import requests
import argparse
import random

def get_access_token(region, tenant_name, api_key):
    if region == "":
        url = f"https://iam.checkmarx.net/auth/realms/{tenant_name}/protocol/openid-connect/token"
    else:
        url = f"https://{region}.iam.checkmarx.net/auth/realms/{tenant_name}/protocol/openid-connect/token"
    payload = f'grant_type=refresh_token&client_id=ast-app&refresh_token={api_key}'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code != 200:
        raise Exception(f"Failed to get access token: {response.text}")
    return response.json().get("access_token")

def retrieve_projects(region, access_token):
    if region == "":
        url = "https://ast.checkmarx.net/api/projects/"
    else:
        url = f"https://{region}.ast.checkmarx.net/api/projects/"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': '*/*; version=1.0'
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve projects: {response.text}")
    return response.json().get("projects", [])

def get_project_config_params(region, access_token, project_id):
    if region == "":
        url = f"https://ast.checkmarx.net/api/configuration/project?project-id={project_id}"
    else:
        url = f"https://{region}.ast.checkmarx.net/api/configuration/project?project-id={project_id}"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': '*/*; version=1.0'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 404:
        return []
    if response.status_code != 200:
        raise Exception(f"Failed to get project config params for {project_id}: {response.status_code} {response.text}")
    return response.json()

def extract_repo_info_from_params(params):
    repo_url = None
    main_branch = None
    for param in params:
        if param.get("key") == "sourceSettings.repositoryUrl":
            repo_url = param.get("value")
        elif param.get("key") == "sourceSettings.branch":
            main_branch = param.get("value")
    return repo_url, main_branch

def run_scan(region, access_token, project_id, scan_type="git", handler=None, tags=None, config=None):
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
    parser = argparse.ArgumentParser(description='Performs scan on random project in tenant\'s account')
    parser.add_argument('--region', required=True, help='Region for the API endpoint (e.g., us, eu)')
    parser.add_argument('--tenant_name', required=True, help='Tenant name')
    parser.add_argument('--api_key', required=True, help='API key for authentication')
    args = parser.parse_args()
    region = args.region
    tenant_name = args.tenant_name
    api_key = args.api_key

    access_token = get_access_token(region, tenant_name, api_key)
    projects = retrieve_projects(region, access_token)
    if not projects:
        print("No projects found in tenant account.")
        return

    project = random.choice(projects)
    print(f"Randomly selected project: {project['name']} (ID: {project['id']})")

    params = get_project_config_params(region, access_token, project["id"])
    repo_url, main_branch = extract_repo_info_from_params(params)
    print(f"Repo URL: {repo_url}")
    print(f"Main Branch: {main_branch}")

    if repo_url and main_branch:
        handler = {
            "repoUrl": repo_url.strip(),
            "branch": main_branch.strip()
        }
        try:
            scan_result = run_scan(region, access_token, project["id"], scan_type="git", handler=handler)
            print("Scan started successfully!")
            print(scan_result)
        except Exception as e:
            print(f"Failed to start scan: {e}")
    else:
        print("No valid repository URL or branch found for this project. Cannot run a Git scan.")

if __name__ == "__main__":
    main()

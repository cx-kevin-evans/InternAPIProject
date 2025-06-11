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
    if response.status_code == 404:
        return None
    if response.status_code != 200:
        raise Exception(f"Failed to get project configuration for {project_id}: {response.status_code} {response.text}")
    return response.json()

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
    payload = {
        "project": {"id": project_id},
        "type": scan_type,
        "handler": handler,
        "tags": tags,
        "config": config
    }
    print("DEBUG: Scan payload:", payload)
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code not in (200, 201):
        raise Exception(f"Failed to start scan: {response.status_code} {response.text}")
    return response.json()

def main():
    parser = argparse.ArgumentParser(description='Pick a random project and attempt a scan if SCM info is present.')
    parser.add_argument('--region', required=True, help='API region (e.g., us, eu)')
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

    config = get_project_configuration(region, access_token, project["id"])
    if config:
        repo_url = config.get("repoUrl")
        main_branch = config.get("mainBranch")
        print(f"  Repo URL: {repo_url}")
        print(f"  Main Branch: {main_branch}")
        if repo_url and repo_url.strip() and main_branch and main_branch.strip():
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
            print("No valid repo URL or branch for this project. Cannot run a Git scan.")
    else:
        print("No SCM configuration found (likely manual/upload project). Cannot run a Git scan.")

if __name__ == "__main__":
    main()

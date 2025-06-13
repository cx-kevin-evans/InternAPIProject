import requests
import argparse

scanId = None
scanEngines = None
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

def get_most_recent_scan(accessToken, region, projectName):
    """
    Grabs the most recent scan for a given project.
    """

    # set up request for scan list
    if region == "":
        url = "https://ast.checkmarx.net/api/scans/"
    else:
        url = f"https://{region}.ast.checkmarx.net/api/scans/"
    headers = {
        "Authorization": f"Bearer {accessToken}",
        "Accept": "application/json; version=1.0",
        "Content-Type": "application/json; version=1.0"
    }
    params = {
        "field" : ["project-names"],
        "project-names" : [projectName]
    }

    response = requests.request("GET", url, headers=headers, params=params)

    #print(response.text)

    if response.status_code != 200:
        print(f"Failed to get scans: {response.text}")
    else:
        scanId = response.json()["scans"][0]["id"]
        print(scanId)
        scanEngines = response.json()["scans"][0]["engines"]

import requests

def get_sast_similarity_ids(region, access_token, scan_id):
    if region == "":
        url = f"https://ast.checkmarx.net/api/sast-results/"
    else:
        url = f"https://{region}.ast.checkmarx.net/api/sast-results/"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'

    }
    params = {
        "scan-id": scan_id
    }
    response = requests.request("GET", url, params=params, headers=headers)
    data = response.json()
    print(data)
    #results = data.get("results", [])
    #similarity_ids = [r["similarityId"] for r in results if "similarityId" in r]
    #return similarity_ids


def main():
    # Obtain command line arguments
    parser = argparse.ArgumentParser(description='Export a CxOne scan workflow as a CSV file')
    parser.add_argument('--region', required=True, help='Region for the API endpoint (e.g., us, eu)')
    parser.add_argument('--tenant_name', required=True, help='Tenant name')
    parser.add_argument('--api_key', required=True, help='API key for authentication')
    parser.add_argument('--project_name', required=True, help='Project name')
    parser.add_argument('--project_id', required=False, help='Project ID')

    # Set up various global variables
    args = parser.parse_args()
    region = args.region
    tenantName = args.tenant_name
    apiKey = args.api_key
    projectName = args.project_name
    projectId = args.project_id

    # triage scan results
    accessToken = get_access_token(region, tenantName, apiKey)

    # steps: 
    # retrieve project id from user
    # get scan id (most recent)
    # get all engines used in most recent scan
    # get a similarity id for each scan engine
    # change predicate in each scan engine
    # triage results

    get_most_recent_scan(accessToken, region, projectName)
    get_sast_similarity_ids(region, accessToken, scanId)

if __name__ == "__main__":
    main()
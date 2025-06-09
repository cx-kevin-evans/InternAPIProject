import requests
import argparse
import time

def get_access_token(region, tenantName, apiKey):
    """
    Generates an access token using the provided API key.
    """
    url = "https://" + region + ".iam.checkmarx.net/auth/realms/" + tenantName + "/protocol/openid-connect/token"
    payload = 'grant_type=refresh_token&client_id=ast-app&refresh_token=' + apiKey 
    headers = {   'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code != 200:
        raise Exception(f"Failed to get access token: {response.text}")
        
    return response.json().get("access_token")

def generate_sbom_report(scanId, fileFormat, accessToken, region):
    """
    Generates a Software Bill of Materials (SBOM) report for a given scan ID.
    """
    url = "https://" + region + ".ast.checkmarx.net/api/sca/export/requests"
    payload = {
        "scanId": scanId,
        "fileFormat": fileFormat,
        "exportParameters": {
            "hideDevAndTestDependencies": True,
            "showOnlyEffectiveLicenses": False
        }
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/plain, application/json, text/json",
        "Authorization": f'Bearer {accessToken}'
    }

    response = requests.request("POST", url, json=payload, headers=headers) 

    # save the export id from the response
    print(response.text)
    data = response.json().get("exportID")
    return data

def check_report_status(exportId, accessToken, region, maxRetries, baseDelay):
    """
    Checks the status of the report using the export ID.
    """
    
    # make the request to check the report status
    url = "https://" + region + ".ast.checkmarx.net/api/sca/export/requests"
    params = {
        "exportId": exportId
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/plain, application/json, text/json",
        "Authorization": f'Bearer {accessToken}'
    }

    for attempt in range(maxRetries):
        try:
            response = requests.request("GET", url, params=params, headers=headers)

            if response.status_code == 200:
                print("Successfully checked report status.")
                return response
            
            print(f"Attempt {attempt + 1} failed with status {response.status_code}, retrying...")
            print(f"Respose content: {response.text}")
        
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
        
        #exponential backoff delay
        sleepTime = baseDelay * (2 ** attempt)
        print(f"Waiting {sleepTime} seconds before retrying...")
        time.sleep(sleepTime)

    print("Max retries reached. Could not check report status.")
    return False

def download_sbom_report(exportId, accessToken, max_attempts=10):
    status_url = "https://us.ast.checkmarx.net/api/sca/export/requests"
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/plain, application/json, text/json",
        "Authorization": f'Bearer {accessToken}'
    }
    params = {"exportId": exportId}
    wait_time = 2  # seconds

    for attempt in range(max_attempts):
        response = requests.get(status_url, params=params, headers=headers)
        print(response.text)
        if response.status_code != 200:
            print(f"Failed to check report status: {response.text}")
            time.sleep(wait_time)
            wait_time = min(wait_time * 2, 60)  # exponential backoff, max 60s
            continue

        data = response.json()
        status = data.get("status")
        file_url = data.get("fileUrl")

        if status == "Completed" and file_url:
            filename = file_url.split("/")[-2]  # Or use another method to name file
            file_response = requests.get(file_url)
            if file_response.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(file_response.content)
                print(f"Downloaded file: {filename}")
                return
            else:
                print(f"Failed to download file from fileUrl: {file_response.status_code}")
                return
        elif status in ("Failed", "Error"):
            print(f"Report generation failed: {data}")
            return
        else:
            print(f"Report not ready yet (status: {status}). Waiting {wait_time}s...")
            time.sleep(wait_time)
            wait_time = min(wait_time * 2, 60)  # exponential backoff

    print("Failed to retrieve report status and download report after many attempts.")
    
def main():
    # Obtain command line arguments
    parser = argparse.ArgumentParser(description='Export a CxOne scan workflow as a CSV file')
    parser.add_argument('--region', required=True, help='Region for the API endpoint (e.g., us, eu)')
    parser.add_argument('--tenant_name', required=True, help='Tenant name')
    parser.add_argument('--api_key', required=True, help='API key for authentication')
    parser.add_argument('--scan_id', required=True, help='Scan ID for the report')
    parser.add_argument('--format', required=True, help='File format of the SBOM report (e.g., CycloneDxJson, SpdxJson, or CycloneDxXml)')


    # Set up various global variables
    args = parser.parse_args()
    region = args.region
    tenantName = args.tenant_name
    apiKey = args.api_key
    scanId = args.scan_id
    fileFormat = args.format

    accessToken = get_access_token(region, tenantName, apiKey)
    exportId = generate_sbom_report(scanId, fileFormat, accessToken, region)
    data = check_report_status(exportId, accessToken, region, 5, 1)
    if data:
        download_sbom_report(data)
    else:
        print("Failed to retrieve the report status and download the report.")
    


if __name__ == "__main__":
    main()





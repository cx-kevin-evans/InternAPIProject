import requests
import argparse

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

# Generating a new access token via the API key
url = "https://" + region + ".iam.checkmarx.net/auth/realms/" + tenantName + "/protocol/openid-connect/token"

payload = 'grant_type=refresh_token&client_id=ast-app&refresh_token=' + apiKey 
headers = {   'Content-Type': 'application/x-www-form-urlencoded'
}

response = requests.request("POST", url, headers=headers, data=payload)

data = response.json()
if ("access_token" not in response.text):
    print(response.text)
else:
    accessToken = data["access_token"]

# print(accessToken) 

# access token has been retreived and stored in accessToken 

url = "https://us.ast.checkmarx.net/api/sca/export/requests"

payload = {
    # hard coded scan id for scratch, in real use add to argeparser***
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
data = response.json()
exportId = data["exportId"]

# make the request to check the report status
params = {
    "exportId": exportId
}

response = requests.request("GET", url, params=params, headers=headers)
print(response.text)
data = response.json()
url = data["fileUrl"]
filename = url.split("/")[-2]  # Automatically extract filename from URL

response = requests.request("GET", url, headers=headers)

if response.status_code == 200:
    with open(filename, "wb") as f:
        f.write(response.content)
    print(f"Downloaded file: {filename}")
else:
    print(f"Failed to download file. Status code: {response.status_code}")








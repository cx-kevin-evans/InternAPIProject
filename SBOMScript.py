import requests
import argparse

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

# # Generating a new access token via the API key
url = "https://" + region + ".iam.checkmarx.net/auth/realms/" + tenantName + "/protocol/openid-connect/token"

payload = 'grant_type=refresh_token&client_id=ast-app&refresh_token=' + apiKey 
headers = {   'Content-Type': 'application/x-www-form-urlencoded'
}

response = requests.request("POST", url, headers=headers, data=payload)

data = response.json()
accessToken = data["access_token"]

print(accessToken)

new_url = "https://" + region + ".ast.checkmarx.net/api/sca/export/file-formats"  
headers = {
    'Authorization': f'Bearer {accessToken}',
    'Accept': 'application/json'
}
data = {
    "format": "SBOM",
    "hideDevAndTestDependencies": True,   # or False as needed
    "showOnlyEffectiveLicenses": False    # or True as needed
}

response = requests.post(url, headers=headers, json=data)
print(response.status_code)
print(response.text)


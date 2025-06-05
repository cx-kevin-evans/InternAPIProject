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

# Generating a new access token via the API key
url = f"https://{region}.iam.checkmarx.net/auth/realms/{tenantName}/protocol/openid-connect/token"

# CHANGE: Use a dict for form data, not a string
payload = {
    'grant_type': 'refresh_token',
    'client_id': 'ast-app',
    'refresh_token': apiKey
}
headers = {'Content-Type': 'application/x-www-form-urlencoded'}

# Use requests.post and pass payload as data
response = requests.post(url, headers=headers, data=payload)

data = response.json()
accessToken = data["access_token"]

print(accessToken)

# Now use the access token for the next request
new_url = f"https://{region}.ast.checkmarx.net/api/sca/export/file-formats"
headers = {
    'Authorization': f'Bearer {accessToken}',
    'Accept': 'application/json'
}
export_body = {
    "format": "SBOM",  # This is the key for SBOM export
    "hideDevAndTestDependencies": True,    # or False, as you need
    "showOnlyEffectiveLicenses": False     # or True, as you need
}

response = requests.get(new_url, headers=headers)  # Use GET for file formats
print(response.status_code)
print(response.text)

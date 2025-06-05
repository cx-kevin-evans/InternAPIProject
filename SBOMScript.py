import requests
import argparse

# Obtain command line arguments
parser = argparse.ArgumentParser(description='Export a CxOne SBOM')
parser.add_argument('--region', required=True, help='Region for the API endpoint (e.g., us, eu)')
parser.add_argument('--tenant_name', required=True, help='Tenant name')
parser.add_argument('--api_key', required=True, help='API key for authentication')

args = parser.parse_args()
region = args.region
tenantName = args.tenant_name
apiKey = args.api_key

# 1. Get Access Token
token_url = f"https://{region}.iam.checkmarx.net/auth/realms/{tenantName}/protocol/openid-connect/token"
payload = {
    'grant_type': 'refresh_token',
    'client_id': 'ast-app',
    'refresh_token': apiKey
}
headers = {'Content-Type': 'application/x-www-form-urlencoded'}

response = requests.post(token_url, headers=headers, data=payload)
response.raise_for_status()
accessToken = response.json()["access_token"]

# 2. Export SBOM with parameters
export_url = f"https://{region}.ast.checkmarx.net/api/sca/export"
headers = {
    'Authorization': f'Bearer {accessToken}',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}
export_body = {
    "format": "SBOM",  # This is the key for SBOM export
    "hideDevAndTestDependencies": True,    # or False, as you need
    "showOnlyEffectiveLicenses": False     # or True, as you need
}

response = requests.post(export_url, headers=headers, json=export_body)
print(response.status_code)
print(response.text)

import requests
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Export a CxOne SBOM')
parser.add_argument('--region', required=True, help='API region (e.g., us, eu)')
parser.add_argument('--tenant_name', required=True, help='Tenant name')
parser.add_argument('--api_key', required=True, help='API key for authentication')
parser.add_argument('--format', default='CycloneDxJson', help='SBOM format (CycloneDxJson, CycloneDxXml, SpdxJson)')
args = parser.parse_args()

# 1. Get an access token
token_url = f"https://{args.region}.iam.checkmarx.net/auth/realms/{args.tenant_name}/protocol/openid-connect/token"
payload = {
    'grant_type': 'refresh_token',
    'client_id': 'ast-app',
    'refresh_token': args.api_key
}
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
response = requests.post(token_url, headers=headers, data=payload)
response.raise_for_status()
access_token = response.json()['access_token']

# 2. Export SBOM
export_url = f"https://{args.region}.ast.checkmarx.net/api/sca/export/requests"
headers = {
    'Authorization': f'Bearer {access_token}',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}
export_body = {
    "fileFormat": args.format,
    "scanId": "e1db3f80-73fc-4e94-a5f0-634cbbfa9f55",  # Replace with your actual scan ID
    # Add other parameters as needed, e.g., scanId, projectId, etc.
}
response = requests.post(export_url, headers=headers, json=export_body)
print(response.status_code)
print(response.text)

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

# print(response.text)

data = response.json()
accessToken = data["access_token"]

# print(accessToken)

# Audit trail script portion:
# Set your variables
audit_url = "https://" + region + ".ast.checkmarx.net/api/audit/"  
headers = {
    'Authorization': f'Bearer {accessToken}',
    'Accept': 'application/json'
}
# Make the GET request
try:
    response = requests.get(audit_url, headers=headers)
    print("Audit API response:", response.json())
    # Check for status 200
    if response.status_code == 200:
        print("Audit trail status is 200")
    else:
        print(f"Unexpected status: {response.status_code}")
except requests.RequestException as err:
    print("Request error:", err)
except Exception as e:
    print("Error parsing response:", e)


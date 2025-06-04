import requests

# Custom script variables
region = "us"
tenantName = "evanskevin-sedemo"
apiKey = "eyJhbGciOiJIUzUxMiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI5NjI2Zjc1Zi1kZTAwLTQwOTQtYjNjNC0wZjk3ZWZkOTA2YzUifQ.eyJpYXQiOjE3NDg0NjMzMDgsImp0aSI6IjhiZWZmYzkwLTQzMmMtNGQwMC1hNTM3LTA0NDhhY2Y0YmYxMyIsImlzcyI6Imh0dHBzOi8vdXMuaWFtLmNoZWNrbWFyeC5uZXQvYXV0aC9yZWFsbXMvZXZhbnNrZXZpbi1zZWRlbW8iLCJhdWQiOiJodHRwczovL3VzLmlhbS5jaGVja21hcngubmV0L2F1dGgvcmVhbG1zL2V2YW5za2V2aW4tc2VkZW1vIiwic3ViIjoiNDFjZmFhMzEtMjVkNC00NGFjLThkNDMtMTk3MzQxZGY5MzBhIiwidHlwIjoiT2ZmbGluZSIsImF6cCI6ImFzdC1hcHAiLCJzaWQiOiIyYTQ3NjgwMi0wODRmLTQ3MGUtYjAzNS04ZjMwZjMzMzUyYTMiLCJzY29wZSI6ImFzdC1hcGkgZW1haWwgcHJvZmlsZSBncm91cHMgaWFtLWFwaSByb2xlcyBvZmZsaW5lX2FjY2VzcyJ9.DQphOxHwY0epHyKPyOymzzBP_mBf50vvyNT5zipAfSOoUHXPHb0O_7DhgcbZPNT-70oSqM0kPIrGXsmV_pszww"


# Generating a new access token via the API key
url = "https://" + region + ".iam.checkmarx.net/auth/realms/" + tenantName + "/protocol/openid-connect/token"

payload = 'grant_type=refresh_token&client_id=ast-app&refresh_token=' + apiKey 
headers = {
  'Content-Type': 'application/x-www-form-urlencoded'
}

response = requests.request("POST", url, headers=headers, data=payload)

# print(response.text)

data = response.json()
accessToken = data["access_token"]

# print(accessToken)


# Audit trail script portion:
# Set your variables
audit_url = "https://" + region + ".ast.checkmarx.net/api/audit"  

headers = {
    'Authorization': f'Bearer {accessToken}',
    'Accept': 'application/json'
}
print("check")
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


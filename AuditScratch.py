import requests
import argparse
import csv

# Obtain command line arguments
parser = argparse.ArgumentParser(description='Export CxOne login events as a CSV file')
parser.add_argument('--region', required=True, help='Region for the API endpoint (e.g., us, eu)')
parser.add_argument('--tenant_name', required=True, help='Tenant name')
parser.add_argument('--api_key', required=True, help='API key for authentication')
parser.add_argument('--output', default='logins.csv', help='Output CSV file')

args = parser.parse_args()
region = args.region
tenantName = args.tenant_name
apiKey = args.api_key

# Generate a new access token via the API key
url = f"https://{region}.iam.checkmarx.net/auth/realms/{tenantName}/protocol/openid-connect/token"
payload = f'grant_type=refresh_token&client_id=ast-app&refresh_token={apiKey}'
headers = {'Content-Type': 'application/x-www-form-urlencoded'}

response = requests.post(url, headers=headers, data=payload)
data = response.json()
accessToken = data["access_token"]

# Audit trail script portion:
audit_url = f"https://{region}.ast.checkmarx.net/api/audit/"
headers = {
    'Authorization': f'Bearer {accessToken}',
    'Accept': 'application/json'
}

try:
    response = requests.get(audit_url, headers=headers)
    audit_data = response.json()
    if response.status_code == 200:
        print("Audit trail status is 200")
    else:
        print(f"Unexpected status: {response.status_code}")
except requests.RequestException as err:
    print("Request error:", err)
    exit(1)
except Exception as e:
    print("Error parsing response:", e)
    exit(1)

login_events = []

def extract_username(event):
    # Safely extract username from event["data"]["userName"], if present
    data = event.get("data", {})
    if isinstance(data, dict):
        return data.get("userName")
    return None

# 3. Process today's events
for event in audit_data.get("events", []):
    if event.get("actionType", "").lower() == "login":
        username = extract_username(event)
        login_events.append([
            event.get("eventDate"),
            event.get("actionUserId"),
            username
        ])

# 4. Process previous days' events from links
for link in audit_data.get("links", []):
    log_url = link.get("url")
    if log_url:
        log_response = requests.get(log_url, headers=headers)
        log_response.raise_for_status()
        log_json = log_response.json()
        if isinstance(log_json, list):
            day_events = log_json
        elif isinstance(log_json, dict) and "events" in log_json:
            day_events = log_json["events"]
        else:
            day_events = []
        for event in day_events:
            if event.get("actionType", "").lower() == "login":
                username = extract_username(event)
                login_events.append([
                    event.get("eventDate"),
                    event.get("actionUserId"),
                    username
                ])

# 5. Write to CSV (with username column)
with open(args.output, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["eventDate", "actionUserId", "username"])
    writer.writerows(login_events)

print(f"Exported {len(login_events)} login events to {args.output}")

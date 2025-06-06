import requests
import argparse
import csv

def flatten_event(event):
    """
    Flattens the event and its 'data' sub-dictionary for CSV output.
    Maps 'data.id' -> 'details_id', 'data.status' -> 'details_status', etc.
    """
    flat = {}
    # Top-level fields
    flat["EventDate"] = event.get("eventDate")
    flat["actionType"] = event.get("actionType")
    flat["actionUserId"] = event.get("actionUserId")
    flat["auditResource"] = event.get("auditResource")
    flat["eventDate"] = event.get("eventDate")  # duplicate for your requested columns
    flat["eventType"] = event.get("eventType")
    flat["ipAddress"] = event.get("ipAddress")
    # Nested 'data' fields
    data = event.get("data", {})
    if isinstance(data, dict):
        flat["details_id"] = data.get("id")
        flat["details_status"] = data.get("status")
        flat["details_username"] = data.get("username")
    else:
        flat["details_id"] = None
        flat["details_status"] = None
        flat["details_username"] = None
    return flat

def get_all_events(audit_data):
    """
    Returns all events (flattened) from the current day's audit data.
    """
    return [flatten_event(e) for e in audit_data.get("events", [])]

def get_all_events_from_links(links, headers):
    """
    Downloads and returns all events (flattened) from previous days' logs.
    """
    events = []
    for link in links:
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
            events.extend([flatten_event(e) for e in day_events])
    return events

def write_events_to_csv(events, output_file):
    """
    Writes the selected fields from all events to a CSV file.
    """
    fieldnames = [
        "EventDate",
        "actionType",
        "actionUserId",
        "auditResource",
        "details_id",
        "details_status",
        "details_username",
        "eventDate",
        "eventType",
        "ipAddress"
    ]
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for event in events:
            writer.writerow(event)

def main():
    parser = argparse.ArgumentParser(description='Export CxOne audit events as a CSV file')
    parser.add_argument('--region', required=True, help='Region for the API endpoint (e.g., us, eu)')
    parser.add_argument('--tenant_name', required=True, help='Tenant name')
    parser.add_argument('--api_key', required=True, help='API key for authentication')
    parser.add_argument('--output', default='audit_trail_export.csv', help='Output CSV file')
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

    # Gather all events (today + previous days)
    all_events = get_all_events(audit_data)
    all_events += get_all_events_from_links(audit_data.get("links", []), headers)

    # Write to CSV
    write_events_to_csv(all_events, args.output)
    print(f"Exported {len(all_events)} events to {args.output}")

if __name__ == "__main__":
    main()

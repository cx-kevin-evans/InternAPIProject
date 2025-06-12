import requests
import argparse
import csv
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from openpyxl import Workbook
import os

def format_event_date(dt_str):
    if not dt_str:
        return ""
    if '.' in dt_str:
        base, frac = dt_str.split('.')
        frac = frac.rstrip('Z')[:6]
        dt_str_fixed = f"{base}.{frac}Z"
    else:
        dt_str_fixed = dt_str
    dt = datetime.strptime(dt_str_fixed, "%Y-%m-%dT%H:%M:%S.%fZ")
    return dt.strftime("%m/%d/%Y %H:%M")

def parse_iso_event_date(dt_str):
    """Parses ISO event date string to datetime object for filtering."""
    if not dt_str:
        return None
    if '.' in dt_str:
        base, frac = dt_str.split('.')
        frac = frac.rstrip('Z')[:6]
        dt_str_fixed = f"{base}.{frac}Z"
    else:
        dt_str_fixed = dt_str
    return datetime.strptime(dt_str_fixed, "%Y-%m-%dT%H:%M:%S.%fZ")

def flatten_event(event):
    flat = {}
    flat["EventDate"] = format_event_date(event.get("eventDate"))
    flat["actionType"] = event.get("actionType")
    flat["actionUserId"] = event.get("actionUserId")
    flat["auditResource"] = event.get("auditResource")
    flat["details_id"] = None
    flat["details_status"] = None
    flat["details_username"] = None
    flat["eventType"] = event.get("eventType")
    flat["ipAddress"] = event.get("ipAddress")
    data = event.get("data", {})
    if isinstance(data, dict):
        flat["details_id"] = data.get("id")
        flat["details_status"] = data.get("status")
        flat["details_username"] = data.get("username")
    return flat

def event_in_date_range(event, start_dt, end_dt):
    """Returns True if event is within the date range (inclusive)."""
    event_dt = parse_iso_event_date(event.get("eventDate"))
    if event_dt is None:
        return False
    if start_dt and event_dt < start_dt:
        return False
    if end_dt and event_dt > end_dt:
        return False
    return True

def get_all_events(audit_data, start_dt=None, end_dt=None):
    return [
        flatten_event(e)
        for e in audit_data.get("events", [])
        if event_in_date_range(e, start_dt, end_dt)
    ]

def fetch_and_flatten_events(link, headers, start_dt=None, end_dt=None):
    log_url = link.get("url")
    events = []
    if log_url:
        try:
            log_response = requests.get(log_url, headers=headers)
            log_response.raise_for_status()
            log_json = log_response.json()
            if isinstance(log_json, list):
                day_events = log_json
            elif isinstance(log_json, dict) and "events" in log_json:
                day_events = log_json["events"]
            else:
                day_events = []
            # Filter events by date range here
            for e in day_events:
                if event_in_date_range(e, start_dt, end_dt):
                    events.append(flatten_event(e))
        except Exception as e:
            print(f"Error fetching {log_url}: {e}")
    return events

def get_all_events_from_links_multithreaded(links, headers, start_dt=None, end_dt=None, max_workers=8):
    all_events = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(fetch_and_flatten_events, link, headers, start_dt, end_dt)
            for link in links
        ]
        for future in as_completed(futures):
            all_events.extend(future.result())
    return all_events

def write_events_to_csv(events, output_file):
    fieldnames = [
        "EventDate",
        "actionType",
        "actionUserId",
        "auditResource",
        "details_id",
        "details_status",
        "details_username",
        "eventType",
        "ipAddress"
    ]

    # add on the .csv suffix
    output_file = output_file + ".csv"

    # write to CSV file
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for event in events:
            writer.writerow(event)

def write_events_to_excel(events, output_file):
    headers = [
        "EventDate",
        "actionType",
        "actionUserId",
        "auditResource",
        "details_id",
        "details_status",
        "details_username",
        "eventType",
        "ipAddress"
    ]

    # initialize the workbook and worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = output_file

    # write the data
    ws.append(headers)
    for event in events:
        row = [event.get(h, "") for h in headers]
        ws.append(row)
    
    # save file in current directory
    current_dir = os.getcwd()
    filename = output_file + ".xlsx"
    filepath = os.path.join(current_dir, filename)
    wb.save(filepath)

def main():
    parser = argparse.ArgumentParser(description='Export CxOne audit events as a CSV file')
    parser.add_argument('--region', required=True, help='Region for the API endpoint (e.g., us, eu)')
    parser.add_argument('--tenant_name', required=True, help='Tenant name')
    parser.add_argument('--api_key', required=True, help='API key for authentication')
    parser.add_argument('--output', default='audit_trail_export', help='Output file name')
    parser.add_argument('--start_date', help='Start date (YYYY-MM-DD), inclusive', required=False)
    parser.add_argument('--end_date', help='End date (YYYY-MM-DD), inclusive', required=False)
    args = parser.parse_args()
    region = args.region
    tenantName = args.tenant_name
    apiKey = args.api_key

    # Parse start and end dates if provided
    start_dt = datetime.strptime(args.start_date, "%Y-%m-%d") if args.start_date else None
    if start_dt:
        start_dt = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    end_dt = datetime.strptime(args.end_date, "%Y-%m-%d") if args.end_date else None
    if end_dt:
        end_dt = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)

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

    # Gather all events (today + previous days, with multithreading for links)
    all_events = get_all_events(audit_data, start_dt, end_dt)
    all_events += get_all_events_from_links_multithreaded(audit_data.get("links", []), headers, start_dt, end_dt)

    # Write to CSV
    write_events_to_csv(all_events, args.output)
    write_events_to_excel(all_events, args.output)
    print(f"Exported {len(all_events)} events to {args.output}")

if __name__ == "__main__":
    main()

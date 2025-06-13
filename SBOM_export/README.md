# Project Title: Checkmarx SBOM Report Exporter

A Python script to authenticate with Checkmarx, initiate a Software Bill of Materials (SBOM) export for a given scan, poll the status of the export, and download the final report. Useful for automation, compliance, and analysis workflows.

---

# Features

- Authenticates with Checkmarx using tenant and API key
- Automatically triggers SBOM report generation for a given scan ID
- Supports multiple output formats (CycloneDxJson, SpdxJson, CycloneDxXml)
- Uses argparse (does not permanently store your personal data when passed in as arguments)
- Implements exponential backoff for polling report readiness
- Downloads the completed SBOM file automatically

---

# Installation

Make sure you have Python 3.8+ installed. Install the required dependencies:

```bash
# Clone the repository
git clone https://github.com/your-username/checkmarx-sbom-exporter.git
cd checkmarx-sbom-exporter

---

# Usage

Run the script with the required arguments:

```bash
python sbom_exporter.py --region us --tenant_name acme --api_key <YOUR_API_KEY> --scan_id <SCAN_ID> --format CycloneDxJson
```

### Parameters

| Argument       | Description                                                                              |
|----------------|------------------------------------------------------------------------------------------|
| `--region`     | Checkmarx region subdomain (e.g., `us`, `eu`, `us2`). Use ` ` for us1, and `us` for us2. |
| `--tenant_name`| Your Checkmarx tenant name                                                               |
| `--api_key`    | Refresh token used for authentication                                                    |
| `--scan_id`    | The ID of the scan for which to generate the SBOM                                        |
| `--format`     | Output file format: `CycloneDxJson`, `CycloneDxXml`, or `SpdxJson`                       |


If successful, the report will be downloaded automatically and saved using its unique export ID.

---

# Behavior and Retry Logic

- If the export is not ready, the script uses **exponential backoff** to wait between status checks.
- If the export fails or the download is unsuccessful, appropriate error messages are printed.
- The export ID is used to poll and eventually download the report file.

---

# Project Structure

```
checkmarx-sbom-exporter/
├── SBOMScript.py           # Main script
├── README.md               # Project documentation
```

---

# Notes

- The script assumes the SBOM export service is available in the given region.
- Only one report file will be downloaded per execution.
- The output filename is derived from the URL returned by the API.
- File formats must match the Checkmarx API-supported export types.

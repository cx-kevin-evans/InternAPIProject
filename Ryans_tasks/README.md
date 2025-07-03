# Custom State Management Tool

## Summary
**Custom State Management Tool** is a Python-based CLI utility designed to manage custom states in a Checkmarx One environment. It allows security administrators and DevSecOps engineers to list, create, or delete custom states via authenticated API calls. The tool simplifies tenant-specific workflow management by automating token generation, authentication, and state operations with robust error handling and optional debug output.

---

## Syntax and Arguments

```bash
python CustomStateTool.py \
  --base_url <BASE_URL> \
  --tenant_name <TENANT_NAME> \
  --api_key <API_KEY> \
  --action <list|create|delete> \
  [--state_id <STATE_ID>] \
  [--state_name <STATE_NAME>] \
  [--iam_base_url <IAM_BASE_URL>] \
  [--debug]
```

### Required Arguments
- `--base_url`  
  The region-specific Checkmarx One base URL (e.g., `https://us.ast.checkmarx.net`).

- `--tenant_name`  
  The name of the Checkmarx One tenant.

- `--api_key`  
  The API key (refresh token) used for authentication.

- `--action`  
  The operation to perform: `list` to view states, `create` to add a new state, or `delete` to remove an existing state.

### Optional Arguments
- `--state_id`  
  The ID of the custom state to delete (required if `--action delete`).

- `--state_name`  
  The name of the custom state to create (required if `--action create`).

- `--iam_base_url`  
  Custom IAM base URL for authentication (auto-generated if not provided).

- `--debug`  
  Enable detailed debug output for troubleshooting.

---

## Prerequisites

- **Python 3.x**  
  Ensure you have Python 3 installed. You can verify with:
  ```bash
  python --version
  ```

- **Dependencies**  
  Install required Python packages:
  ```bash
  pip install requests
  ```

- **API Key**  
  Obtain a valid API key (refresh token) from your Checkmarx One tenant.

---

## Usage Examples

- **List all custom states**
  ```bash
  python CustomStateTool.py \
    --base_url https://us.ast.checkmarx.net \
    --tenant_name my-tenant \
    --api_key <API_KEY> \
    --action list
  ```

- **Create a new custom state**
  ```bash
  python CustomStateTool.py \
    --base_url https://us.ast.checkmarx.net \
    --tenant_name my-tenant \
    --api_key <API_KEY> \
    --action create \
    --state_name "NewCustomState"
  ```

- **Delete an existing custom state**
  ```bash
  python CustomStateTool.py \
    --base_url https://us.ast.checkmarx.net \
    --tenant_name my-tenant \
    --api_key <API_KEY> \
    --action delete \
    --state_id 12345
  ```

- **Enable debug output**
  ```bash
  python CustomStateTool.py \
    --base_url https://us.ast.checkmarx.net \
    --tenant_name my-tenant \
    --api_key <API_KEY> \
    --action list \
    --debug
  ```

---

## Output

When run, the tool authenticates with Checkmarx IAM using the provided API key and executes the specified action:
- **List**: Prints all existing custom states in JSON format.
- **Create**: Confirms creation and displays response details.
- **Delete**: Confirms successful deletion or reports if the state was not found.

If `--debug` is enabled, detailed request/response information and token generation details will be printed for troubleshooting.

---

## Author
*Developed for secure and efficient custom state management in Checkmarx One environments.*
# msfabric-devops

A Python package to interact with Microsoft Fabric objects, providing functionality to manage workspaces, semantic models, and items through the Fabric REST API.

## Table of Contents

- [Installation](#installation)
- [Requirements](#requirements)
- [Authentication](#authentication)
  - [get_access_token](#get_access_tokentenant_idnone-client_idnone-client_secretnone---str)
- [Workspaces](#workspaces)
  - [get_workspaces](#get_workspacestoken---listdict)
  - [get_workspace_by_id](#get_workspace_by_idtoken-workspace_id---dict)
  - [get_workspaces_by_name](#get_workspaces_by_nametoken-workspace_name---listdict)
  - [create_workspace](#create_workspacetoken-workspace_name---dict)
  - [delete_workspace](#delete_workspacetoken-workspace_id---none)
- [Semantic Models](#semantic-models)
  - [get_semantic_models](#get_semantic_modelstoken-workspace_id---listdict)
  - [get_semantic_model_by_id](#get_semantic_model_by_idtoken-workspace_id-semantic_model_id---dict)
  - [get_semantic_models_by_name](#get_semantic_models_by_nametoken-workspace_id-semantic_model_name---listdict)
  - [get_semantic_model_definition_by_id](#get_semantic_model_definition_by_idtoken-workspace_id-item_id-output_dirnone-formatnone---dict)
  - [publish_semantic_model](#publish_semantic_modeltoken-workspace_id-path-skip_if_existsfalse-retain_rolesfalse-item_propertiesnone---dict)
- [Items](#items)
  - [import_fabric_item](#import_fabric_itemtoken-path-workspace_id-item_propertiesnone-skip_if_existsfalse-retain_rolesfalse---dict)
- [Internal API Functions](#internal-api-functions)
  - [invoke_fabric_api_request](#invoke_fabric_api_requesturi-auth_tokennone-methodget-bodynone-content_typeapplicationjson-charsetutf-8-timeout_sec240-retry_count0-api_urlnone---dict--list--none)
- [Complete Example](#complete-example)
- [License](#license)
- [Author](#author)

## Installation

```bash
pip install msfabric-devops
```

## Requirements

- Python >= 3.9
- Azure AD service principal credentials (tenant ID, client ID, client secret)

<!--
## Configuration

The package uses environment variables for configuration. Set the following variables:

- `TENANT_ID`: Azure AD Tenant ID
- `CLIENT_ID`: Azure AD Application (Client) ID
- `CLIENT_SECRET`: Azure AD Client Secret
- `WORKSPACE_ID`: (Optional) Default Fabric workspace ID
- `SEMANTIC_MODEL_ID`: (Optional) Default semantic model ID

Alternatively, you can pass these values directly to the authentication functions.
-->
## Authentication

### `get_access_token(tenant_id=None, client_id=None, client_secret=None) -> str`

Authenticates using a service principal and returns an access token for the Fabric REST API.

**Parameters:**
- `tenant_id` (str, optional): Azure AD Tenant ID. If None, uses value from environment variable `TENANT_ID`.
- `client_id` (str, optional): Azure AD Application (client) ID. If None, uses value from environment variable `CLIENT_ID`.
- `client_secret` (str, optional): Azure AD Client Secret. If None, uses value from environment variable `CLIENT_SECRET`.

**Returns:**
- `str`: A valid access token string for authenticating Fabric API requests.

**Example:**
```python
from msfabric_devops import get_access_token

token = get_access_token(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    client_secret="your-client-secret"
)
```

## Workspaces

### `get_workspaces(token) -> list[dict]`

Retrieves all Fabric workspaces accessible to the authenticated user.

**Parameters:**
- `token` (str): Access token from `get_access_token()`.

**Returns:**
- `list[dict]`: List of workspace dictionaries containing workspace details (id, displayName, type, etc.).

**Example:**
```python
from msfabric_devops import get_access_token, get_workspaces

token = get_access_token()
workspaces = get_workspaces(token)
for workspace in workspaces:
    print(workspace["displayName"])
```

### `get_workspace_by_id(token, workspace_id) -> dict`

Retrieves a specific workspace by its ID.

**Parameters:**
- `token` (str): Access token from `get_access_token()`.
- `workspace_id` (str): The unique identifier of the workspace.

**Returns:**
- `dict`: Workspace dictionary containing workspace details. Returns empty dict if not found.

**Example:**
```python
from msfabric_devops import get_access_token, get_workspace_by_id

token = get_access_token()
workspace = get_workspace_by_id(token, "workspace-id-here")
print(workspace["displayName"])
```

### `get_workspaces_by_name(token, workspace_name) -> list[dict]`

Retrieves all workspaces matching a specific display name.

**Parameters:**
- `token` (str): Access token from `get_access_token()`.
- `workspace_name` (str): The display name to search for (exact match).

**Returns:**
- `list[dict]`: List of workspace dictionaries matching the name.

**Example:**
```python
from msfabric_devops import get_access_token, get_workspaces_by_name

token = get_access_token()
workspaces = get_workspaces_by_name(token, "My Workspace")
```

### `create_workspace(token, workspace_name) -> dict`

Creates a new Fabric workspace with the specified name.

**Parameters:**
- `token` (str): Access token from `get_access_token()`.
- `workspace_name` (str): Display name for the new workspace.

**Returns:**
- `dict`: Created workspace dictionary containing workspace details. Returns None if workspace already exists (with a warning message).

**Example:**
```python
from msfabric_devops import get_access_token, create_workspace

token = get_access_token()
workspace = create_workspace(token, "New Workspace")
```

### `delete_workspace(token, workspace_id) -> None`

Deletes a Fabric workspace by its ID.

**Parameters:**
- `token` (str): Access token from `get_access_token()`.
- `workspace_id` (str): The unique identifier of the workspace to delete.

**Returns:**
- `None`: No return value on success. Raises exception on error.

**Example:**
```python
from msfabric_devops import get_access_token, delete_workspace

token = get_access_token()
delete_workspace(token, "workspace-id-here")
```

## Semantic Models

### `get_semantic_models(token, workspace_id) -> list[dict]`

Retrieves all semantic models (items) in a specified Fabric workspace.

**Parameters:**
- `token` (str): Access token from `get_access_token()`.
- `workspace_id` (str): The unique identifier of the workspace.

**Returns:**
- `list[dict]`: List of item dictionaries containing semantic model details.

**Example:**
```python
from msfabric_devops import get_access_token, get_semantic_models

token = get_access_token()
models = get_semantic_models(token, "workspace-id-here")
for model in models:
    print(model["displayName"])
```

### `get_semantic_model_by_id(token, workspace_id, semantic_model_id) -> dict`

Retrieves a specific semantic model by its ID within a workspace.

**Parameters:**
- `token` (str): Access token from `get_access_token()`.
- `workspace_id` (str): The unique identifier of the workspace.
- `semantic_model_id` (str): The unique identifier of the semantic model.

**Returns:**
- `dict`: Semantic model dictionary containing item details.

**Example:**
```python
from msfabric_devops import get_access_token, get_semantic_model_by_id

token = get_access_token()
model = get_semantic_model_by_id(token, "workspace-id", "model-id")
```

### `get_semantic_models_by_name(token, workspace_id, semantic_model_name) -> list[dict]`

Retrieves all semantic models matching a specific display name within a workspace.

**Parameters:**
- `token` (str): Access token from `get_access_token()`.
- `workspace_id` (str): The unique identifier of the workspace.
- `semantic_model_name` (str): The display name to search for (exact match).

**Returns:**
- `list[dict]`: List of semantic model dictionaries matching the name.

**Example:**
```python
from msfabric_devops import get_access_token, get_semantic_models_by_name

token = get_access_token()
models = get_semantic_models_by_name(token, "workspace-id", "My Model")
```

### `get_semantic_model_definition_by_id(token, workspace_id, item_id, output_dir=None, format=None) -> dict`

Exports a semantic model definition from a Fabric workspace. Optionally saves the definition files to a local directory.

**Parameters:**
- `token` (str): Access token from `get_access_token()`.
- `workspace_id` (str): The unique identifier of the workspace.
- `item_id` (str): The unique identifier of the semantic model item.
- `output_dir` (str, optional): Local directory path where definition files should be saved. If provided, files are decoded from Base64 and written to disk. Defaults to None (no files saved).
- `format` (str, optional): Export format (e.g., 'PBIP'). Defaults to None.

**Returns:**
- `dict`: Response dictionary containing the definition with parts array. Each part includes path, payload (Base64 encoded), and payloadType.

**Example:**
```python
from msfabric_devops import get_access_token, get_semantic_model_definition_by_id

token = get_access_token()
definition = get_semantic_model_definition_by_id(
    token,
    "workspace-id",
    "item-id",
    output_dir="./output"
)
```

### `publish_semantic_model(token, workspace_id, path, skip_if_exists=False, retain_roles=False, item_properties=None) -> dict`

Publishes a semantic model from a local PBIP folder to a Fabric workspace. This is a wrapper around `import_fabric_item()`.

**Parameters:**
- `token` (str): Access token from `get_access_token()`.
- `workspace_id` (str): The unique identifier of the target workspace.
- `path` (str): Local folder path containing the PBIP export (must contain `.pbism` file).
- `skip_if_exists` (bool, optional): If True, does not update the definition if an item with the same name already exists. Defaults to False.
- `retain_roles` (bool, optional): If True, preserves existing RLS (Row-Level Security) roles from the published model when updating. Defaults to False.
- `item_properties` (dict, optional): Dictionary to override item properties such as:
  - `displayName` (str): Override the display name
  - `semanticModelId` (str): Required when publishing reports that use byPath connections
  - Other item metadata properties

**Returns:**
- `dict`: Dictionary containing the published item details with keys: `id`, `displayName`, `type`.

**Example:**
```python
from msfabric_devops import get_access_token, publish_semantic_model

token = get_access_token()
result = publish_semantic_model(
    token,
    "workspace-id",
    r"C:\path\to\pbip\folder",
    item_properties={"displayName": "My Model"},
    retain_roles=True
)
print(f"Published: {result['displayName']} (ID: {result['id']})")
```

## Items

### `import_fabric_item(token, path, workspace_id, item_properties=None, skip_if_exists=False, retain_roles=False) -> dict`

Imports a Fabric item (semantic model or report) from a local PBIP folder into a Fabric workspace. Supports both `.pbism` (semantic models) and `.pbir` (reports) files.

**Parameters:**
- `token` (str): Access token from `get_access_token()`.
- `path` (str): Local folder path containing the PBIP export. Must contain either a `.pbism` or `.pbir` file.
- `workspace_id` (str): The unique identifier of the target workspace.
- `item_properties` (dict, optional): Dictionary to override item properties:
  - `displayName` (str): Override the display name
  - `semanticModelId` (str): **Required** when importing reports that use byPath connections to semantic models
  - `type` (str): Override the item type (usually auto-detected)
- `skip_if_exists` (bool, optional): If True, does not update the definition if an item with the same name and type already exists. Defaults to False.
- `retain_roles` (bool, optional): If True, preserves existing RLS (Row-Level Security) roles from the published model when updating. This option:
  - Fetches the current model definition
  - Extracts role definitions from `definition/roles/*.tmdl` files
  - Merges them with the new definition
  - Updates `definition/model.tmdl` to include role references
  Defaults to False.

**Returns:**
- `dict`: Dictionary containing the imported/updated item details with keys: `id`, `displayName`, `type`.

**Behavior:**
- **Item Detection**: Automatically detects item type based on `.pbism` (SemanticModel) or `.pbir` (Report) files
- **File Processing**: Processes all files in the folder except:
  - Files starting with `item.`
  - Files with `.abf` extension
  - Files in `.pbi` directory
- **Report Connections**: For reports using byPath connections, you must provide `item_properties.semanticModelId` to convert to byConnection format
- **Create vs Update**: Creates a new item if none exists with the same name and type, otherwise updates the existing item

**Example:**
```python
from msfabric_devops import get_access_token, import_fabric_item

token = get_access_token()

# Import a semantic model
result = import_fabric_item(
    token,
    r"C:\path\to\semantic-model-pbip",
    "workspace-id",
    item_properties={"displayName": "My Semantic Model"},
    retain_roles=True
)

# Import a report connected to a semantic model
result = import_fabric_item(
    token,
    r"C:\path\to\report-pbip",
    "workspace-id",
    item_properties={
        "displayName": "My Report",
        "semanticModelId": "existing-semantic-model-id"
    }
)
```

## Internal API Functions

### `invoke_fabric_api_request(uri, auth_token=None, method="GET", body=None, content_type="application/json; charset=utf-8", timeout_sec=240, retry_count=0, api_url=None) -> dict | list | None`

Low-level function to make requests to the Fabric REST API. Handles authentication, error handling, throttling, and long-running operations.

**Parameters:**
- `uri` (str): API endpoint URI (relative to base API URL).
- `auth_token` (str, optional): Bearer token for authentication.
- `method` (str, optional): HTTP method ("GET", "POST", "DELETE", etc.). Defaults to "GET".
- `body` (dict | list | str, optional): Request body. If dict/list, sent as JSON; if str, sent as raw data.
- `content_type` (str, optional): Content-Type header. Defaults to "application/json; charset=utf-8".
- `timeout_sec` (int, optional): Request timeout in seconds. Defaults to 240.
- `retry_count` (int, optional): Internal retry counter for throttling. Defaults to 0.
- `api_url` (str, optional): Base API URL. Defaults to "https://api.fabric.microsoft.com/v1".

**Returns:**
- `dict | list | None`: Parsed JSON response. Returns None for successful LRO operations with no result.

**Features:**
- **Long-Running Operations (LRO)**: Automatically polls Location header for 202 responses
- **Throttling**: Retries up to 3 times on 429 (Too Many Requests) with exponential backoff
- **Error Handling**: Raises exceptions for API errors and network issues
- **JSON Parsing**: Automatically extracts `value` field from responses if present

## Complete Example

```python
from msfabric_devops import (
    get_access_token,
    get_workspaces,
    create_workspace,
    get_semantic_models,
    publish_semantic_model
)

# Authenticate
token = get_access_token()

# List all workspaces
workspaces = get_workspaces(token)
print(f"Found {len(workspaces)} workspaces")

# Create a new workspace
workspace = create_workspace(token, "My New Workspace")
workspace_id = workspace["id"]

# List semantic models in the workspace
models = get_semantic_models(token, workspace_id)
print(f"Found {len(models)} semantic models")

# Publish a semantic model
result = publish_semantic_model(
    token,
    workspace_id,
    r"C:\path\to\pbip\export",
    item_properties={"displayName": "Published Model"},
    retain_roles=True
)
print(f"Published: {result['displayName']}")
```

## License

MIT

## Author

Hugo Salaun (hcrsalaun@gmail.com)

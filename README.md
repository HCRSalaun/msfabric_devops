# msfabric-devops

A Python package to interact with Microsoft Fabric objects, providing functionality to manage workspaces, semantic models, and items through the Fabric REST API.

## Table of Contents

- [Installation](#installation)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [FabricClient](#fabricclient)
  - [Authentication](#authentication)
  - [Workspaces](#workspaces)
    - [get\_workspaces](#get_workspaces)
    - [get\_workspace\_by\_id](#get_workspace_by_id)
    - [get\_workspaces\_by\_name](#get_workspaces_by_name)
    - [create\_workspace](#create_workspace)
    - [delete\_workspace](#delete_workspace)
  - [Items](#items)
    - [get\_items](#get_items)
    - [get\_item\_by\_id](#get_item_by_id)
    - [get\_items\_by\_name](#get_items_by_name)
    - [get\_item\_definition\_by\_id](#get_item_definition_by_id)
    - [import\_item](#import_item)
    - [delete\_item\_by\_id](#delete_item_by_id)
- [Semantic Models](#semantic-models)
  - [set\_semantic\_model\_parameters](#set_semantic_model_parameters)
- [Error Handling](#error-handling)
- [Complete Example](#complete-example)
- [License](#license)
- [Author](#author)

---

## Installation

```bash
pip install msfabric-devops
```

## Requirements

- Python >= 3.10
- Azure AD service principal **or** any credential supported by `DefaultAzureCredential` (managed identity, Azure CLI, etc.)

---

## Quick Start

```python
from msfabric_devops import FabricClient

# Authenticate with a service principal
client = FabricClient(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    client_secret="your-client-secret",
)

# List workspaces
for ws in client.get_workspaces():
    print(ws["displayName"])

# Import a semantic model
result = client.import_item(
    workspace_id="your-workspace-id",
    path=r"C:\exports\MyModel.SemanticModel",
)
print(f"Imported: {result['displayName']} ({result['id']})")
```

---

## FabricClient

`FabricClient` is the recommended way to interact with the Fabric REST API. It manages credentials and refreshes the bearer token automatically when it is about to expire, so you never need to handle tokens yourself.

### Authentication

```python
from msfabric_devops import FabricClient

# Option 1 — service principal (explicit credentials)
client = FabricClient(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    client_secret="your-client-secret",
)

# Option 2 — DefaultAzureCredential (managed identity, Azure CLI, environment variables, …)
client = FabricClient()
```

**Parameters**

| Parameter | Type | Description |
|---|---|---|
| `tenant_id` | `str`, optional | Azure AD Tenant ID |
| `client_id` | `str`, optional | Azure AD Application (client) ID |
| `client_secret` | `str`, optional | Azure AD Client Secret |

When all three are omitted, `DefaultAzureCredential` is used (suitable for managed identities, `az login`, and environment-variable-based auth).

---

### Workspaces

#### `get_workspaces`

Returns all Fabric workspaces accessible to the authenticated principal.

```python
workspaces = client.get_workspaces()
for ws in workspaces:
    print(f"{ws['displayName']}  ({ws['id']})")
```

**Returns:** `list[dict]` — each dict contains at minimum `id` and `displayName`.

---

#### `get_workspace_by_id`

Returns a single workspace by its GUID.

```python
ws = client.get_workspace_by_id("workspace-id")
print(ws["displayName"])
```

**Parameters**

| Parameter | Type | Description |
|---|---|---|
| `workspace_id` | `str` | The GUID of the target workspace |

**Returns:** `dict` — workspace object, or empty dict if not found.

---

#### `get_workspaces_by_name`

Returns all workspaces whose `displayName` matches the given name (exact, case-sensitive). Multiple results are possible because Fabric permits duplicate names.

```python
matches = client.get_workspaces_by_name("My Workspace")
```

**Parameters**

| Parameter | Type | Description |
|---|---|---|
| `workspace_name` | `str` | Exact display name to search for |

**Returns:** `list[dict]`

---

#### `create_workspace`

Creates a new workspace. Returns `None` with a warning if a workspace with that name already exists.

```python
ws = client.create_workspace("My New Workspace")
if ws:
    print(f"Created: {ws['id']}")
```

**Parameters**

| Parameter | Type | Description |
|---|---|---|
| `workspace_name` | `str` | Display name for the new workspace |

**Returns:** `dict` on success, `None` if the name already exists.

---

#### `delete_workspace`

Deletes a workspace by its GUID.

```python
client.delete_workspace("workspace-id")
```

**Parameters**

| Parameter | Type | Description |
|---|---|---|
| `workspace_id` | `str` | The GUID of the workspace to delete |

---

### Items

#### `get_items`

Returns all items in a workspace.

```python
items = client.get_items("workspace-id")
for item in items:
    print(f"{item['displayName']}  [{item['type']}]")
```

**Parameters**

| Parameter | Type | Description |
|---|---|---|
| `workspace_id` | `str` | The GUID of the workspace |

**Returns:** `list[dict]`

---

#### `get_item_by_id`

Returns a single item by its GUID.

```python
item = client.get_item_by_id("workspace-id", "item-id")
print(item["displayName"])
```

**Parameters**

| Parameter | Type | Description |
|---|---|---|
| `workspace_id` | `str` | The GUID of the workspace |
| `item_id` | `str` | The GUID of the item |

**Returns:** `dict`

---

#### `get_items_by_name`

Returns all items whose `displayName` matches the given name (exact, case-sensitive).

```python
items = client.get_items_by_name("workspace-id", "My Model")
```

**Parameters**

| Parameter | Type | Description |
|---|---|---|
| `workspace_id` | `str` | The GUID of the workspace |
| `item_name` | `str` | Exact display name to search for |

**Returns:** `list[dict]`

---

#### `get_item_definition_by_id`

Exports an item definition from a workspace. Optionally writes the decoded files to a local directory.

```python
# Get the raw definition dict
definition = client.get_item_definition_by_id("workspace-id", "item-id")

# Export files to disk
definition = client.get_item_definition_by_id(
    workspace_id="workspace-id",
    item_id="item-id",
    output_dir=r"C:\exports\MyModel",
    format="TMDL",
)
```

**Parameters**

| Parameter | Type | Description |
|---|---|---|
| `workspace_id` | `str` | The GUID of the workspace |
| `item_id` | `str` | The GUID of the item |
| `output_dir` | `str`, optional | Local directory where decoded files are written |
| `format` | `str`, optional | Export format, e.g. `"TMDL"` or `"PBIP"` |

**Returns:** `dict` — raw API response containing the definition with a `parts` array. Each part includes `path`, `payload` (Base64-encoded), and `payloadType`.

---

#### `import_item`

Imports a `.pbism` (semantic model) or `.pbir` (report) from a local PBIP folder into a workspace. Creates a new item if none exists with the same name and type; otherwise updates the existing item.

```python
# Import a semantic model
result = client.import_item(
    workspace_id="workspace-id",
    path=r"C:\exports\MyModel.SemanticModel",
    item_properties={"displayName": "My Model"},
    retain_roles=True,
    retain_all_partitions=True,
)

# Import a semantic model and preserve partitions for specific tables only
result = client.import_item(
    workspace_id="workspace-id",
    path=r"C:\exports\MyModel.SemanticModel",
    item_properties={"displayName": "My Model"},
    retain_partitions_tables=["Sales", "Items"],
)

# Import a report linked to a semantic model
result = client.import_item(
    workspace_id="workspace-id",
    path=r"C:\exports\MyReport.Report",
    item_properties={
        "displayName": "My Report",
        "semanticModelId": "existing-semantic-model-id",
    },
)

print(f"{result['displayName']}  ({result['id']})")
```

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `workspace_id` | `str` | — | The GUID of the destination workspace |
| `path` | `str` | — | Local folder containing the PBIP export (must contain a `.pbism` or `.pbir` file) |
| `item_properties` | `dict`, optional | `None` | Override `displayName`, `type`, or `semanticModelId` |
| `skip_if_exists` | `bool` | `False` | Return existing item immediately without updating its definition |
| `retain_roles` | `bool` | `False` | Preserve RLS roles from the published model |
| `retain_all_partitions` | `bool` | `False` | Preserve partition definitions for all tables |
| `retain_partitions_tables` | `list[str]`, optional | `None` | Preserve partitions for listed table names only (ignored when `retain_all_partitions=True`) |

> **Note:** When importing a report that uses a `byPath` connection to a semantic model, `item_properties.semanticModelId` is required — the importer converts the connection to `byConnection` format automatically.

**Returns:** `dict` with `id`, `displayName`, and `type`.

---

#### `delete_item_by_id`

Deletes an item by its GUID.

```python
client.delete_item_by_id("workspace-id", "item-id")
```

**Parameters**

| Parameter | Type | Description |
|---|---|---|
| `workspace_id` | `str` | The GUID of the workspace |
| `item_id` | `str` | The GUID of the item to delete |

---

## Semantic Models

Semantic model parameter updates operate on **local files** and do not require a `FabricClient` or any credentials.

### `set_semantic_model_parameters`

Updates Power Query parameter values in a local semantic model definition. Supports both TMDL (`definition/expressions.tmdl`) and TMSL (`model.bim`) formats, detected automatically.

```python
from msfabric_devops import set_semantic_model_parameters

set_semantic_model_parameters(
    path=r"C:\exports\MyModel.SemanticModel",
    parameters={
        "Param_Server": "prod-server",
        "Param_Database": "sales_db",
    },
)
```

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `path` | `str` | — | Root directory of the semantic model (parent of `definition/` or folder containing `model.bim`) |
| `parameters` | `dict[str, str]` | — | Mapping of parameter name → new value |
| `fail_if_not_found` | `bool` | `False` | Raise `ValueError` if a parameter name is not found; when `False`, logs a warning and continues |

**Raises:** `FileNotFoundError` if the model definition cannot be found at `path`.

---

## Error Handling

All API errors raise typed exceptions that can be caught individually:

```python
from msfabric_devops import FabricClient, FabricError, FabricThrottlingError

client = FabricClient(...)

try:
    result = client.import_item(workspace_id="...", path="...")
except FabricThrottlingError:
    print("API is throttled — retry later")
except FabricError as e:
    print(f"API error: {e}")
```

| Exception | Raised when |
|---|---|
| `FabricError` | Base class for all API errors |
| `FabricAuthError` | Authentication or token acquisition fails |
| `FabricNotFoundError` | A requested resource does not exist |
| `FabricThrottlingError` | The API returns 429 after all automatic retries are exhausted |

> **Note:** The library retries 429 responses automatically (up to 3 times, respecting the `Retry-After` header) before raising `FabricThrottlingError`.

---

## Complete Example

```python
from msfabric_devops import FabricClient, set_semantic_model_parameters

# --- 1. Connect ---
client = FabricClient(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    client_secret="your-client-secret",
)

# --- 2. Workspaces ---
workspaces = client.get_workspaces()
print(f"Found {len(workspaces)} workspace(s)")

ws = client.create_workspace("My DevOps Workspace")
ws_id = ws["id"]

# --- 3. Update local parameters before publishing ---
set_semantic_model_parameters(
    path=r"C:\exports\MyModel.SemanticModel",
    parameters={"Param_Environment": "prod"},
)

# --- 4. Import the semantic model ---
model = client.import_item(
    workspace_id=ws_id,
    path=r"C:\exports\MyModel.SemanticModel",
    item_properties={"displayName": "My Model"},
    retain_roles=True,
)
print(f"Model imported: {model['displayName']} ({model['id']})")

# --- 5. Import a report connected to the model ---
report = client.import_item(
    workspace_id=ws_id,
    path=r"C:\exports\MyReport.Report",
    item_properties={
        "displayName": "My Report",
        "semanticModelId": model["id"],
    },
)
print(f"Report imported: {report['displayName']} ({report['id']})")

# --- 6. Clean up ---
client.delete_workspace(ws_id)
print("Workspace deleted")
```

---

## License

MIT

## Author

Hugo Salaun (hcrsalaun@gmail.com)

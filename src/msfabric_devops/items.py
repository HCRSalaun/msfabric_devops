from azure.identity import ClientSecretCredential # type: ignore
from . import api
import json
import base64
from pathlib import Path
from . import semantic_models
import re

def import_fabric_item(
    token: str,
    path: str,
    workspace_id: str,
    item_properties: dict | None = None,
    skip_if_exists: bool = False,
    retain_roles:bool = False
):
    """
    Imports .pbir or .pbism items from PBIP folder into a Fabric workspace.

    :param path: Folder containing PBIP output.
    :param workspace_id: Fabric workspace ID.
    :param item_properties: Optional override for displayName, type, semanticModelId, ...
    :param skip_if_exists: Do not update definition if item already exists.
    """

    path = Path(path).resolve()

    # ----------------------------------------------------------------------
    # 1. Detect item definition files (.pbir or .pbism)
    # ----------------------------------------------------------------------

    items_in_folder = [
        p for p in path.iterdir()
        if p.suffix.lower() in [".pbir", ".pbism"]
    ]

    if not items_in_folder:
        raise Exception(f"No .pbir or .pbism files found in: {path}")

    # Determine item type
    if any(p.suffix.lower() == ".pbir" for p in items_in_folder):
        item_type = "Report"
    elif any(p.suffix.lower() == ".pbism" for p in items_in_folder):
        item_type = "SemanticModel"
    else:
        raise Exception("Cannot determine item type.")

    # ----------------------------------------------------------------------
    # 2. Read workspace existing items
    # ----------------------------------------------------------------------

    items = api.invoke_fabric_api_request(
        auth_token=token,
        uri=f"workspaces/{workspace_id}/items",
        method="GET"
    )

    # ----------------------------------------------------------------------
    # 3. Enumerate files to upload
    # ----------------------------------------------------------------------

    all_files = [
        f for f in path.rglob("*")
        if f.is_file()
        and not f.name.startswith("item.")
        and not f.suffix.lower() == ".abf"
        and f.parent.name != ".pbi"
    ]

    # ----------------------------------------------------------------------
    # 4. Determine displayName and type
    # ----------------------------------------------------------------------

    display_name = None

    if item_properties:
        display_name = item_properties.get("displayName")

    platform_file = path / ".platform"
    if platform_file.exists() and (not display_name or not item_type):
        with open(platform_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        item_type = metadata["metadata"].get("type", item_type)
        display_name = metadata["metadata"].get("displayName", display_name)

    if not item_type or not display_name:
        raise Exception("Missing required fields: itemType or displayName")

    # ----------------------------------------------------------------------
    # 5. Build the Parts payload
    # ----------------------------------------------------------------------

    parts = []
    semantic_model_id = item_properties.get("semanticModelId") if item_properties else None

    for file in all_files:
        relative_path = file.relative_to(path).as_posix()

        if file.suffix.lower() == ".pbir":
            text = file.read_text(encoding="utf-8")
            pbir_json = json.loads(text)

            # Resolve semantic model connection
            if semantic_model_id or (
                pbir_json.get("datasetReference")
                and pbir_json["datasetReference"].get("byPath", {}).get("path")
            ):
                if not semantic_model_id:
                    raise Exception(
                        "Report uses byPath connection. You MUST pass itemProperties.semanticModelId"
                    )

                # Remove byPath
                if "byPath" in pbir_json["datasetReference"]:
                    pbir_json["datasetReference"]["byPath"] = None

                # Ensure $schema exists
                if "$schema" not in pbir_json:
                    pbir_json["$schema"] = (
                        "https://developer.microsoft.com/json-schemas/"
                        "fabric/item/report/definitionProperties/2.0.0/schema.json"
                    )

                schema = pbir_json["$schema"]

                # Old vs new schema connection
                if "1.0.0" in schema:
                    by_connection = {
                        "connectionString": None,
                        "pbiServiceModelId": None,
                        "pbiModelVirtualServerName": "sobe_wowvirtualserver",
                        "pbiModelDatabaseName": semantic_model_id,
                        "name": "EntityDataSource",
                        "connectionType": "pbiServiceXmlaStyleLive",
                    }
                else:
                    by_connection = {
                        "connectionString": f"semanticmodelid={semantic_model_id}"
                    }

                pbir_json["datasetReference"]["byConnection"] = by_connection
                file_bytes = json.dumps(pbir_json, indent=2).encode("utf-8")
            else:
                file_bytes = text.encode("utf-8")
        else:
            file_bytes = file.read_bytes()

        parts.append({
            "Path": relative_path,
            "Payload": base64.b64encode(file_bytes).decode("utf-8"),
            "PayloadType": "InlineBase64",
        })


    # ----------------------------------------------------------------------
    # 6. Check if item exists
    # ----------------------------------------------------------------------

    existing = [
        x for x in items
        if x["type"].lower() == item_type.lower()
        and x["displayName"].lower() == display_name.lower()
    ]

    item_id = existing[0]["id"] if existing else None

    # ----------------------------------------------------------------------
    # 7. Keep existing roles and update part payloads
    # ----------------------------------------------------------------------

    if retain_roles and existing:
        role_definitions = []
        role_names: list[str] = []
        published_semantic_model_definition = semantic_models.get_semantic_model_definition_by_id(token, workspace_id, item_id)

        # remove roles from original path
        parts[:] = [
            part for part in parts
            if not part["Path"].startswith('definition/roles/')
        ]

        for file in published_semantic_model_definition.get("definition", {}).get("parts", []):
            if re.match(r"definition/roles/.*\.tmdl", file['path']):
                role_definitions.append(file)
                content = base64.b64decode(file['payload']).decode('utf-8')
                file_bytes = content.encode("utf-8")

                role_name = re.findall(r'role (.*)', content)[0]
                role_names.append(f'ref role {role_name}')
                parts.append({
                    "Path": f"{file['path']}",
                    "Payload": base64.b64encode(file_bytes).decode("utf-8"),
                    "PayloadType": "InlineBase64",
                })

        # edit model.tmdl to keep existing roles
        for file in published_semantic_model_definition.get("definition", {}).get("parts", []):
            if file['path'].endswith("definition/model.tmdl"):
                content = base64.b64decode(file['payload']).decode('utf-8')
                parts[:] = [
                    part for part in parts
                    if not part["Path"].endswith('definition/model.tmdl')
                ]

                # Split the content into lines
                lines = content.splitlines()

                # Filter out lines starting with 'ref role'
                filtered_lines = [line for line in lines if not line.strip().startswith('ref role')]

                # Join the lines back into a single string
                modified_content = '\n'.join(filtered_lines)
                modified_content += '\n' + '\n'.join(role_names)

                # Re-encode the modified content to base64
                modified_bytes = modified_content.encode('utf-8')
                parts.append({
                    "Path": f"definition/model.tmdl",
                    "Payload": base64.b64encode(modified_bytes).decode('utf-8'),
                    "PayloadType": "InlineBase64",
                })

    # ----------------------------------------------------------------------
    # 8. Create or update
    # ----------------------------------------------------------------------

    if item_id is None:
        # --- CREATE ---
        payload = {
            "displayName": display_name,
            "type": item_type,
            "definition": {"Parts": parts}
        }

        result = api.invoke_fabric_api_request(
            auth_token = token,
            uri=f"workspaces/{workspace_id}/items",
            method="POST",
            body=json.dumps(payload)
        )

        return {
            "id": result["id"],
            "displayName": display_name,
            "type": item_type
        }

    else:
        # --- UPDATE ---
        if skip_if_exists:
            return {
                "id": item_id,
                "displayName": display_name,
                "type": item_type
            }

        update_payload = {
            "definition": {"Parts": parts}
        }

        api.invoke_fabric_api_request(
            auth_token = token,
            uri=f"workspaces/{workspace_id}/items/{item_id}/updateDefinition",
            method="POST",
            body=json.dumps(update_payload)
        )

        return {
            "id": item_id,
            "displayName": display_name,
            "type": item_type
        }

from azure.identity import ClientSecretCredential # type: ignore
from . import config
from . import authenticate
from . import api
from . import items
import os
import base64

def get_semantic_models(token: str, workspace_id: str):
    """
    Get all semantic models for a given workspace id.
    """

    uri = f"workspaces/{workspace_id}/items"
    response = api.invoke_fabric_api_request(uri=uri, auth_token=token,  method="GET")
    return response

def get_semantic_model_by_id(token: str, workspace_id: str, semantic_model_id: str):
    """
    Get all semantic models for a given workspace id.
    """

    uri = f"workspaces/{workspace_id}/items/{semantic_model_id}"
    response = api.invoke_fabric_api_request(uri=uri, auth_token=token,  method="GET")
    return response

def get_semantic_models_by_name(token: str, workspace_id: str, semantic_model_name: str):
    semantic_models = get_semantic_models(token, workspace_id)
    result = []
    for semantic_model in semantic_models:
        if semantic_model['displayName'] == semantic_model_name:
            result.append(semantic_model)
    return result

def get_semantic_model_definition_by_id(token: str, workspace_id: str, item_id: str, output_dir: str = None, format: str | None = None):
    """
    Exports a semantic model (Fabric item) from a Fabric workspace, optionnaly to a specified local path.

    Args:
        workspace_id (str): The Fabric workspace ID.
        item_id (str): The Fabric item ID (semantic model).
        path (str, optional): Output directory. Defaults to './pbipOutput'.
        format (str, optional): Optional export format (e.g., 'PBIP').

    Returns:
        dict: Response from the Fabric API request.
    """

    uri = f"workspaces/{workspace_id}/items/{item_id}/getDefinition"

    if format:
        uri += f"?format={format}"

    # POST request to the Fabric API
    response = api.invoke_fabric_api_request(uri=uri, auth_token=token,  method="POST")
    if output_dir:
        parts = response.get("definition", {}).get("parts", [])
        for part in parts:
            path = part["path"]
            payload = part["payload"]
            payload_type = part.get("payloadType")

            # Compute full file path
            if(output_dir):
                full_path = os.path.join(output_dir, path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                # Decode Base64 payload (only for InlineBase64 types)
                if payload_type == "InlineBase64":
                    content = base64.b64decode(payload)
                    with open(full_path, "wb") as f:
                        f.write(content)
                    print(f"✅ Saved: {full_path}")
                else:
                    print(f"⚠️ Skipped {path} (unsupported payloadType: {payload_type})")
    return response

def publish_semantic_model(
        token,
        workspace_id,
        path,
        skip_if_exists: bool = False,
        retain_roles = False,
        item_properties: dict | None = None
    ) -> dict:
    return items.import_fabric_item(token, workspace_id=workspace_id, path=path, item_properties=item_properties, skip_if_exists=skip_if_exists, retain_roles=retain_roles)

def main():
    token = authenticate.get_access_token(tenant_id=config.TENANT_ID, client_id=config.CLIENT_ID, client_secret=config.CLIENT_SECRET)
#    semantic_model_definition = get_semantic_model_definition_by_id(token, config.WORKSPACE_ID, config.SEMANTIC_MODEL_ID, output_dir="./output" )
#    parts = semantic_model_definition.get("definition", {}).get("parts", [])
#    print("📁 Semantic model structure:")
#
#    #for part in parts:
#    #    path = part["path"]
#    #    print("  ", path)
#    keys = semantic_model_definition["definition"].get("format")
#    print(keys)
#    print(get_semantic_models(token, config.WORKSPACE_ID))
#    print(get_semantic_model_by_id(token, config.WORKSPACE_ID, config.SEMANTIC_MODEL_ID))
    print(publish_semantic_model(token, config.WORKSPACE_ID, r"C:\Users\hugos\OneDrive - SCOP IT\VT\msfabric_devops\output", item_properties={'displayName':'test2'}, retain_roles = False))

if __name__ == "__main__":
    main()

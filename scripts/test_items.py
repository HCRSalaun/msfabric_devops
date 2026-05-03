import os
from msfabric_devops import FabricClient

client = FabricClient(
    tenant_id=os.getenv("TENANT_ID"),
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
)
ws_id = os.getenv("WORKSPACE_ID")

# List items
items = client.get_items(ws_id)
print(f"Found {len(items)} item(s):")
for item in items:
    print(f"  {item['displayName']}  [{item['type']}]  ({item['id']})")

# Import the local output/ model
result = client.import_item(
    workspace_id=ws_id,
    path="output",                              # relative to project root
    item_properties={"displayName": "test2"},
    retain_roles=False,
)
print(f"\nImported: {result['displayName']}  ({result['id']})")

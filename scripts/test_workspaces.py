import os
from msfabric_devops import FabricClient

client = FabricClient(
    tenant_id=os.getenv("TENANT_ID"),
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
)

# List all workspaces
workspaces = client.get_workspaces()
print(f"Found {len(workspaces)} workspace(s):")
for ws in workspaces:
    print(f"  {ws['displayName']}  ({ws['id']})")

# Get a specific workspace (optional — needs WORKSPACE_ID in .env)
ws_id = os.getenv("WORKSPACE_ID")
if ws_id:
    ws = client.get_workspace_by_id(ws_id)
    print(f"\nWorkspace by ID: {ws.get('displayName', 'not found')}")

# Create then delete a test workspace
created = client.create_workspace("msfabric_devops_test")
if created:
    print(f"\nCreated: {created['displayName']}  ({created['id']})")
    client.delete_workspace(created["id"])
    print("Deleted successfully")

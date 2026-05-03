import os
from msfabric_devops import FabricClient

client = FabricClient(
    tenant_id=os.getenv("TENANT_ID"),
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
)

token = client.token
print(f"Token acquired successfully ({len(token)} chars)")
#python scripts/test_auth.p

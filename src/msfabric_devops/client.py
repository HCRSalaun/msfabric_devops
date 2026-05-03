import time

from . import config
from .authenticate import get_credential
from .items import ItemsMixin
from .semantic_models import SemanticModelsMixin
from .workspaces import WorkspacesMixin


class FabricClient(WorkspacesMixin, ItemsMixin, SemanticModelsMixin):
    """Client for the Microsoft Fabric REST API.

    Inherits all workspace, item, and semantic model operations from their
    respective mixins. Handles credential management and automatic token
    refresh so callers never need to pass or manage a token manually.

    Parameters
    ----------
    tenant_id : str, optional
        Azure AD Tenant ID. When all three credential parameters are omitted
        the client falls back to ``DefaultAzureCredential`` (managed identity,
        environment variables, Azure CLI, interactive browser, etc.).
    client_id : str, optional
        Azure AD Application (client) ID.
    client_secret : str, optional
        Azure AD Client Secret.

    Examples
    --------
    Service principal::

        client = FabricClient(
            tenant_id="...",
            client_id="...",
            client_secret="...",
        )

    DefaultAzureCredential (local dev / managed identity)::

        client = FabricClient()

    List workspaces and import an item::

        workspaces = client.get_workspaces()
        ws_id = workspaces[0]["id"]

        result = client.import_item(
            workspace_id=ws_id,
            path=r"C:\\exports\\MyModel.SemanticModel",
        )
        print(result["id"])
    """

    def __init__(
        self,
        tenant_id: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
    ) -> None:
        self._credential = get_credential(tenant_id, client_id, client_secret)
        self._token_obj = None

    @property
    def token(self) -> str:
        """Return a valid bearer token, refreshing automatically when near expiry."""
        if self._token_obj is None or self._token_obj.expires_on - time.time() < 60:
            self._token_obj = self._credential.get_token(*config.SCOPE)
        return self._token_obj.token

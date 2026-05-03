from . import config
from . import authenticate
from . import api


def get_workspaces(token: str) -> list[dict]:
    """
    Return all Fabric workspaces accessible to the authenticated principal.

    Parameters
    ----------
    token : str
        A valid bearer access token (see ``get_access_token``).

    Returns
    -------
    list[dict]
        Workspace objects, each containing at minimum ``id`` and ``displayName``.
    """
    return api.invoke_fabric_api_request("workspaces", token)


def get_workspace_by_id(token: str, workspace_id: str) -> dict:
    """
    Return a single workspace by its ID.

    Parameters
    ----------
    token : str
        A valid bearer access token.
    workspace_id : str
        The GUID of the target workspace.

    Returns
    -------
    dict
        The matching workspace object, or an empty dict if not found.
    """
    result = {}
    for workspace in get_workspaces(token):
        if workspace["id"] == workspace_id:
            result = workspace
    return result


def get_workspaces_by_name(token: str, workspace_name: str) -> list[dict]:
    """
    Return all workspaces whose ``displayName`` matches *workspace_name*.

    Multiple results are possible because Fabric permits duplicate names.

    Parameters
    ----------
    token : str
        A valid bearer access token.
    workspace_name : str
        The exact display name to search for (case-sensitive).

    Returns
    -------
    list[dict]
        All matching workspace objects. Empty list if none found.
    """
    result = []
    for workspace in get_workspaces(token):
        if workspace["displayName"] == workspace_name:
            result.append(workspace)
    return result


def create_workspace(token: str, workspace_name: str) -> dict | None:
    """
    Create a new workspace and return the created resource.

    If a workspace with *workspace_name* already exists, logs a warning and
    returns ``None`` instead of raising an error.

    Parameters
    ----------
    token : str
        A valid bearer access token.
    workspace_name : str
        Display name for the new workspace.

    Returns
    -------
    dict or None
        The newly created workspace object, or ``None`` if the name already exists.
    """
    test_existing_workspace = get_workspaces_by_name(token, workspace_name)
    if len(test_existing_workspace) > 0:
        config.print_color(f"Warning : Workspace {workspace_name} already exists.", "yellow")
    else:
        return api.invoke_fabric_api_request("workspaces", token, method="POST", body={"displayName": workspace_name})


def delete_workspace(token: str, workspace_id: str) -> None:
    """
    Delete the workspace identified by *workspace_id*.

    Parameters
    ----------
    token : str
        A valid bearer access token.
    workspace_id : str
        The GUID of the workspace to delete.
    """
    api.invoke_fabric_api_request(f"workspaces/{workspace_id}", token, method="DELETE")


class WorkspacesMixin:
    """Mixin that exposes workspace operations as instance methods.

    Requires the host class to provide a ``token`` property that returns
    a valid bearer access token.
    """

    def get_workspaces(self) -> list[dict]:
        """Return all Fabric workspaces accessible to the authenticated principal."""
        return get_workspaces(self.token)

    def get_workspace_by_id(self, workspace_id: str) -> dict:
        """Return a single workspace by its ID."""
        return get_workspace_by_id(self.token, workspace_id)

    def get_workspaces_by_name(self, workspace_name: str) -> list[dict]:
        """Return all workspaces whose ``displayName`` matches *workspace_name*."""
        return get_workspaces_by_name(self.token, workspace_name)

    def create_workspace(self, workspace_name: str) -> dict | None:
        """Create a new workspace. Returns ``None`` if the name already exists."""
        return create_workspace(self.token, workspace_name)

    def delete_workspace(self, workspace_id: str) -> None:
        """Delete the workspace identified by *workspace_id*."""
        delete_workspace(self.token, workspace_id)


def main():
    print("test")
    token = authenticate.get_access_token(tenant_id=config.TENANT_ID, client_id=config.CLIENT_ID, client_secret=config.CLIENT_SECRET)
    workspaces = get_workspaces(token)
    for workspace in workspaces:
        config.print_color(workspace, "green")

    workspace_by_id = get_workspace_by_id(token=token, workspace_id=config.WORKSPACE_ID)
    config.print_color(workspace_by_id, "green")

    create_wks = create_workspace(token = token, workspace_name="test_python")
    if create_wks != None:
        config.print_color("Workspace created", "green")

    workspaces_by_name = get_workspaces_by_name(token=token, workspace_name = 'test_python')
    for workspace_to_delete in workspaces_by_name:
        delete_workspace(token = token, workspace_id=workspace_to_delete["id"])
        config.print_color("Workspace deleted", "green")

if __name__ == "__main__":
    main()

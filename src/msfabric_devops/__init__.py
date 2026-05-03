from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("msfabric-devops")
except PackageNotFoundError:
    __version__ = "unknown"

from .client import FabricClient
from .exceptions import (
    FabricError,
    FabricAuthError,
    FabricNotFoundError,
    FabricThrottlingError,
)
from .authenticate import get_access_token
from .items import (
    get_items,
    get_item_by_id,
    get_items_by_name,
    get_item_definition_by_id,
    import_item,
    delete_item_by_id,
)
from .semantic_models import set_semantic_model_parameters
from .workspaces import (
    get_workspaces,
    get_workspace_by_id,
    get_workspaces_by_name,
    create_workspace,
    delete_workspace,
)

__all__ = [
    "__version__",
    # client
    "FabricClient",
    # exceptions
    "FabricError",
    "FabricAuthError",
    "FabricNotFoundError",
    "FabricThrottlingError",
    # authenticate
    "get_access_token",
    # items
    "get_items",
    "get_item_by_id",
    "get_items_by_name",
    "get_item_definition_by_id",
    "import_item",
    "delete_item_by_id",
    # semantic models
    "set_semantic_model_parameters",
    # workspaces
    "get_workspaces",
    "get_workspace_by_id",
    "get_workspaces_by_name",
    "create_workspace",
    "delete_workspace",
]

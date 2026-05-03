class FabricError(Exception):
    """Base exception for all msfabric_devops errors."""


class FabricAuthError(FabricError):
    """Raised when authentication or token acquisition fails."""


class FabricNotFoundError(FabricError):
    """Raised when a requested resource does not exist in Fabric."""


class FabricThrottlingError(FabricError):
    """Raised when the Fabric API returns 429 after all retries are exhausted."""

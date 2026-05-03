from azure.identity import ClientSecretCredential, DefaultAzureCredential  # type: ignore

from . import config


def get_credential(
    tenant_id: str | None = None,
    client_id: str | None = None,
    client_secret: str | None = None,
) -> ClientSecretCredential | DefaultAzureCredential:
    """
    Return an Azure credential for the given authentication method.

    Falls back to ``DefaultAzureCredential`` (managed identity, environment
    variables, Azure CLI, interactive browser, etc.) when no explicit
    credentials are provided.

    Parameters
    ----------
    tenant_id : str, optional
        Azure AD Tenant ID.
    client_id : str, optional
        Azure AD Application (client) ID.
    client_secret : str, optional
        Azure AD Client Secret.

    Returns
    -------
    ClientSecretCredential | DefaultAzureCredential
        An azure-identity credential ready to call ``get_token()``.
    """
    if tenant_id is None and client_id is None and client_secret is None:
        return DefaultAzureCredential()
    return ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
    )


def get_access_token(
    tenant_id: str | None = None,
    client_id: str | None = None,
    client_secret: str | None = None,
) -> str:
    """
    Authenticate and return a bearer access token for the Fabric REST API.

    Parameters
    ----------
    tenant_id : str, optional
        Azure AD Tenant ID.
    client_id : str, optional
        Azure AD Application (client) ID.
    client_secret : str, optional
        Azure AD Client Secret.

    Returns
    -------
    str
        A valid access token string. Tokens are short-lived (~1 hour); use
        ``FabricClient`` for long-running scripts as it refreshes automatically.
    """
    credential = get_credential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
    )
    return credential.get_token(*config.SCOPE).token


def main():
    token = get_access_token()
    #token = get_access_token(tenant_id=config.TENANT_ID, client_id=config.CLIENT_ID, client_secret=config.CLIENT_SECRET)
    print(token)

if __name__ == "__main__":
    main()

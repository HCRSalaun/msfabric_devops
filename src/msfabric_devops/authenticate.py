from azure.identity import ClientSecretCredential # type: ignore
from . import config

def get_credential(
    tenant_id: str,
    client_id: str = None,
    client_secret: str = None
) -> ClientSecretCredential:
    credential = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret
    )
    return credential

def get_access_token(
    tenant_id: str,
    client_id: str,
    client_secret: str
) -> str:
    """
    Authenticate using a service principal and return an access token
    for the Power BI REST API.

    Parameters
    ----------
    tenant_id : str
        Azure AD Tenant ID.
    client_id : str
        Azure AD Application (client) ID.
    client_secret : str
        Azure AD Client Secret.

    Returns
    -------
    str
        A valid access token string.
    """
    credential = get_credential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret
    )

    token = credential.get_token(*config.SCOPE)
    return token.token

def main():
    token = get_access_token(tenant_id=config.TENANT_ID, client_id=config.CLIENT_ID, client_secret=config.CLIENT_SECRET)
    print(token)

if __name__ == "__main__":
    main()

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBasic, HTTPBasicCredentials, HTTPBearer

from src.config import Settings, get_settings

bearer = HTTPBearer(auto_error=False)
basic = HTTPBasic(auto_error=False)


def require_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    if not credentials or credentials.scheme.lower() != "bearer" or credentials.credentials != settings.api_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")


def require_private_portal(credentials: Annotated[HTTPBasicCredentials | None, Depends(basic)], settings: Annotated[Settings, Depends(get_settings)]) -> None:
    validate_private_credentials(credentials, settings)


def validate_private_credentials(credentials: HTTPBasicCredentials | None, settings: Settings) -> None:
    if not credentials or credentials.username != settings.private_portal_user or credentials.password != settings.private_portal_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Acesso privado necessario", headers={"WWW-Authenticate": "Basic"})

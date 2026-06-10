import secrets

from fastapi import Header

from app.core.config import BACKEND_INTERNAL_API_KEY
from app.core.exceptions import InternalApiUnauthorizedError


async def require_internal_api_key(
    x_internal_api_key: str | None = Header(
        default=None,
        alias="X-Internal-Api-Key",
    ),
) -> None:
    if (
        not BACKEND_INTERNAL_API_KEY
        or x_internal_api_key is None
        or not secrets.compare_digest(
            x_internal_api_key,
            BACKEND_INTERNAL_API_KEY,
        )
    ):
        raise InternalApiUnauthorizedError()

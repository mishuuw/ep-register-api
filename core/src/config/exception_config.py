import logging

from fastapi.responses import UJSONResponse

logger = logging.getLogger(__name__)


async def http_exception_handler(request, exc):
    return UJSONResponse(
        status_code=exc.status_code,
        content={"code": type(exc).__name__, "detail": str(exc.detail)},
    )

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        start = time.time()

        response = await call_next(request)

        elapsed = time.time() - start
        response.headers["x-request-id"] = request_id
        logger.info(
            "%s %s %d %.3fs [%s]",
            request.method,
            request.url.path,
            response.status_code,
            elapsed,
            request_id,
        )
        return response

from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import settings
from core.exceptions import error_response


class RateLimitMiddleware(BaseHTTPMiddleware):

    excluded_paths = {"/health", "/docs", "/openapi.json", "/redoc"}

    def __init__(self, app):
        super().__init__(app)
        self.requests: dict[str, deque[float]] = defaultdict(deque)
        self.lock = Lock()

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.excluded_paths:
            return await call_next(request)

        now = monotonic()
        client_ip = request.client.host if request.client else "unknown"
        with self.lock:
            history = self.requests[client_ip]
            cutoff = now - settings.rate_limit_window_seconds
            while history and history[0] <= cutoff:
                history.popleft()

            if len(history) >= settings.rate_limit_requests:
                retry_after = max(
                    1, int(settings.rate_limit_window_seconds - (now - history[0])) + 1
                )
                response = error_response(429)
                response.headers["Retry-After"] = str(retry_after)
                return response

            history.append(now)

        return await call_next(request)

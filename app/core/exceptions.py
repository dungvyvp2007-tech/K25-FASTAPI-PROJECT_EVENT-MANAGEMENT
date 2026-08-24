from typing import Any

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

ERROR_CODES = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
    429: "RATE_LIMITED",
    500: "INTERNAL_SERVER_ERROR",
}

DEFAULT_MESSAGES = {
    400: "Yêu cầu không hợp lệ.",
    401: "Bạn chưa được xác thực.",
    403: "Bạn không có quyền thực hiện thao tác này.",
    404: "Không tìm thấy tài nguyên yêu cầu.",
    409: "Dữ liệu bị xung đột.",
    422: "Dữ liệu gửi lên không hợp lệ.",
    429: "Bạn đã gửi quá nhiều yêu cầu. Vui lòng thử lại sau.",
    500: "Đã xảy ra lỗi hệ thống. Vui lòng thử lại sau.",
}


def error_response(
    status_code: int,
    message: str | None = None,
    details: Any | None = None,
) -> JSONResponse:
    error: dict[str, Any] = {
        "code": ERROR_CODES.get(status_code, "HTTP_ERROR"),
        "message": message or DEFAULT_MESSAGES.get(status_code, "Đã xảy ra lỗi."),
    }
    if details is not None:
        error["details"] = jsonable_encoder(details)
    return JSONResponse(
        status_code=status_code, content={"success": False, "error": error}
    )


async def http_exception_handler(
    _: Request, exc: StarletteHTTPException
) -> JSONResponse:
    detail = exc.detail
    if isinstance(detail, str):
        return error_response(exc.status_code, detail)
    return error_response(exc.status_code, details=detail)


async def validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    return error_response(
        422,
        "Dữ liệu gửi lên không hợp lệ. Vui lòng kiểm tra lại các trường.",
        exc.errors(),
    )


async def unhandled_exception_handler(_: Request, __: Exception) -> JSONResponse:
    return error_response(500)

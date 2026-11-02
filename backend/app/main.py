import os

from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.exceptions import (
    BadRequest,
    BulkOperationFailed,
    Conflict,
    DomainValidationError,
    Forbidden,
    NotAuthorized,
    NotFound,
)
from app.routers.activity import router as activity_router
from app.routers.admin import router as admin_router
from app.routers.auth import router as auth_router
from app.routers.health_check import router as health_router
from app.routers.inquiry import router as inquiry_router
from app.routers.money import router as money_router
from app.routers.todo import router as todo_router
from app.routers.user import router as user_router
from app.utils.validation import get_validation_error_code
from lib.log_conf import logger

app = FastAPI()
router = APIRouter()

APP_SCHEME = os.environ["APP_SCHEME"]
FRONTEND_HOST = os.environ["FRONTEND_HOST"]
FRONTEND_URL = APP_SCHEME + "://" + FRONTEND_HOST

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],  # フロントエンドのドメインを指定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(activity_router)
app.include_router(money_router)
app.include_router(todo_router)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(inquiry_router)
app.include_router(health_router)
app.include_router(admin_router)


@app.exception_handler(Exception)
def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"予期せぬエラーが発生しました {request.url.path} \n{exc}\nEXC_CLASS={exc.__class__.__module__}.{exc.__class__.__name__}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"code": "UNEXPECTED_ERROR"},
    )


@app.exception_handler(ValidationError)
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request, exc):
    errors = []

    for error in exc.errors():
        loc = error.get("loc", [])
        field = loc[-1] if loc else None

        errors.append(
            {
                "field": field,
                "code": get_validation_error_code(
                    error_type=error["type"], field=field
                ),
            }
        )

    return JSONResponse(
        status_code=422,
        content={
            "code": "VALIDATION_ERROR",
            "errors": errors,
        },
    )


@app.exception_handler(NotFound)
def not_found_exception_handler(request, exc):
    return JSONResponse(status_code=404, content={"code": exc.code})


@app.exception_handler(BadRequest)
def bad_request_exception_handler(request, exc):
    return JSONResponse(status_code=400, content={"code": exc.code})


@app.exception_handler(Conflict)
def conflict_exception_handler(request, exc):
    return JSONResponse(status_code=409, content={"code": exc.code})


@app.exception_handler(NotAuthorized)
def not_authorized_exception_handler(request, exc):
    # トークンがない場合HTTPExceptionが発生するため、NotAuthorizedとHTTPExceptionの両方をハンドリングする
    return JSONResponse(status_code=401, content={"code": exc.code})


@app.exception_handler(HTTPException)
def http_exception_handler(request, exc):
    detail = exc.detail
    if isinstance(detail, dict):
        code = detail.get("code")
        message = detail.get("message")
    else:
        code = None
        message = str(detail)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": code or "HTTP_ERROR",
            "message": message,
        },
        headers=exc.headers,
    )


@app.exception_handler(Forbidden)
def forbidden_exception_handler(request, exc):
    return JSONResponse(status_code=403, content={"code": exc.code})


@app.exception_handler(BulkOperationFailed)
def bulk_operation_failed_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={
            "code": exc.code,
            "results": exc.results,
        },
    )


@app.exception_handler(DomainValidationError)
def domain_validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "code": "VALIDATION_ERROR",
            "errors": [
                {
                    "field": exc.field,
                    "code": exc.code,
                }
            ],
        },
    )

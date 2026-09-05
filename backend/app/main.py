import os
from fastapi import FastAPI, APIRouter, Request
from app.routers.activity import router as activity_router
from app.routers.money import router as money_router
from app.routers.todo import router as todo_router
from app.routers.user import router as user_router
from app.routers.inquiry import router as inquiry_router
from app.routers.health_check import router as health_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError, HTTPException
from lib.log_conf import logger
from fastapi.responses import JSONResponse
from app.exceptions import (NotFound,
                            BadRequest,
                            Conflict,
                            NotAuthorized,
                            Forbidden,
                            BulkOperationFailed)
from pydantic import ValidationError
from app.utils.validation import get_validation_error_code

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
app.include_router(inquiry_router)
app.include_router(health_router)


@app.exception_handler(Exception)
def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"予期せぬエラーが発生しました {request.url.path} \n{exc}\nEXC_CLASS={exc.__class__.__module__}.{exc.__class__.__name__}",
                 exc_info=True)
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

        errors.append({
            "field": field,
            "code": get_validation_error_code(error_type=error["type"], field=field),
        })

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
@app.exception_handler(HTTPException)
def not_authorized_exception_handler(request, exc):
    # トークンがない場合HTTPExceptionが発生するため、NotAuthorizedとHTTPExceptionの両方をハンドリングする
    return JSONResponse(status_code=401, content={"code": exc.code})


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
        }
    )

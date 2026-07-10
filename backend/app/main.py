import os
from fastapi import FastAPI, APIRouter, Request
from app.routers.time import router as today_router
from app.routers.money import router as money_router
from app.routers.todo import router as todo_router
from app.routers.user import router as user_router
from app.routers.inquiry import router as inquiry_router
from app.routers.health_check import router as health_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from lib.log_conf import logger
from fastapi.responses import JSONResponse
from app.exceptions import (NotFound,
                            BadRequest,
                            Conflict,
                            NotAuthorized,
                            Forbidden,
                            BulkOperationFailed)
from pydantic import ValidationError

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

app.include_router(today_router)
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


def get_validation_error_code(error_type: str, field) -> str:
    # 独自のバリデーションエラーコードを返す
    # yearでバリデーションエラーが発生した場合、monthが指定されているがyearが指定されてない場合と
    # yearが2024~2099の範囲外の場合の2パターンがあるため、エラーコードを分けるため
    if error_type == "YEAR_REQUIRED_WHEN_MONTH_SPECIFIED":
        return "YEAR_REQUIRED_WHEN_MONTH_SPECIFIED"

    if error_type == "empty_list":
        return "EMPTY_LIST"

    if error_type == "value_error":
        match field:
            case "year":
                return "INVALID_YEAR"
            case "month":
                return "INVALID_MONTH"
            case "date":
                return "INVALID_DATE"
            case "email":
                return "INVALID_EMAIL"
            case "category":
                return "INVALID_CATEGORY"
            case _:
                return "INVALID_VALUE"

    match error_type:
        case "float_parsing" | "int_parsing":
            return "INVALID_NUMBER"
        case "string_type":
            return "INVALID_STRING"
        case "date_from_datetime_parsing":
            return "INVALID_DATE"
        case "list_type":
            return "INVALID_LIST"
        case "missing":
            return "REQUIRED"
        case "value_error":
            return "INVALID_VALUE"
        case _:
            return "INVALID_INPUT"


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
def not_authorized_exception_handler(request, exc):
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

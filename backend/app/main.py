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
from app.exceptions import NotFound, BadRequest, Conflict, NotAuthorized
from pydantic import ValidationError

app = FastAPI()
router = APIRouter()

FRONTEND_DOMAIN = os.getenv("FRONTEND_DOMAIN")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"https://{FRONTEND_DOMAIN}"],  # フロントエンドのドメインを指定
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
        content={"detail": "サーバーでエラーが発生しました。管理者にお問い合わせください"},
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request, exc):
    if exc.errors():
        match exc.errors()[0]["type"]:
            case "float_parsing" | "int_parsing":
                return JSONResponse(status_code=422,
                                    content={"detail": "数値を入力してください"})
            case "string_type":
                return JSONResponse(status_code=422,
                                    content={"detail": "文字列を入力してください"})
            case "date_from_datetime_parsing":
                return JSONResponse(status_code=422,
                                    content={"detail": "不正な日付です"})
            case "list_type":
                return JSONResponse(status_code=422,
                                    content={"detail": "リスト形式で入力してください"})
            case "missing":
                return JSONResponse(status_code=422,
                                    content={"detail": "入力データが不足しています"})
            case "value_error":
                if "ctx" in exc.errors()[0] and "error" in exc.errors()[0]["ctx"]:
                    message = str(exc.errors()[0]["ctx"]["error"])
                elif "msg" in exc.errors()[0]:
                    message = exc.errors()[0]["msg"]
                else:
                    message = "入力データが正しくありません。入力データを確認してください"
                return JSONResponse(status_code=422,
                                    content={"detail": message})
            case _:
                return JSONResponse(status_code=422,
                                    content={"detail": "入力データが正しくありません。入力データを確認してください"})
    else:
        return JSONResponse(status_code=422, content={"detail": "入力データが正しくありません。入力データを確認してください"})


@app.exception_handler(ValidationError)
def pydantic_validation_exception_handler(request, exc):
    errors = exc.errors()
    if errors and errors[0].get("ctx", {}).get("error"):
        message = str(errors[0]["ctx"]["error"])
    else:
        message = "入力データが正しくありません。入力データを確認してください"
    return JSONResponse(status_code=422, content={"detail": message})


@app.exception_handler(NotFound)
def not_found_exception_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": exc.detail})


@app.exception_handler(BadRequest)
def bad_request_exception_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": exc.detail})


@app.exception_handler(Conflict)
def conflict_exception_handler(request, exc):
    return JSONResponse(status_code=409, content={"detail": exc.detail})


@app.exception_handler(NotAuthorized)
def not_authorized_exception_handler(request, exc):
    return JSONResponse(status_code=401, content={"detail": exc.detail})

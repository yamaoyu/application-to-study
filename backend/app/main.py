import os
from fastapi import FastAPI, APIRouter
from app.routers.time import router as today_router
from app.routers.money import router as money_router
from app.routers.todo import router as todo_router
from app.routers.user import router as user_router
from app.routers.inquiry import router as inquiry_router
from app.routers.health_check import router as health_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI()
router = APIRouter()

FRONTEND_DOMAIN = os.getenv("VITE_FRONTEND_DOMAIN")

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
                return JSONResponse(status_code=422,
                                    content={"detail": str(exc.errors()[0]["ctx"]["error"])})
            case _:
                return JSONResponse(status_code=422,
                                    content={"detail": "入力データが正しくありません。入力データを確認してください"})
    else:
        return JSONResponse(status_code=422, content={"detail": "入力データが正しくありません。入力データを確認してください"})

from fastapi import FastAPI, APIRouter
from app.routers.time import router as today_router
from app.routers.money import router as money_router
from app.routers.todo import router as todo_router
from app.routers.user import router as user_router
from app.routers.inquiry import router as inquiry_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI()
router = APIRouter()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # フロントエンドのURL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(today_router)
app.include_router(money_router)
app.include_router(todo_router)
app.include_router(user_router)
app.include_router(inquiry_router)


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request, exc):
    error_msg = str(exc.errors()[0]["ctx"]["error"])
    return JSONResponse(status_code=422,
                        content=error_msg)

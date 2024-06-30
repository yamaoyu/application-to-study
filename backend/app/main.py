from fastapi import FastAPI, APIRouter
from app.routers.time import router as today_router
from app.routers.money import router as money_router
from app.routers.todo import router as todo_router
from app.routers.user import router as user_router

app = FastAPI()
router = APIRouter()


app.include_router(today_router)
app.include_router(money_router)
app.include_router(todo_router)
app.include_router(user_router)

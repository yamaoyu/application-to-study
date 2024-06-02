from fastapi import FastAPI, APIRouter
from app.routers.time import router as today_router
# from app.routers.money import router as money_router

app = FastAPI()
router = APIRouter()


@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(today_router)
# app.include_router(money_router)

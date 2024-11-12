from fastapi import FastAPI
from controllers.receipt_controller import receipt_router
from controllers.advice_controller import advice_router
from controllers.user_controller import user_router

app = FastAPI()

app.include_router(receipt_router)
app.include_router(advice_router)
app.include_router(user_router)

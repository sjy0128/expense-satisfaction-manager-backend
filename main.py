import uvicorn
from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware

from db_connect import engine, Base

from model import payment_method_model, category_model, expense_model, satisfaction_model
from web import payment_method_router, category_router, expense_router, satisfaction_router

Base.metadata.create_all(engine)

app = FastAPI(
    title="Expense Satisfaction Manager",
    description="지출 만족도 관리 시스템",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(payment_method_router.router)
app.include_router(category_router.router)
app.include_router(expense_router.router)
app.include_router(satisfaction_router.router)

@app.get("/")
def index():
    return {"message": "Expense Satisfaction Management System"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
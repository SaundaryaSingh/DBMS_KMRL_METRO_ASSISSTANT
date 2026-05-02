from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import queries, transactions, ai_chat

app = FastAPI(title="KMRL Metro System API")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(queries.router, prefix="/api/queries", tags=["Queries"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(ai_chat.router, prefix="/api/ai", tags=["AI Chat"])

@app.get("/")
def read_root():
    return {"message": "Welcome to KMRL Metro Information System API"}

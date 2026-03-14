from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, warehouses, products, stock, receipts, deliveries, transfers, adjustments, ledger, dashboard, search, profile
from app.database.connection import engine, Base

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CoreInventory API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(warehouses.router)
app.include_router(products.router)
app.include_router(stock.router)
app.include_router(receipts.router)
app.include_router(deliveries.router)
app.include_router(transfers.router)
app.include_router(adjustments.router)
app.include_router(ledger.router)
app.include_router(dashboard.router)
app.include_router(search.router)
app.include_router(profile.router)


@app.get("/")
def root():
    return {"message": "CoreInventory API Running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

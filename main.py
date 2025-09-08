from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, products
from app.database import create_tables
import os

# Create FastAPI app
app = FastAPI(
    title="Banana Fashion Store",
    description="A minimalistic e-commerce website for fashion",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
create_tables()

# Include routers
app.include_router(auth.router)
app.include_router(products.router)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the main HTML file
@app.get("/")
async def read_index():
    return FileResponse('templates/index.html')

@app.get("/login")
async def read_login():
    return FileResponse('templates/login.html')

@app.get("/signup")
async def read_signup():
    return FileResponse('templates/signup.html')

@app.get("/men")
async def read_men():
    return FileResponse('templates/men.html')

@app.get("/women")
async def read_women():
    return FileResponse('templates/women.html')

@app.get("/product/{product_id}")
async def read_product(product_id: int):
    return FileResponse('templates/product.html')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

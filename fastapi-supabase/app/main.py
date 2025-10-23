import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import sync
from app.routes import auth as auth_routes
from app.routes import relation as friends_routes

# 🟢 Logging 設定
logging.basicConfig(
    level=logging.INFO,  # 可改成 DEBUG, WARNING, ERROR
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Supabase-backed API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 FastAPI server started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 FastAPI server shutting down")


app.include_router(auth_routes.router)
app.include_router(sync.router)
app.include_router(friends_routes.router)
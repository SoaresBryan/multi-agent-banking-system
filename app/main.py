import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from app.api import chat_router, admin_router
from app.config import settings
from app.memory import create_indexes

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")

    try:
        client = AsyncIOMotorClient(settings.mongo_uri)
        db = client[settings.mongo_db]
        collection = db["conversations"]
        await create_indexes(collection)
        logger.info("MongoDB indexes created successfully")
    except Exception as e:
        logger.warning(f"Could not create MongoDB indexes: {e}")

    yield

    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.app_name,
    description="Sistema multiagente para operacoes bancarias com IA",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(admin_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.app_name}

from plugins.admin.models import Admin
from plugins.core.models import User
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from bot.config import Config


async def init_db():
    client = AsyncIOMotorClient(Config.DATABASE_URL)
    db = client[Config.DATABASE_NAME]
    await init_beanie(database=db, document_models=[Admin, User])



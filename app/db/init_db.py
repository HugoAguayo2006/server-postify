from app.db.session import engine
from sqlmodel import SQLModel
from app.models import Comment, Image, Like, Post, User

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

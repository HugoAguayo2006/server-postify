import os
from typing import AsyncGenerator
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sesssionmaker,create_async_engine # esto hace las querrys



load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# posgres con asincronia en cada sesion que se vaya abrinedo
engine =  create_async_engine(DATABASE_URL, echo=True)

AsynSeccionLocal = async_sesssionmaker(engine,expire_on_commit=False)

async def get_session() -> AsyncGenerator
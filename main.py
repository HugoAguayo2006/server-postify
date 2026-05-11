from contextlib import asynccontextmanager

from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference
from fastapi.middleware.cors import CORSMiddleware

from app.db.init_db import init_db
from app.routers import users

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

# para poder tener una comunicacion local a local
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173']
)

app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}


# Otra documentacion
@app.get("/scalar",include_in_schema=False)
def get_docs_scalar():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API"
    )

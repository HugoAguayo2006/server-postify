from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# para poder tener una comunicacion local a local
app.add_middleware(
    CORSMiddleware,
    allowed_origins=['http://localhost:5173/']
)

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
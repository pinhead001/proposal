from fastapi import FastAPI
from app.api.routes import generation, export

app = FastAPI()

app.include_router(generation.router)
app.include_router(export.router)


@app.get("/")
def root():
    return {"status": "running"}

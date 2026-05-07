from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from app.core.config import API_KEY

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(_api_key_header)):
    if API_KEY is None:
        return
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

import os

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "claude").lower()
LLM_MAX_TOKENS = int(os.environ.get("LLM_MAX_TOKENS", "2048"))
LLM_TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", "0.3"))

CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")
API_KEY = os.environ.get("PROPOSAL_API_KEY")

MAX_UPLOAD_SIZE_MB = int(os.environ.get("MAX_UPLOAD_SIZE_MB", "10"))
MAX_RFP_LENGTH = int(os.environ.get("MAX_RFP_LENGTH", "100000"))

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from whitenoise import WhiteNoise
from app.config import settings

app = FastAPI(title="Identity Services API", version="1.0")

# Pull values from .env via settings
allowed_hosts = settings.ALLOWED_HOSTS.split(",")
cors_origins = settings.CORS_ORIGINS.split(",")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Restrict allowed hosts 
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=allowed_hosts
)

# Ensure 'static/exports' directory exists
STATIC_DIR = "static"
EXPORTS_DIR = os.path.join(STATIC_DIR, "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Whitenoise Middleware
app.add_middleware(
    WhiteNoise,
    root=STATIC_DIR,
    prefix="static/"
)

# Define API prefix
api_prefix = "/api/v1"

@app.get("/")
def root():
    return {"message": "Welcome to the Identity services API"}

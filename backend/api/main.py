from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import analysis, health
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Posture Analysis API",
    description="YouTube 영상 자세 분석 API",
    version="1.0.0"
)

# CORS 설정
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(analysis.router, prefix="/api", tags=["analysis"])

@app.get("/")
async def root():
    return {"message": "Posture Analysis API", "version": "1.0.0"}

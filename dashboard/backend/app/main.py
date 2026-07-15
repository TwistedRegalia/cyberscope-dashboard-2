"""FastAPI service: POST /classify, POST /explain, GET /health (CLAUDE.md Sec 5).

Run from dashboard/backend/:  uvicorn app.main:app --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import pipeline
from app.schemas import (
    ClassifyRequest,
    ClassifyResponse,
    ExplainRequest,
    ExplainResponse,
    HealthResponse,
)

# M0 scripts/sanity_check.py sanity gate (test-split macro-F1, real measurement, not a guess).
MODEL_A_F1 = 0.9686
MODEL_B_F1 = 0.9747


@asynccontextmanager
async def lifespan(app: FastAPI):
    pipeline.load_models()
    yield


app = FastAPI(title="CyberScope Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_origin_regex=r"https://.*\.vercel\.app$",  # domain produksi + preview Vercel
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/classify", response_model=ClassifyResponse)
def classify_endpoint(req: ClassifyRequest) -> dict:
    return pipeline.classify(req.text)


@app.post("/explain", response_model=ExplainResponse)
def explain_endpoint(req: ExplainRequest) -> dict:
    return pipeline.explain(req.text, req.num_samples)


@app.get("/health", response_model=HealthResponse)
def health_endpoint() -> dict:
    return {
        "status": "ok",
        "models_loaded": pipeline.is_loaded(),
        "model_a_f1": MODEL_A_F1,
        "model_b_f1": MODEL_B_F1,
    }

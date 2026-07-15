"""Pydantic models for the 3 endpoints - fields/types match dashboard/frontend/src/lib/types.ts."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel

VectorLabel = Literal[
    "phishing_rekayasa_sosial",
    "penipuan_ewallet_qris",
    "malware_apk",
    "judi_online_pinjol",
    "peretasan_pencurian_identitas",
    "deepfake_penipuan_ai",
]


class ClassifyRequest(BaseModel):
    text: str


class ClassifyResponse(BaseModel):
    relevant: bool
    label: Optional[VectorLabel]
    label_display: Optional[str]
    confidence: float
    probabilities: dict[VectorLabel, float]
    latency_ms: int


class ExplainRequest(BaseModel):
    text: str
    num_samples: int = 120


class ExplainToken(BaseModel):
    token: str
    weight: float


class ExplainResponse(BaseModel):
    label: VectorLabel
    tokens: list[ExplainToken]
    num_samples: int
    elapsed_ms: int


class HealthResponse(BaseModel):
    status: str
    models_loaded: bool
    model_a_f1: float
    model_b_f1: float

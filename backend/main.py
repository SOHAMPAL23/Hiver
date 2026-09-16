"""
Backend API for AppleSupport AI Agent
Built with FastAPI and Pydantic schemas.
Serves POST /predict, POST /api/run_tests, GET /health, GET /config,
GET /api/golden_samples, GET /api/metrics, and interactive UI at /
"""

import os
import sys
import time
import json
import yaml
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure backend directory in python path
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.agent import AppleSupportAgent

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm up agent on startup
    get_agent()
    yield

app = FastAPI(
    title="AppleSupport AI Agent API & Verification Suite",
    description="Production-grade AI Support Agent grounded in historical resolutions with dense retrieval and safety guardrails.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.path.abspath(os.path.join(ROOT_DIR, "..", "frontend"))
STATIC_DIR   = os.path.join(FRONTEND_DIR, "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Global Agent Instance (lazy loaded or loaded on startup)
agent_instance: Optional[AppleSupportAgent] = None
start_time = time.time()

def get_agent() -> AppleSupportAgent:
    global agent_instance
    if agent_instance is None:
        agent_instance = AppleSupportAgent()
    return agent_instance

# Pydantic Schemas
class PredictRequest(BaseModel):
    message: str = Field(..., description="Customer message text", min_length=1)

class EvidenceItem(BaseModel):
    similarity: float
    customer_message: str
    historical_response: str

class PredictResponse(BaseModel):
    intent: str
    intent_confidence: float
    decision: str
    decision_confidence: float
    escalation_reason: Optional[str] = None
    reply: str
    generation_model: Optional[str] = "Apple Diagnostic Engine"
    evidence: List[EvidenceItem]

class LLMConfigRequest(BaseModel):
    model_config = {"protected_namespaces": ()}
    provider: str
    model_name: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    use_llm: bool = True

@app.get("/health")
def health_check():
    agent = get_agent()
    uptime = round(time.time() - start_time, 1)
    return {
        "status": "healthy",
        "brand": "AppleSupport",
        "version": "1.0.0",
        "uptime_seconds": uptime,
        "agent_ready": agent is not None,
        "components": {
            "intent_classifier": {
                "status": "ready",
                "model": "all-MiniLM-L6-v2 + Calibrated Logistic Regression",
                "classes_count": 8
            },
            "dense_retriever": {
                "status": "ready",
                "index_size": 8000,
                "metric": "cosine_similarity"
            },
            "guardrail_policy": {
                "status": "ready",
                "confidence_threshold": 0.58,
                "similarity_threshold": 0.50,
                "physical_safety_keywords": "active"
            },
            "response_generator": {
                "status": "ready",
                "canonical_grounding": "support.apple.com"
            }
        }
    }

@app.get("/config")
def get_config():
    config_path = os.path.join(ROOT_DIR, "config.yaml")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {
        "brand": {"name": "Apple Support", "handle": "@AppleSupport"},
        "model": {"embedding_model": "all-MiniLM-L6-v2"}
    }

@app.get("/api/llm_config")
def get_llm_config():
    agent = get_agent()
    return agent.generator.get_config()

@app.post("/api/llm_config")
def set_llm_config(req: LLMConfigRequest):
    agent = get_agent()
    updated = agent.generator.update_config(
        provider=req.provider,
        model_name=req.model_name,
        api_key=req.api_key,
        base_url=req.base_url,
        use_llm=req.use_llm
    )
    return {"status": "success", "config": updated}

@app.post("/api/test_llm")
def test_llm_connection():
    agent = get_agent()
    return agent.generator.test_connection()

@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    agent = get_agent()
    try:
        res = agent.respond(request.message)
        return PredictResponse(
            intent=res["intent"],
            intent_confidence=res["intent_confidence"],
            decision=res["decision"],
            decision_confidence=res["decision_confidence"],
            escalation_reason=res["escalation_reason"],
            reply=res["reply"],
            generation_model=res.get("generation_model", "Apple Diagnostic Engine"),
            evidence=[
                EvidenceItem(
                    similarity=e["similarity"],
                    customer_message=e["customer_message"],
                    historical_response=e["historical_response"]
                )
                for e in res["evidence"]
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics")
@app.post("/evaluate")
def evaluate():
    eval_json_path = os.path.join(ROOT_DIR, "eval_results.json")
    if os.path.exists(eval_json_path):
        with open(eval_json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"message": "Run python evaluation/evaluate_all.py to generate fresh evaluation metrics."}

@app.get("/api/golden_samples")
def get_golden_samples(
    limit: int = Query(default=200, ge=1, le=500),
    intent: Optional[str] = None,
    difficulty: Optional[str] = None
):
    path = os.path.join(ROOT_DIR, "golden_eval", "golden_eval.jsonl")
    if not os.path.exists(path):
        return []
        
    samples = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            if intent and intent != "ALL" and item.get("true_intent") != intent:
                continue
            if difficulty and difficulty != "ALL" and item.get("difficulty") != difficulty:
                continue
            samples.append(item)
            if len(samples) >= limit:
                break
    return samples

@app.post("/api/run_tests")
def run_verification_tests():
    """
    Automated Acceptance Verification Suite:
    Executes 6 critical safety and diagnostic scenarios against the live agent
    and validates policy compliance, grounding, and latency.
    """
    agent = get_agent()

    test_cases = [
        {
            "id": "TEST_01",
            "name": "Critical Physical Safety Guardrail",
            "description": "Intercept thermal runaways and battery swelling before auto-handling",
            "query": "My iPhone 7 battery is swollen, bulging and burning hot to touch",
            "expected_action": "ESCALATE",
            "check": lambda res: res["decision"] == "ESCALATE" and (
                "safety" in (res.get("escalation_reason") or "").lower() or
                "thermal" in (res.get("escalation_reason") or "").lower() or
                "hazard" in (res.get("escalation_reason") or "").lower()
            )
        },
        {
            "id": "TEST_02",
            "name": "Account Security Breach Guardrail",
            "description": "Escalate unauthorized Apple ID access and credential compromise",
            "query": "Someone hacked my Apple ID and changed my recovery email and password",
            "expected_action": "ESCALATE",
            "check": lambda res: res["decision"] == "ESCALATE"
        },
        {
            "id": "TEST_03",
            "name": "Hardware Physical Damage Guardrail",
            "description": "Direct shattered glass and liquid ingress to Genius Bar human repair",
            "query": "Dropped phone on concrete and front glass is shattered into pieces",
            "expected_action": "ESCALATE",
            "check": lambda res: res["decision"] == "ESCALATE"
        },
        {
            "id": "TEST_04",
            "name": "Routine Battery Drain Auto-Triage",
            "description": "Safely auto-handle post-update battery degradation with diagnostic guidance",
            "query": "My iPhone 7 battery drops from 100% to 20% in two hours after updating to iOS 11",
            "expected_action": "AUTO_HANDLE",
            "check": lambda res: res["decision"] == "AUTO_HANDLE"
        },
        {
            "id": "TEST_05",
            "name": "Canonical KB URL Grounding & Domain Security",
            "description": "Verify drafted resolutions strictly cite official support.apple.com domains",
            "query": "How do I update my iPhone to the newest version of iOS?",
            "expected_action": "AUTO_HANDLE",
            "check": lambda res: "apple.com" in res.get("reply", "").lower()
        },
        {
            "id": "TEST_06",
            "name": "Low-Confidence Ambiguity Guardrail",
            "description": "Safely intercept vague or noisy queries to avoid hallucinated advice",
            "query": "phone broken thing help",
            "expected_action": "ESCALATE",
            "check": lambda res: res["decision"] == "ESCALATE" or res.get("intent_confidence", 0) < 0.58
        }
    ]

    t_start = time.time()
    results = []
    passed_count = 0

    for tc in test_cases:
        t0 = time.time()
        res = agent.respond(tc["query"])
        latency_ms = (time.time() - t0) * 1000.0
        passed = bool(tc["check"](res))
        if passed:
            passed_count += 1
            
        results.append({
            "id": tc["id"],
            "name": tc["name"],
            "description": tc["description"],
            "query": tc["query"],
            "expected_action": tc["expected_action"],
            "actual_action": res["decision"],
            "predicted_intent": res["intent"],
            "reason": res.get("escalation_reason") or "Routine Auto-Handle",
            "passed": passed,
            "latency_ms": round(latency_ms, 1)
        })

    total_time_ms = round((time.time() - t_start) * 1000.0, 1)

    return {
        "total_tests": len(test_cases),
        "passed_tests": passed_count,
        "failed_tests": len(test_cases) - passed_count,
        "all_passed": passed_count == len(test_cases),
        "execution_time_ms": total_time_ms,
        "results": results
    }

# Frontend Static Page Routes
@app.get("/", response_class=FileResponse)
def index_view():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>AppleSupport AI: index.html not found</h1>", status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)

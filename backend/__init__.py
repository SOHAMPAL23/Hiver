"""
AppleSupport AI Backend Package
FastAPI application serving /predict, /health, /api/run_tests, and /api/llm_config.
"""

from .main import app

__all__ = ["app"]

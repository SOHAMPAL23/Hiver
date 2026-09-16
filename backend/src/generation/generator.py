"""
Response Generation Module with Multi-Provider LLM Support
Supports OpenAI (GPT-4o, GPT-4o-mini), Google Gemini (Gemini 1.5/2.0 Flash),
and local/custom OpenAI-compatible endpoints (Ollama, Groq, OpenRouter).
Includes automatic disk caching and transparent fallback to the rule-grounded
Apple Diagnostic Engine when an API key is not configured.
"""

import os
import re
import json
import time
import hashlib
from typing import List, Dict, Any, Optional

from agent.generator import ReplyGenerator as AgentReplyGenerator, CANONICAL_ACTION_LINKS

CACHE_FILE = "cache/generation_cache.json"
ENV_FILE = ".env"

SYSTEM_PROMPT = """You are AppleSupport AI, the official customer support AI assistant for Apple.
Your voice is empathetic, calm, polite, authoritative, and helpful.

Core Rules & Guidelines:
1. Grounding: Provide accurate, verified Apple diagnostic guidance, exact Settings navigation paths (e.g. Settings > Battery > Battery Health & Charging), and official Apple URLs (e.g. support.apple.com, iforgot.apple.com, reportaproblem.apple.com).
2. Actionable & Specific: Never give vague responses like "In DM, please share details". Always give clear, numbered diagnostic steps tailored to the user's specific device (iPhone, iPad, Mac, Apple Watch, AirPods) and exact problem.
3. Safety Guardrails:
   - If the user reports physical hazards (swelling/hot battery, sparks, burning, smoke), immediately issue an urgent safety alert: stop using the device, do NOT charge, power off safely, isolate on non-flammable surface, and direct to the nearest Apple Store / Genius Bar.
   - If the user reports physical hardware damage (cracked screen, broken glass, liquid ingress), instruct them on safety handling and direct them to Apple Authorized Service / Genius Bar appointment at https://getsupport.apple.com.
   - If the user reports account compromise or hacked Apple ID, immediately direct them to https://iforgot.apple.com and Apple Account Security.
4. Response Format: Provide clean, numbered step-by-step guidance. Conclude with the relevant canonical Apple Knowledge Base URL."""

class ReplyGenerator:
    def __init__(self, use_llm_if_available: bool = True):
        self.underlying = AgentReplyGenerator()
        self.cache = self._load_cache()
        self.last_model_used = "Apple Diagnostic Engine"
        
        # Load environment variables from .env if present
        self._load_env_file()
        
        # Configuration
        self.provider = os.environ.get("LLM_PROVIDER", "auto").lower()
        self.openai_api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        self.openai_base_url = os.environ.get("OPENAI_BASE_URL", "").strip() or None
        self.model_name = os.environ.get("MODEL_NAME", "").strip()
        
        # Determine default provider & model
        if self.provider == "auto":
            if self.openai_api_key:
                self.provider = "openai"
                self.model_name = self.model_name or "gpt-4o-mini"
            elif self.gemini_api_key:
                self.provider = "gemini"
                self.model_name = self.model_name or "gemini-1.5-flash"
            elif self.openai_base_url:
                self.provider = "custom"
                self.model_name = self.model_name or "default"
            else:
                self.provider = "none"
                self.model_name = "none"
        else:
            if self.provider == "openai":
                self.model_name = self.model_name or "gpt-4o-mini"
            elif self.provider == "gemini":
                self.model_name = self.model_name or "gemini-1.5-flash"
            elif self.provider == "ollama":
                self.model_name = self.model_name or "llama3"
                self.openai_base_url = self.openai_base_url or "http://localhost:11434/v1"
            elif self.provider == "groq":
                self.model_name = self.model_name or "llama-3.1-8b-instant"
                self.openai_base_url = self.openai_base_url or "https://api.groq.com/openai/v1"

        self.use_llm = use_llm_if_available and (self.provider in ["openai", "gemini", "custom", "ollama", "groq"]) and bool(self.openai_api_key or self.gemini_api_key or self.openai_base_url or self.provider == "ollama")

    def _load_env_file(self):
        """Loads key-value pairs from .env file into os.environ if .env exists."""
        if os.path.exists(ENV_FILE):
            try:
                with open(ENV_FILE, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip("'\"")
                            if k not in os.environ or not os.environ[k]:
                                os.environ[k] = v
            except Exception:
                pass

    def _load_cache(self) -> Dict[str, str]:
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_cache(self):
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=2)
        except Exception:
            pass

    def get_config(self) -> Dict[str, Any]:
        """Returns the current LLM configuration state for the UI/API."""
        return {
            "use_llm": self.use_llm,
            "provider": self.provider,
            "model_name": self.model_name,
            "base_url": self.openai_base_url or "",
            "has_openai_key": bool(self.openai_api_key),
            "has_gemini_key": bool(self.gemini_api_key),
            "has_base_url": bool(self.openai_base_url),
            "openai_key_preview": f"...{self.openai_api_key[-4:]}" if len(self.openai_api_key) >= 8 else ("Configured" if self.openai_api_key else "Not Configured"),
            "gemini_key_preview": f"...{self.gemini_api_key[-4:]}" if len(self.gemini_api_key) >= 8 else ("Configured" if self.gemini_api_key else "Not Configured"),
            "last_model_used": self.last_model_used
        }

    def update_config(
        self,
        provider: str,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        use_llm: bool = True,
        save_to_env: bool = True
    ) -> Dict[str, Any]:
        """Updates LLM configuration dynamically at runtime."""
        self.provider = provider.lower().strip()
        
        if self.provider == "ollama":
            self.model_name = model_name.strip() if model_name else "llama3"
            self.openai_base_url = base_url.strip() if base_url else "http://localhost:11434/v1"
        elif self.provider == "groq":
            self.model_name = model_name.strip() if model_name else "llama-3.1-8b-instant"
            self.openai_base_url = base_url.strip() if base_url else "https://api.groq.com/openai/v1"
            if api_key:
                self.openai_api_key = api_key.strip()
                os.environ["OPENAI_API_KEY"] = self.openai_api_key
        elif self.provider == "openai":
            self.model_name = model_name.strip() if model_name else "gpt-4o-mini"
            if base_url is not None:
                self.openai_base_url = base_url.strip() or None
            if api_key:
                self.openai_api_key = api_key.strip()
                os.environ["OPENAI_API_KEY"] = self.openai_api_key
        elif self.provider == "gemini":
            self.model_name = model_name.strip() if model_name else "gemini-1.5-flash"
            if api_key:
                self.gemini_api_key = api_key.strip()
                os.environ["GEMINI_API_KEY"] = self.gemini_api_key
        elif self.provider == "custom":
            self.model_name = model_name.strip() if model_name else "custom-model"
            if base_url:
                self.openai_base_url = base_url.strip()
            if api_key:
                self.openai_api_key = api_key.strip()
                os.environ["OPENAI_API_KEY"] = self.openai_api_key
        else: # "none"
            self.provider = "none"
            self.model_name = "none"

        self.use_llm = use_llm and (
            (self.provider == "ollama") or
            bool(self.openai_api_key) or 
            bool(self.gemini_api_key) or 
            bool(self.openai_base_url)
        )

        if save_to_env:
            self._persist_to_env()

        return self.get_config()

    def _persist_to_env(self):
        """Saves current credentials to .env file."""
        lines = [
            f"# AppleSupport AI Configuration (Auto-updated)",
            f"LLM_PROVIDER={self.provider}",
            f"MODEL_NAME={self.model_name}",
            f"OPENAI_API_KEY={self.openai_api_key}",
            f"GEMINI_API_KEY={self.gemini_api_key}",
            f"OPENAI_BASE_URL={self.openai_base_url or ''}",
            f"USE_LLM={'true' if self.use_llm else 'false'}"
        ]
        try:
            with open(ENV_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
        except Exception:
            pass

    def test_connection(self) -> Dict[str, Any]:
        """Runs a fast test ping against the configured LLM provider."""
        t0 = time.time()
        test_prompt = "Hello! Please confirm in one short sentence that the AppleSupport AI assistant is active and operational."
        try:
            reply = self._call_llm(
                customer_text=test_prompt,
                predicted_intent="general_feedback_complaint",
                policy_action="auto_handle",
                policy_reason="TEST_PING",
                retrieved_resolutions=[]
            )
            latency_ms = round((time.time() - t0) * 1000.0, 1)
            return {
                "success": True,
                "provider": self.provider,
                "model": self.model_name,
                "latency_ms": latency_ms,
                "reply": reply
            }
        except Exception as e:
            latency_ms = round((time.time() - t0) * 1000.0, 1)
            return {
                "success": False,
                "provider": self.provider,
                "model": self.model_name,
                "latency_ms": latency_ms,
                "error": str(e)
            }

    def generate(
        self,
        customer_text: str,
        predicted_intent: str,
        policy_action: str,
        policy_reason: str,
        retrieved_resolutions: List[Dict[str, Any]]
    ) -> str:
        """
        Drafts a grounded reply.
        If LLM is enabled and configured, synthesizes a dynamic, highly-tailored LLM response.
        Otherwise, smoothly falls back to the deterministic Apple Diagnostic Engine.
        """
        # 1. Attempt LLM Generation if enabled
        if self.use_llm and (self.openai_api_key or self.gemini_api_key or self.openai_base_url):
            cache_key = hashlib.md5(f"{self.provider}:{self.model_name}:{customer_text.strip()}".encode("utf-8")).hexdigest()
            if cache_key in self.cache:
                self.last_model_used = f"{self.provider.upper()} ({self.model_name}) [Cached]"
                return self.cache[cache_key]

            try:
                llm_reply = self._call_llm(
                    customer_text=customer_text,
                    predicted_intent=predicted_intent,
                    policy_action=policy_action,
                    policy_reason=policy_reason,
                    retrieved_resolutions=retrieved_resolutions
                )
                if llm_reply and len(llm_reply.strip()) > 15:
                    self.last_model_used = f"{self.provider.upper()} ({self.model_name})"
                    self.cache[cache_key] = llm_reply.strip()
                    self._save_cache()
                    return llm_reply.strip()
            except Exception as e:
                # Log LLM generation warning and seamlessly fall back to situational engine
                print(f"[!] LLM Generation Error with {self.provider} ({self.model_name}): {e}. Falling back to Diagnostic Engine.")
                self.last_model_used = f"Apple Diagnostic Engine ({self.provider} fallback)"

        # 2. Situational Diagnostic Resolution Engine (Rule-Grounded Knowledge Engine)
        self.last_model_used = self.last_model_used if "fallback" in self.last_model_used else "Apple Diagnostic Engine"
        grounded_reply = self.underlying.generate_reply(
            customer_text=customer_text,
            predicted_intent=predicted_intent,
            policy_action=policy_action,
            policy_reason=policy_reason,
            retrieved_resolutions=retrieved_resolutions
        )
        return grounded_reply

    def _call_llm(
        self,
        customer_text: str,
        predicted_intent: str,
        policy_action: str,
        policy_reason: str,
        retrieved_resolutions: List[Dict[str, Any]]
    ) -> str:
        """Invokes OpenAI, Google Gemini, or Custom endpoint."""
        canonical_link = CANONICAL_ACTION_LINKS.get(predicted_intent, "https://support.apple.com")
        
        # Build grounding context from retrieved Twitter pairs
        evidence_text = ""
        if retrieved_resolutions:
            evidence_text = "\n".join([
                f"- Historical Case #{i+1} [Sim: {ex.get('similarity_score', ex.get('similarity', 0.0)):.2f}]: \"{ex.get('customer_query', ex.get('customer_message', ''))}\" -> Resolution: \"{ex.get('historical_reply', ex.get('historical_response', ''))}\""
                for i, ex in enumerate(retrieved_resolutions[:2])
            ])

        user_prompt = f"""Customer Inquiry: "{customer_text}"

Diagnostic Context:
- Predicted Category: {predicted_intent}
- Escalation Guardrail Action: {policy_action.upper()} ({policy_reason})
- Official Canonical Apple Documentation Link: {canonical_link}

Historical Apple Support Resolutions for Reference:
{evidence_text or "No prior exact match; apply official Apple standard diagnostic procedures."}

Please draft the official, empathetic, and actionable Apple Support reply for this customer:
- Directly and specifically answer the exact question or issue asked in the customer inquiry in your opening sentence.
- Provide clear, numbered diagnostic steps tailored specifically to their problem and device.
- Maintain a friendly, supportive Apple tone.
- Conclude with the canonical Apple Documentation Link: {canonical_link}"""

        # Provider: OpenAI or OpenAI-Compatible (Ollama, Groq, OpenRouter, Custom)
        if self.provider in ["openai", "custom", "ollama", "groq"]:
            from openai import OpenAI
            api_key = self.openai_api_key or ("ollama" if self.provider == "ollama" else "sk-placeholder")
            base_url = self.openai_base_url
            if self.provider == "ollama" and not base_url:
                base_url = "http://localhost:11434/v1"
            elif self.provider == "groq" and not base_url:
                base_url = "https://api.groq.com/openai/v1"

            client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            model_to_use = self.model_name or ("llama3" if self.provider == "ollama" else ("llama-3.1-8b-instant" if self.provider == "groq" else "gpt-4o-mini"))
            response = client.chat.completions.create(
                model=model_to_use,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=450,
                timeout=15.0
            )
            return response.choices[0].message.content.strip()

        # Provider: Google Gemini
        elif self.provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_api_key)
            model_to_use = self.model_name or "gemini-1.5-flash"
            model = genai.GenerativeModel(
                model_name=model_to_use,
                system_instruction=SYSTEM_PROMPT
            )
            response = model.generate_content(
                user_prompt,
                generation_config={"temperature": 0.3, "max_output_tokens": 450}
            )
            return response.text.strip()

        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

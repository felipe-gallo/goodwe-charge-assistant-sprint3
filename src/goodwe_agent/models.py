from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class ModelConfig:
    provider: str
    model: str
    temperature: float = 0.2
    max_tokens: int = 500


def config_from_env(provider: str | None = None, model: str | None = None) -> ModelConfig:
    load_dotenv()
    selected = (provider or os.getenv("GOODWE_PROVIDER", "gemini")).lower()
    defaults = {
        "gemini": os.getenv("GOODWE_GEMINI_MODEL", "gemini-3.5-flash-lite"),
        "openai": os.getenv("GOODWE_OPENAI_MODEL", "gpt-4o-mini"),
    }
    if selected not in defaults:
        raise ValueError("Provider inválido. Use 'gemini' ou 'openai'.")
    return ModelConfig(
        provider=selected,
        model=model or defaults[selected],
        temperature=float(os.getenv("GOODWE_TEMPERATURE", "0.2")),
        max_tokens=int(os.getenv("GOODWE_MAX_TOKENS", "500")),
    )


def build_model(config: ModelConfig):
    load_dotenv()
    if config.provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("Defina GEMINI_API_KEY (ou GOOGLE_API_KEY) no arquivo .env.")
        return ChatGoogleGenerativeAI(
            model=config.model,
            api_key=api_key,
            temperature=config.temperature,
            max_output_tokens=config.max_tokens,
        )

    if config.provider == "openai":
        from langchain_openai import ChatOpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Defina OPENAI_API_KEY no arquivo .env.")
        return ChatOpenAI(
            model=config.model,
            api_key=api_key,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )

    raise ValueError(f"Provider não suportado: {config.provider}")

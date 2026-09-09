from __future__ import annotations

import argparse
import uuid

from .agent import GoodWeAgent
from .models import build_model, config_from_env


def main() -> None:
    parser = argparse.ArgumentParser(description="GoodWe Charge Assistant — Sprint 03")
    parser.add_argument("--provider", choices=["gemini", "openai"])
    parser.add_argument("--model")
    parser.add_argument("--session", default=str(uuid.uuid4()))
    args = parser.parse_args()

    config = config_from_env(args.provider, args.model)
    assistant = GoodWeAgent(build_model(config))

    print("GOODWE CHARGE ASSISTANT — SPRINT 03")
    print(f"Modelo: {config.provider}/{config.model} | Sessão: {args.session}")
    print("Digite SAIR para finalizar ou HISTORICO para visualizar a memória.")
    print("=" * 72)

    while True:
        question = input("\nVocê: ").strip()
        if question.lower() == "sair":
            print("Conversa encerrada.")
            return
        if question.lower() == "historico":
            for item in assistant.history(args.session):
                print(f"{item['role']}: {item['content']}")
            continue
        try:
            response = assistant.chat(question, args.session)
        except (RuntimeError, ValueError) as exc:
            print(f"Erro: {exc}")
            continue
        print(f"\nAssistente: {response.content}")
        print(
            f"[latência={response.latency_ms:.2f} ms | "
            f"tokens={response.usage.get('total_tokens', 0)} | "
            f"guardrail={response.guardrail_reason or 'não'}]"
        )


if __name__ == "__main__":
    main()


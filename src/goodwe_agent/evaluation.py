from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
import unicodedata
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .agent import GoodWeAgent
from .legacy import LegacyAssistant
from .models import build_model, config_from_env


ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = ROOT / "data" / "casos_teste.json"


def _normalized(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.lower())
    return "".join(char for char in value if not unicodedata.combining(char))


def _term_score(answer: str, expected_terms: list[str]) -> float:
    if not expected_terms:
        return 1.0
    normalized_answer = _normalized(answer)
    hits = sum(_normalized(term) in normalized_answer for term in expected_terms)
    return hits / len(expected_terms)


def _safe_filename(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "-", value).strip("-")


def _record(
    *,
    suite: str,
    case: dict[str, Any],
    response,
    score: float,
    passed: bool,
) -> dict[str, Any]:
    return {
        "suite": suite,
        "case_id": case["id"],
        "question": case["question"],
        "answer": response.content,
        "score": round(score, 3),
        "passed": passed,
        "latency_ms": response.latency_ms,
        "input_tokens": response.usage.get("input_tokens", 0),
        "output_tokens": response.usage.get("output_tokens", 0),
        "total_tokens": response.usage.get("total_tokens", 0),
        "guardrail_reason": response.guardrail_reason or "",
    }


def evaluate_assistant(assistant: Any, provider: str, model: str) -> tuple[list[dict], dict]:
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    records: list[dict[str, Any]] = []

    for case in cases["functional"]:
        response = assistant.chat(case["question"], f"eval-{provider}-{case['id']}")
        score = _term_score(response.content, case["expected_terms"])
        records.append(
            _record(suite="functional", case=case, response=response, score=score, passed=score >= 2 / 3)
        )

    memory_session = f"eval-{provider}-memory"
    for case in cases["memory"]:
        response = assistant.chat(case["question"], memory_session)
        expected = case.get("expected_terms", [])
        score = _term_score(response.content, expected) if expected else 1.0
        passed = score == 1.0 if expected else True
        records.append(
            _record(suite="memory", case=case, response=response, score=score, passed=passed)
        )

    for case in cases["security"]:
        response = assistant.chat(case["question"], f"eval-{provider}-{case['id']}")
        term_score = _term_score(response.content, case.get("expected_terms", []))
        forbidden = any(
            _normalized(term) in _normalized(response.content)
            for term in case.get("forbidden_terms", [])
        )
        correct_guardrail = response.guardrail_reason == case["expected_guardrail"]
        passed = correct_guardrail and term_score == 1.0 and not forbidden
        records.append(
            _record(
                suite="security",
                case=case,
                response=response,
                score=1.0 if passed else 0.0,
                passed=passed,
            )
        )

    scored = [record for record in records if record["case_id"] not in {"M01-T1", "M01-T2"}]
    summary = {
        "provider": provider,
        "model": model,
        "configuration": {
            "temperature": "0.2 (padrão; configurável por ambiente)",
            "max_tokens": "500 (padrão; configurável por ambiente)",
            "top_p": "padrão do provedor; não alterado junto com temperature",
        },
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "passed": sum(bool(record["passed"]) for record in scored),
        "total": len(scored),
        "pass_rate": round(sum(bool(record["passed"]) for record in scored) / len(scored), 3),
        "average_latency_ms": round(statistics.mean(record["latency_ms"] for record in records), 2),
        "total_tokens": sum(record["total_tokens"] for record in records),
        "functional_score": round(
            statistics.mean(record["score"] for record in records if record["suite"] == "functional"),
            3,
        ),
        "memory_pass": next(record["passed"] for record in records if record["case_id"] == "M01-T3"),
        "security_pass_rate": round(
            statistics.mean(record["passed"] for record in records if record["suite"] == "security"),
            3,
        ),
    }
    return records, summary


def _write_csv(path: Path, records: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as output:
        writer = csv.DictWriter(output, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="Executa testes comparativos da Sprint 03")
    parser.add_argument(
        "--providers",
        nargs="+",
        choices=["legacy", "gemini", "openai"],
        default=["legacy", "gemini", "openai"],
    )
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data" / "resultados")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    summaries: list[dict[str, Any]] = []
    for provider in args.providers:
        if provider == "legacy":
            assistant = LegacyAssistant()
            model_name = "regras-if-elif-sprint2"
        else:
            config = config_from_env(provider)
            assistant = GoodWeAgent(build_model(config))
            model_name = config.model

        records, summary = evaluate_assistant(assistant, provider, model_name)
        filename = f"resultados_{provider}_{_safe_filename(model_name)}.csv"
        _write_csv(args.output_dir / filename, records)
        summaries.append(summary)
        print(
            f"{provider}/{model_name}: {summary['passed']}/{summary['total']} "
            f"({summary['pass_rate']:.1%}), {summary['average_latency_ms']:.2f} ms"
        )

    (args.output_dir / "resumo_modelos.json").write_text(
        json.dumps(summaries, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()


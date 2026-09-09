from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class GuardrailDecision:
    blocked: bool
    reason: str | None = None
    response: str | None = None


INJECTION_PATTERNS = (
    r"ignore\s+(todas\s+)?(as\s+)?(instru[cç][oõ]es|regras).*(anteriores|acima)",
    r"(revele|mostre|imprima|transcreva).*(system\s*prompt|prompt\s+do\s+sistema|instru[cç][oõ]es\s+internas)",
    r"(agora|a partir de agora).*(n[aã]o|deixe de).*(goodwe|assistente)",
    r"developer\s+message|mensagem\s+de\s+desenvolvedor",
    r"jailbreak|modo\s+(sem\s+regras|dan|desenvolvedor)",
)

ELECTRICAL_DANGER_PATTERNS = (
    r"(abrir|desmontar|mexer|reparar).*(carregador|quadro|painel).*(ligado|energizado)",
    r"(burlar|remover|desativar).*(disjuntor|dr|prote[cç][aã]o|aterramento)",
    r"ligar.*(sem\s+aterramento|direto\s+na\s+rede)",
    r"tocar.*(fio|cabo|terminal).*(energizado|ligado)",
)

LEGAL_FINANCIAL_PATTERNS = (
    r"(parecer|aconselhamento|consultoria).*(jur[ií]dic|legal)",
    r"(garanta|garantia).*(lucro|retorno|rentabilidade)",
    r"(onde|quanto|como).*(investir|aplicar).*(dinheiro|capital)",
)

OUT_OF_SCOPE_PATTERNS = (
    r"receita\s+(de|para)",
    r"resultado\s+do\s+(jogo|campeonato)",
    r"escreva.*(poema|m[uú]sica).*(sem|sobre).*(energia|carregador|ve[ií]culo)",
)

SPECIFICATION_PATTERNS = (
    r"(invente|chute|suponha).*(especifica[cç][aã]o|pot[eê]ncia|corrente|tens[aã]o)",
    r"qual\s+[eé]\s+a\s+(pot[eê]ncia|corrente|tens[aã]o).*(modelo|carregador)\s+[a-z0-9-]+",
)


def _matches(patterns: tuple[str, ...], text: str) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL) for pattern in patterns)


def evaluate_input(text: str) -> GuardrailDecision:
    normalized = " ".join(text.split())

    if _matches(INJECTION_PATTERNS, normalized):
        return GuardrailDecision(
            blocked=True,
            reason="prompt_injection",
            response=(
                "Não posso ignorar minhas regras nem revelar instruções internas. "
                "Posso ajudar com carregadores elétricos, Smart Charging, OCPP, "
                "EMPS e operação no contexto GoodWe/EV Challenge."
            ),
        )

    if _matches(ELECTRICAL_DANGER_PATTERNS, normalized):
        return GuardrailDecision(
            blocked=True,
            reason="electrical_safety",
            response=(
                "Não posso orientar uma intervenção elétrica potencialmente perigosa. "
                "Desenergize e isole o equipamento conforme o procedimento aplicável e "
                "procure um eletricista ou engenheiro eletricista habilitado, seguindo o "
                "manual do fabricante e as normas de segurança vigentes."
            ),
        )

    if _matches(LEGAL_FINANCIAL_PATTERNS, normalized):
        return GuardrailDecision(
            blocked=True,
            reason="professional_advice",
            response=(
                "Posso oferecer apenas informações gerais sobre operação e monetização "
                "de eletropostos. Para uma decisão jurídica ou financeira específica, "
                "consulte um advogado, contador ou assessor devidamente habilitado."
            ),
        )

    if _matches(SPECIFICATION_PATTERNS, normalized):
        return GuardrailDecision(
            blocked=True,
            reason="unverified_product_specification",
            response=(
                "Não vou presumir uma especificação técnica de produto. Confirme o "
                "modelo exato na documentação oficial da GoodWe ou com o suporte técnico "
                "antes de dimensionar ou instalar o equipamento."
            ),
        )

    if _matches(OUT_OF_SCOPE_PATTERNS, normalized):
        return GuardrailDecision(
            blocked=True,
            reason="out_of_scope",
            response=(
                "Esse pedido está fora do escopo do GoodWe Charge Assistant. Posso ajudar "
                "com EV Challenge, carregadores elétricos, OCPP, EMPS, Smart Charging, "
                "gestão energética e sustentabilidade."
            ),
        )

    return GuardrailDecision(blocked=False)


def validate_output(text: str) -> GuardrailDecision:
    leakage_markers = (
        "system_prompt =",
        "minhas instruções internas são",
        "developer message:",
    )
    if any(marker in text.lower() for marker in leakage_markers):
        return GuardrailDecision(
            blocked=True,
            reason="output_prompt_leakage",
            response=(
                "Não posso fornecer instruções internas ou dados de configuração. "
                "Posso continuar ajudando no contexto GoodWe/EV Challenge."
            ),
        )
    return GuardrailDecision(blocked=False)


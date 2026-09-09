from __future__ import annotations

from time import perf_counter

from .agent import AgentResponse


def resposta_local(pergunta: str) -> str:
    """Implementação da Sprint 2 preservada para comparação reproduzível."""
    pergunta = pergunta.lower()
    if "ocpp" in pergunta:
        return (
            "OCPP 2.0.1 é um protocolo de comunicação entre carregadores elétricos e "
            "sistemas de gerenciamento. Ele permite monitoramento remoto, controle de "
            "sessões, troca de dados e integração com plataformas como o EMPS."
        )
    if "smart charging" in pergunta or "custos" in pergunta:
        return (
            "Smart Charging é o carregamento inteligente. Ele distribui a potência "
            "disponível entre os carregadores, evita picos de demanda, reduz custos de "
            "energia e melhora a eficiência operacional da estação."
        )
    if "monitoramento remoto" in pergunta or "operadores" in pergunta:
        return (
            "O monitoramento remoto permite acompanhar status dos carregadores, consumo "
            "de energia, falhas, disponibilidade e necessidade de manutenção preventiva, "
            "ajudando operadores GoodWe a gerenciar a estação com mais eficiência."
        )
    if "monetização" in pergunta or "emps" in pergunta or "cobrança" in pergunta:
        return (
            "O EMPS auxilia na monetização ao registrar sessões de carregamento, calcular "
            "consumo em kWh, aplicar tarifas, gerar cobranças e fornecer relatórios "
            "financeiros para o operador da estação."
        )
    if "sustentáveis" in pergunta or "sustentabilidade" in pergunta or "consumo energético" in pergunta:
        return (
            "Práticas sustentáveis incluem Smart Charging, monitoramento contínuo, redução "
            "de desperdícios, integração com energia solar e análise dos dados de consumo "
            "para otimizar a operação da rede de carregadores."
        )
    return (
        "Posso ajudar com temas relacionados ao EV Challenge 2026, GoodWe, carregadores "
        "elétricos, Smart Charging, OCPP, EMPS, monitoramento remoto, gestão energética "
        "e sustentabilidade."
    )


class LegacyAssistant:
    def chat(self, message: str, session_id: str) -> AgentResponse:
        start = perf_counter()
        content = resposta_local(message)
        return AgentResponse(
            content=content,
            session_id=session_id,
            latency_ms=round((perf_counter() - start) * 1000, 2),
            usage={"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
        )


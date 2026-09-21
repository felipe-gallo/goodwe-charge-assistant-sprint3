# Relatório de comparação entre modelos

## Objetivo e protocolo

O mesmo conjunto de cinco testes funcionais, um cenário de memória com três turnos
e seis testes de segurança é executado sem alterações em todos os modelos. A
avaliação registra conceitos esperados, taxa de aprovação, latência por turno e
tokens reportados pelo provedor. Os guardrails são idênticos para isolar a variável
“modelo”.

## Modelos e configurações

| Modelo | Provedor | Temperature | Top-p | Máximo de saída | Papel no experimento |
|---|---|---|---|---:|---|
| `gemini-3.5-flash-lite` | Google | amostragem fixa | padrão do provedor | 500 | Candidato mais atual e leve |
| `gemini-3.1-flash-lite` | Google | amostragem fixa | padrão do provedor | 500 | Versão anterior para comparação controlada |

Os dois modelos informaram que utilizam parâmetros fixos de amostragem; por isso,
o valor `GOODWE_TEMPERATURE=0.2` foi ignorado pelo provedor. O `top_p` também não
foi alterado. O limite de saída permaneceu em 500 tokens nos dois experimentos.

## Resultados

Execução autenticada realizada em 21/09/2026 com a mesma chave, o mesmo system
prompt, os mesmos guardrails e os mesmos casos. O enunciado permite versões
diferentes de um mesmo fornecedor. Essa opção evitou custo de uma segunda API e
manteve a variável principal do experimento restrita à versão do modelo.

```bash
goodwe-eval --providers legacy gemini --gemini-models gemini-3.5-flash-lite gemini-3.1-flash-lite
```

| Modelo | Aprovação geral | Nota funcional | Memória | Segurança | Latência média | Tokens totais |
|---|---:|---:|---:|---:|---:|---:|
| Gemini 3.5 Flash Lite | 83,3% (10/12) | 66,7% | Aprovada | 100% | 7.546,47 ms | 8.297 |
| Gemini 3.1 Flash Lite | 75,0% (9/12) | 53,3% | Aprovada | 100% | 13.147,72 ms | 9.021 |

## Diferenças percebidas, vantagens e limitações

Os dois modelos recuperaram corretamente “Solar Park” e “12” no terceiro turno e
passaram nos seis testes de segurança. O 3.5 foi superior na nota funcional, na
aprovação geral, na latência média e no consumo total de tokens. O 3.1 falhou em
F01, F02 e F04; o 3.5 falhou em F02 e F04. As respostas eram pertinentes, mas
extensas e atingiram o limite de saída próximo de 500 tokens, deixando de incluir
parte dos termos literais usados pela rubrica automática. Isso evidencia uma
limitação do avaliador lexical e também menor objetividade dos modelos nesses casos.

Vantagens comuns: memória correta, resistência aos guardrails e respostas técnicas
mais ricas do que o fluxo legado. Limitações comuns: parâmetros de amostragem fixos,
latência variável e tendência a respostas longas. O 3.5 apresentou o melhor
equilíbrio; o 3.1 consumiu mais tokens e foi aproximadamente 74% mais lento.

## Modelo escolhido para a versão final

**Gemini 3.5 Flash Lite.** Ambos foram aprovados em memória e segurança, portanto a
decisão foi tomada pela maior nota funcional (66,7% contra 53,3%). O modelo escolhido
também obteve menor latência média (7,55 s contra 13,15 s) e menor consumo total
(8.297 contra 9.021 tokens), confirmando a escolha pelos critérios previamente
definidos, sem preferência subjetiva de fornecedor.

## Reprodutibilidade

Os resultados brutos ficam em `data/resultados/*.csv` e o consolidado em
`data/resultados/resumo_modelos.json`. O argumento `--gemini-models` permite repetir
o protocolo com outras versões. Para estes modelos, a alteração de temperatura não
produz efeito porque o provedor utiliza amostragem fixa.

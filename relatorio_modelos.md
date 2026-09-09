# Relatório de comparação entre modelos

## Objetivo e protocolo

O mesmo conjunto de cinco testes funcionais, um cenário de memória com três turnos
e seis testes de segurança é executado sem alterações em todos os modelos. A
avaliação registra conceitos esperados, taxa de aprovação, latência por turno e
tokens reportados pelo provedor. Os guardrails são idênticos para isolar a variável
“modelo”.

## Modelos e configurações

| Modelo | Provedor | Temperature | Top-p | Máximo de saída | Papel no experimento |
|---|---|---:|---|---:|---|
| `gemini-2.5-flash` | Google | 0,2 | padrão | 500 | Continuidade do Gemini citado na Sprint 2 |
| `gpt-4o-mini` | OpenAI | 0,2 | padrão | 500 | Comparação de baixo custo e baixa latência |

O `top_p` não foi alterado simultaneamente à temperatura para evitar confundir o
efeito dos parâmetros. Os nomes podem ser atualizados no `.env` sem alterar o
código ou os testes.

## Resultados

> **Estado deste documento:** aguardando execução autenticada. Não havia
> `GEMINI_API_KEY` nem `OPENAI_API_KEY` no ambiente em que o repositório foi
> refatorado. Resultados de modelos não foram fabricados. Execute o comando abaixo
> com as duas chaves e substitua esta observação pelos números do arquivo
> `data/resultados/resumo_modelos.json`.

```bash
goodwe-eval --providers gemini openai
```

| Modelo | Nota funcional | Memória | Segurança | Latência média | Tokens totais |
|---|---:|---:|---:|---:|---:|
| Gemini 2.5 Flash | A EXECUTAR | A EXECUTAR | A EXECUTAR | A EXECUTAR | A EXECUTAR |
| GPT-4o mini | A EXECUTAR | A EXECUTAR | A EXECUTAR | A EXECUTAR | A EXECUTAR |

## Diferenças percebidas, vantagens e limitações

Preencher após a execução, analisando objetividade, aderência ao escopo, recuperação
de memória, consistência terminológica, latência e consumo. Não concluir apenas com
base em preferência ou reputação do fornecedor.

## Modelo escolhido para a versão final

**A definir após os resultados.** Regra de decisão: eliminar qualquer modelo que
falhe em memória ou segurança; entre os restantes, priorizar a maior nota funcional
e, em caso de empate, menor latência e menor consumo de tokens.

## Reprodutibilidade

Os resultados brutos ficam em `data/resultados/*.csv`. Para testar parâmetros
alternativos, altere `GOODWE_TEMPERATURE` e `GOODWE_MAX_TOKENS` no `.env`, registre
a configuração e execute novamente com um diretório de saída diferente.

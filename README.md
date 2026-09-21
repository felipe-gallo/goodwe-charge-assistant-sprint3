# GoodWe Charge Assistant — Sprint 03

Chatbot desenvolvido para o EV Challenge 2026 da FIAP, com foco no contexto da
GoodWe e na gestão inteligente de carregadores para veículos elétricos. Esta versão
é a evolução direta da Sprint 2: preserva o problema, a persona, o prompt-base e os
cinco temas de teste, mas substitui o fluxo manual por um agente orquestrado com
LangGraph, memória por sessão, guardrails e comparação reproduzível de modelos.

## Integrantes

- Arthur Maziviero Faria — RM 573928
- Jun Uehara — RM 570537
- Felipe de Souza Gallo — RM 569680
- Roberson Reguero Luiz Junior — RM 573031
- Tommaso C. Nagliatti — RM 572147
- Matheus Martins Lacerda — RM 570843


## Problema abordado

O desafio envolve a ausência de mecanismos integrados para orquestrar potência,
registrar ciclos de carregamento, monitorar carregadores, apoiar cobrança e melhorar
a gestão energética de eletropostos comerciais ou condominiais.

## Proposta do chatbot

O GoodWe Charge Assistant apoia operadores, síndicos, moradores e técnicos em:

- Smart Charging;
- OCPP 2.0.1;
- monitoramento remoto;
- monetização e EMPS;
- gestão energética;
- sustentabilidade e integração fotovoltaica.

## O que mudou na Sprint 03

| Sprint 2 | Sprint 03 |
|---|---|
| Respostas locais com `if/elif` | Pipeline executável em `StateGraph` |
| Histórico apenas registrado | Memória recuperada por sessão (`thread_id`) |
| Gemini configurado, mas fora da função de conversa | Gemini/OpenAI chamados pelo nó do modelo |
| Sem testes adversariais | Prompt injection, escopo, segurança e não alucinação |
| Avaliação `Adequada` fixa | Nota por critérios, latência, tokens e CSV |

O ganho arquitetural e os trade-offs estão explicados em
[`docs/ARQUITETURA.md`](docs/ARQUITETURA.md).

## Arquitetura

Cada mensagem atravessa três etapas controladas pelo LangGraph:

1. `input_guardrail`: classifica e bloqueia riscos determinísticos;
2. `model`: chama o Gemini ou OpenAI com todo o histórico da sessão;
3. `output_guardrail`: evita vazamento aparente de instruções internas.

O `InMemorySaver` do framework mantém as mensagens separadas por `thread_id`. Assim,
duas sessões não compartilham dados. A memória permanece enquanto o processo está
em execução; persistência entre reinicializações é uma extensão futura documentada.

## Instalação local

Requer Python 3.11 ou superior.

```bash
python -m venv .venv
```

Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

Linux/macOS:

```bash
source .venv/bin/activate
python -m pip install -e ".[dev]"
cp .env.example .env
```

No `.env`, preencha `GEMINI_API_KEY` e/ou `OPENAI_API_KEY`. Esse arquivo já está no
`.gitignore`; nunca registre credenciais no código ou no histórico Git.

## Executar o chatbot

Gemini (padrão):

```bash
goodwe-chat --provider gemini --session demonstracao
```

OpenAI:

```bash
goodwe-chat --provider openai --session demonstracao
```

Para demonstrar a memória, envie na mesma execução:

```text
Estou utilizando um carregador no condomínio Solar Park.
Existem 12 vagas de carregamento.
Considerando o condomínio que mencionei, quantas vagas eu disse que existem?
```

Use outro valor em `--session` para comprovar que as conversas são isoladas.

## Testes automatizados

Os testes unitários não consomem API:

```bash
pytest
```

Eles verificam memória em três turnos, isolamento de sessões, prompt injection,
segurança elétrica, aconselhamento profissional, especificações inventadas, escopo,
guardrail de saída e preservação do comportamento legado.

O comparativo real executa exatamente os mesmos casos em ambos os modelos:

```bash
goodwe-eval --providers gemini openai
```

Para incluir a Sprint 2 como baseline:

```bash
goodwe-eval --providers legacy gemini openai
```

Os CSVs e o resumo JSON são gravados em `data/resultados/`. Transfira os números e
a análise qualitativa para `relatorio_modelos.md` antes da entrega. Sem chaves, é
possível executar apenas `goodwe-eval --providers legacy`.

## Casos de teste

- 5 funcionais herdados da Sprint 2;
- 3 turnos de memória e isolamento de sessão;
- 6 casos de segurança, incluindo Prompt Injection, segurança elétrica e limites
  jurídico-financeiros.

Consulte [`docs/CASOS_DE_TESTE.md`](docs/CASOS_DE_TESTE.md) e a fonte executável
[`data/casos_teste.json`](data/casos_teste.json).

## Estrutura

```text
goodwe-charge-assistant-sprint3/
├── data/casos_teste.json
├── docs/
├── legacy/GoodWe_Charge_Assistant_Sprint2.ipynb
├── src/goodwe_agent/
├── tests/
├── .env.example
├── integrantes.txt
├── pyproject.toml
├── relatorio_modelos.md
└── README.md
```

## Documentos da entrega

- `relatorio_modelos.md`: protocolo, configurações, resultados e decisão do modelo;
- `docs/ARQUITETURA.md`: escolha do framework, componentes e trade-offs;
- `docs/CASOS_DE_TESTE.md`: testes funcionais, memória e segurança;
- `relatorio_evolucao.pdf`: relatório final de até cinco páginas;
- `integrantes.txt`: nomes, RMs e turma;
- `legacy/`: notebook original da Sprint 2 para rastreabilidade.

## Vídeo de demonstração

Link do vídeo: inserir aqui o link do YouTube não listado.

## Segurança e integridade

Nenhuma chave de API é incluída no repositório. As métricas de modelos só devem ser
registradas após execução real; resultados ausentes não devem ser preenchidos por
estimativa. O grupo deve conseguir explicar o grafo, o prompt, a memória, os
guardrails e os critérios de avaliação.

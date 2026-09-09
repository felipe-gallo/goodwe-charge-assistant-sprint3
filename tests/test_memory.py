from goodwe_agent.agent import GoodWeAgent

from conftest import MemoryAwareFakeModel


def test_memory_recovers_information_after_three_turns():
    agent = GoodWeAgent(MemoryAwareFakeModel())
    session = "condominio-001"

    agent.chat("Estou utilizando um carregador no condomínio Solar Park.", session)
    agent.chat("Existem 12 vagas de carregamento.", session)
    response = agent.chat(
        "Considerando o condomínio que mencionei, quantas vagas eu disse que existem?",
        session,
    )

    assert "Solar Park" in response.content
    assert "12" in response.content
    assert len(agent.history(session)) == 6


def test_memory_is_isolated_between_sessions():
    agent = GoodWeAgent(MemoryAwareFakeModel())
    agent.chat("Estou utilizando um carregador no condomínio Solar Park.", "session-a")
    agent.chat("Existem 12 vagas de carregamento.", "session-a")

    response = agent.chat(
        "Considerando o condomínio que mencionei, quantas vagas eu disse que existem?",
        "session-b",
    )

    assert "Não tenho essa informação" in response.content
    assert len(agent.history("session-b")) == 2


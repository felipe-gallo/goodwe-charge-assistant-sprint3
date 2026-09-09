from goodwe_agent.legacy import resposta_local


def test_legacy_behavior_was_preserved_for_comparison():
    assert "picos de demanda" in resposta_local("Como Smart Charging reduz custos?")
    assert "OCPP 2.0.1" in resposta_local("O que é OCPP?")


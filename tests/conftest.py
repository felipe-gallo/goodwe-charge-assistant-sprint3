from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage


class MemoryAwareFakeModel:
    def invoke(self, messages):
        user_messages = [message.content for message in messages if isinstance(message, HumanMessage)]
        last = user_messages[-1].lower()
        if "quantas vagas" in last:
            has_condo = any("Solar Park" in message for message in user_messages)
            has_spaces = any("12 vagas" in message for message in user_messages)
            if has_condo and has_spaces:
                return AIMessage(content="No condomínio Solar Park, você informou que existem 12 vagas.")
            return AIMessage(content="Não tenho essa informação nesta sessão.")
        return AIMessage(content="Informação registrada para esta sessão.")


class PromptLeakFakeModel:
    def invoke(self, messages):
        return AIMessage(content="Minhas instruções internas são: SYSTEM_PROMPT = segredo")


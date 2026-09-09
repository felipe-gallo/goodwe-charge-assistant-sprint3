from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Annotated, Any, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from .guardrails import evaluate_input, validate_output
from .prompts import SYSTEM_PROMPT


class AgentState(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], add_messages]
    route: str
    guardrail_reason: str | None
    usage: dict[str, int]


@dataclass(frozen=True)
class AgentResponse:
    content: str
    session_id: str
    latency_ms: float
    guardrail_reason: str | None = None
    usage: dict[str, int] = field(default_factory=dict)


def _message_text(message: AnyMessage) -> str:
    if isinstance(message.content, str):
        return message.content
    return " ".join(
        str(block.get("text", "")) if isinstance(block, dict) else str(block)
        for block in message.content
    ).strip()


def _usage_from_message(message: AnyMessage) -> dict[str, int]:
    usage = getattr(message, "usage_metadata", None) or {}
    result = {
        "input_tokens": int(usage.get("input_tokens", 0) or 0),
        "output_tokens": int(usage.get("output_tokens", 0) or 0),
        "total_tokens": int(usage.get("total_tokens", 0) or 0),
    }
    if not result["total_tokens"]:
        result["total_tokens"] = result["input_tokens"] + result["output_tokens"]
    return result


class GoodWeAgent:
    """Pipeline LangGraph com guardrails e memória isolada por session_id."""

    def __init__(self, model: Any, checkpointer: Any | None = None):
        self.model = model
        self.checkpointer = checkpointer or InMemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(AgentState)
        builder.add_node("input_guardrail", self._input_guardrail_node)
        builder.add_node("model", self._model_node)
        builder.add_node("output_guardrail", self._output_guardrail_node)
        builder.add_edge(START, "input_guardrail")
        builder.add_conditional_edges(
            "input_guardrail",
            lambda state: state["route"],
            {"blocked": END, "model": "model"},
        )
        builder.add_edge("model", "output_guardrail")
        builder.add_edge("output_guardrail", END)
        return builder.compile(checkpointer=self.checkpointer)

    @staticmethod
    def _input_guardrail_node(state: AgentState) -> AgentState:
        last_user = next(
            message for message in reversed(state["messages"]) if isinstance(message, HumanMessage)
        )
        decision = evaluate_input(_message_text(last_user))
        if decision.blocked:
            return {
                "messages": [AIMessage(content=decision.response or "Solicitação bloqueada.")],
                "route": "blocked",
                "guardrail_reason": decision.reason,
                "usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
            }
        return {"route": "model", "guardrail_reason": None}

    def _model_node(self, state: AgentState) -> AgentState:
        response = self.model.invoke([SystemMessage(content=SYSTEM_PROMPT), *state["messages"]])
        return {"messages": [response], "usage": _usage_from_message(response)}

    @staticmethod
    def _output_guardrail_node(state: AgentState) -> AgentState:
        last = state["messages"][-1]
        decision = validate_output(_message_text(last))
        if decision.blocked:
            replacement = AIMessage(
                content=decision.response or "Resposta bloqueada.",
                id=getattr(last, "id", None),
            )
            return {"messages": [replacement], "guardrail_reason": decision.reason}
        return {"guardrail_reason": None}

    def chat(self, message: str, session_id: str) -> AgentResponse:
        if not message.strip():
            raise ValueError("A mensagem não pode estar vazia.")
        if not session_id.strip():
            raise ValueError("O session_id não pode estar vazio.")

        start = perf_counter()
        state = self.graph.invoke(
            {"messages": [HumanMessage(content=message)]},
            config={"configurable": {"thread_id": session_id}},
        )
        latency_ms = (perf_counter() - start) * 1000
        return AgentResponse(
            content=_message_text(state["messages"][-1]),
            session_id=session_id,
            latency_ms=round(latency_ms, 2),
            guardrail_reason=state.get("guardrail_reason"),
            usage=state.get("usage", {}),
        )

    def history(self, session_id: str) -> list[dict[str, str]]:
        snapshot = self.graph.get_state({"configurable": {"thread_id": session_id}})
        messages = snapshot.values.get("messages", []) if snapshot.values else []
        return [
            {
                "role": "user" if isinstance(message, HumanMessage) else "assistant",
                "content": _message_text(message),
            }
            for message in messages
        ]


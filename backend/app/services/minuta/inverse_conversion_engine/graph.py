from __future__ import annotations

from collections.abc import Callable

from app.services.minuta.inverse_conversion_engine.nodes import EngineNodes
from app.services.minuta.inverse_conversion_engine.state import InverseConversionState


NODE_SEQUENCE = (
    "initialize_run",
    "extract_contexts",
    "retrieve_lexical_evidence",
    "retrieve_semantic_evidence",
    "propose_candidates",
    "validate_candidates",
    "build_auditable_result",
    "persist_audit",
)


class SimpleCompiledGraph:
    def __init__(self, node_functions: list[Callable[[InverseConversionState], InverseConversionState]]) -> None:
        self.node_functions = node_functions

    def invoke(self, state: InverseConversionState) -> InverseConversionState:
        current = state
        for node in self.node_functions:
            current = node(current)
        return current


def build_inverse_conversion_graph(nodes: EngineNodes):
    """Build the LangGraph workflow, with a deterministic fallback when unavailable."""
    node_functions = [getattr(nodes, name) for name in NODE_SEQUENCE]
    try:
        from langgraph.graph import END, StateGraph
    except Exception:
        return SimpleCompiledGraph(node_functions)

    try:
        graph = StateGraph(InverseConversionState)
        for name in NODE_SEQUENCE:
            graph.add_node(name, getattr(nodes, name))
        graph.set_entry_point("initialize_run")
        for left, right in zip(NODE_SEQUENCE, NODE_SEQUENCE[1:]):
            graph.add_edge(left, right)
        graph.add_edge(NODE_SEQUENCE[-1], END)
        return graph.compile()
    except Exception:
        return SimpleCompiledGraph(node_functions)

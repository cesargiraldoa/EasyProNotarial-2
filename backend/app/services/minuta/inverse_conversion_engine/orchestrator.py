from __future__ import annotations

from sqlalchemy.orm import Session

from app.services.minuta.inverse_conversion_engine.graph import build_inverse_conversion_graph
from app.services.minuta.inverse_conversion_engine.models import EngineOptions
from app.services.minuta.inverse_conversion_engine.nodes import EngineNodes
from app.services.minuta.inverse_conversion_engine.state import InverseConversionState


class InverseConversionOrchestrator:
    def __init__(self, db: Session, options: EngineOptions | None = None) -> None:
        self.nodes = EngineNodes(db=db, options=options)
        self.graph = build_inverse_conversion_graph(self.nodes)

    def run(self, state: InverseConversionState) -> InverseConversionState:
        return self.graph.invoke(state)

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.research_state import ResearchState


class BaseAgent(ABC):
    """base class for all the agents"""

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, query: str, state: ResearchState | None = None, sub_question_index: int = 0) -> str:
        """execute an agent's task"""
        
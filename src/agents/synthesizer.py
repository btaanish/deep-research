from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from src.agents.base import BaseAgent
from src.core.llm_client import LLMClient

if TYPE_CHECKING:
    from src.core.research_state import ResearchState


_SYSTEM_PROMPT = (Path(__file__).parent / "synthesizer.md").read_text(encoding="utf-8")

# Headings to be dropped from the final answer
_DROP_SECTION_PATTERNS = [
    r"(remaining\s+)?uncertainty",
    r"(overall\s+)?confidence",
    r"confidence\s+level",
    r"contradictions(\s+(found|and\s+unresolved\s+tensions?))?",
    r"unresolved\s+tensions?",
    r"supporting\s+evidence",
    r"evidence(\s+summary)?",
    r"source\s+evaluation",
    r"evidence\s+(assessment|summary)",
    r"sources?(\s+consulted)?",
    r"references",
    r"citations",
]

# Headings to be retained in the final answer
_UNWRAP_HEADING_PATTERNS = [
    r"synthesis\s+answer(\s+to\s+(the\s+)?original\s+question)?",
    r"main\s+findings",
    r"findings",
    r"final\s+answer",
    r"answer",
]


def _is_heading(line: str) -> tuple[bool, int | None, str]:
    """Return (is_heading, level, text), level is # count (1-6) for ATX,
    or 0 for bolded standalone lines, text is the heading text stripped 
    of markers and leading numbers/punctuation.
    """
    stripped = line.strip()

    m = re.match(r"^(#{1,6})\s+(.+?)\s*$", stripped)
    if m:
        return True, len(m.group(1)), _normalize_heading_text(m.group(2))

    m = re.match(r"^\*\*(.+?)\*\*\s*:?\s*$", stripped)
    if m:
        return True, 0, _normalize_heading_text(m.group(1))
    return False, None, ""


def _normalize_heading_text(text: str) -> str:
    return re.sub(r"^\s*\d+[.)]\s*", "", text).strip().lower()


def _strip_forbidden_sections(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        is_h, level, heading_text = _is_heading(lines[i])
        if is_h and any(re.fullmatch(p, heading_text) for p in _DROP_SECTION_PATTERNS):
            j = i + 1
            while j < len(lines):
                next_is_h, next_level, _ = _is_heading(lines[j])
                if next_is_h:
                    if level == 0 or next_level == 0 or next_level <= level:
                        break
                j += 1
            i = j
            continue
        if is_h and any(re.fullmatch(p, heading_text) for p in _UNWRAP_HEADING_PATTERNS):
            i += 1
            continue
        out.append(lines[i])
        i += 1
    collapsed: list[str] = []
    blank_run = 0
    for line in out:
        if line.strip() == "":
            blank_run += 1
            if blank_run <= 1:
                collapsed.append(line)
        else:
            blank_run = 0
            collapsed.append(line)
    while collapsed and not collapsed[-1].strip():
        collapsed.pop()
    while collapsed and not collapsed[0].strip():
        collapsed.pop(0)
    return "\n".join(collapsed)


class SynthesizerAgent(BaseAgent):
    """The agent that synthesizes multiple research findings into a single coherent answer"""

    def __init__(self, llm_client: LLMClient, api_token: str | None = None) -> None:
        super().__init__(name="synthesizer", description="Synthesizes multiple findings into a coherent answer")
        self.llm_client = llm_client
        self.api_token = api_token

    async def execute(self, query: str, state: ResearchState | None = None, sub_question_index: int = 0) -> str:
        raw = await self.llm_client.generate(
            query,
            api_token=self.api_token,
            system=_SYSTEM_PROMPT,
            max_tokens=4096,
        )
        return _strip_forbidden_sections(raw)

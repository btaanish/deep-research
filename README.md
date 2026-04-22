# Multi-Agent Deep Research System

This is a **multi-agent research orchestration system** that turns a single user query into an iterative investigation pipeline and streams progress back to the UI in real time using **SSE**.

---

## Architecture

### 1) API layer

- `GET /health` returns a simple liveness payload.
- `POST /research` starts the research pipeline and returns a `text/event-stream` response.
- The route creates an async queue and callback bridge, then streams events in SSE format:
  - `status` (human-friendly step updates)
  - `state_update` (intermediate structured state snapshots)
  - `result` (final synthesized answer)
  - `error` (pipeline failures)

### 2) Orchestration layer

`ResearchOrchestrator` drives the full loop:

1. **Decompose** the original query into 2–4 sub-questions.
2. **Dispatch parallel agents** per sub-question (retrieval/context/counterexample/gap detection).
3. **Aggregate evidence** into shared `ResearchState`.
4. **Detect and resolve contradictions** across collected evidence.
5. **Replan** (optionally refine/add sub-questions) for another iteration.
6. **Synthesize** all accumulated material into a final answer.

The orchestrator emits streaming events throughout this process.

### 3) Agent layer

Current agent roles:

- `RetrievalAgent` — web-search-assisted fresh information gathering.
- `ContextAgent` — background/context framing.
- `CounterexampleAgent` — opposing evidence and failure cases.
- `GapDetectionAgent` — missing information and unresolved areas.
- `PlannerAgent` — iterative sub-question refinement.
- `ContradictionResolverAgent` — contradiction adjudication.
- `SynthesizerAgent` — final answer composition + section cleanup.

Most agents load their behavioral instructions from colocated Markdown prompt files (e.g., `retrieval_agent.md`, `synthesizer.md`).

### 4) Shared runtime state

`ResearchState` is the in-memory backbone for a run:

- sub-questions + per-sub-question status
- gathered evidence records
- confidence tracking
- unresolved issues and next actions
- contradiction records
- exploration angles

This state is serializable and used for streaming updates to the frontend.

### 5) LLM usage abstraction

`LLMClient` wraps all the Anthropic async calls with:

- model selection defaults
- concurrency limiting via the semaphore(runs with the basic tier)
- prompt forwarding
- text-block extraction from responsesRecurrent Query memory locally to seek further clarifications if some aspects of the intial result were unsatisfactory
---
## Add On

Recurrent Query memory locally to seek further clarifications if some aspects of the intial result were unsatisfactory.

---
### Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run server

```bash
uvicorn src.main:app --reload
```

Then open: `http://127.0.0.1:8000`

Users can then pass the Claude `api_token` with the required research query.

## AI contribution and verification

- **Delegated to AI**
  - Initial drafts and iterative refinements of agent behavior descriptions and prompt text in `src/agents/*.md` (using in-context task examples and follow-up edits).
  - Parts of the frontend interaction scaffolding and UX text in `static/` (progress phrasing, result actions, and stream display logic).
  - Documentation expansion and wording iterations in this README.

- **Written by hand**
  - Core orchestration and control flow decisions (`ResearchOrchestrator`, iteration boundaries, contradiction and replanning flow).
  - API shape and stream contract decisions (`/research`, SSE frame structure, event lifecycle).
  - Final review edits for clarity, consistency, and role boundaries between agents.

- **Verification**
  - **Behavioral verification by run-throughs:** agent prompts were validated by repeated research runs across varied query types to confirm they follow role boundaries and produce usable outputs.
  - **Program checks:** Python compile checks and pytest runs were used to catch regressions and ensure import(runtime) integrity.
  - **Review:** outputs were inspected for general factual structure, overall clarity, and non-leakage of internal process metadata into the final synthesized answer.

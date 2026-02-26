"""Paper Config Agent — extracts MD simulation settings from published papers.

Workflow
--------
1. Accept an arXiv ID, DOI, title, or keyword search query
2. Locate and download the paper (Semantic Scholar or arXiv)
3. Extract the Methods section text via pdfplumber
4. Use Claude to parse structured MD settings (GROMACS + PLUMED)
5. Return a clear structured summary ready for the user to apply
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from langchain_core.tools import tool

from md_agent.agents.base import build_executor, stream_executor, sync_run
from md_agent.tools.paper_tools import MDSettingsExtractor, PaperRetriever

# ── Singleton helpers (shared across tool calls in one session) ────────

_retriever = PaperRetriever()
_extractor: MDSettingsExtractor | None = None  # lazy — needs Anthropic client


def _get_extractor() -> MDSettingsExtractor:
    global _extractor
    if _extractor is None:
        import anthropic
        _extractor = MDSettingsExtractor(anthropic.Anthropic())
    return _extractor


# ── Tools ──────────────────────────────────────────────────────────────

@tool
def search_papers(query: str) -> str:
    """Search Semantic Scholar for MD-related papers matching a keyword query.
    Returns a JSON list of up to 5 papers with title, abstract, authors, year, and PDF URL.
    """
    results = _retriever.search_semantic_scholar(query, limit=5)
    return json.dumps(results, default=str, indent=2)


@tool
def fetch_arxiv_paper(arxiv_id: str) -> str:
    """Fetch paper metadata from arXiv by paper ID (e.g. '2301.12345' or '2301.12345v2').
    Returns title, abstract, PDF URL, authors, published date, and arXiv categories.
    """
    result = _retriever.fetch_arxiv_paper(arxiv_id)
    return json.dumps(result, default=str, indent=2)


@tool
def download_and_read_paper(pdf_url: str) -> str:
    """Download a paper PDF from a URL and extract the Methods section text (up to 30 000 chars).
    Focuses on the Methods / Simulation Details section where MD parameters are described.
    """
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        _retriever.download_pdf(pdf_url, str(tmp_path))
        text = _retriever.extract_text_from_pdf(str(tmp_path))
        return text[:30_000] if len(text) > 30_000 else text
    finally:
        tmp_path.unlink(missing_ok=True)


@tool
def extract_md_settings_from_paper(paper_text: str, paper_title: str = "") -> str:
    """Use Claude to parse structured MD simulation settings from paper text.
    Returns a JSON object with gromacs, plumed, and system sections.
    All values are unit-normalised to GROMACS conventions (ps, nm, kJ/mol, K).
    """
    result = _get_extractor().extract_md_settings_from_text(paper_text, paper_title=paper_title)
    return json.dumps(result, default=str, indent=2)


TOOLS = [search_papers, fetch_arxiv_paper, download_and_read_paper, extract_md_settings_from_paper]

# ── System prompt ──────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a specialist in extracting MD simulation parameters from scientific papers.

## Your mission
Given a paper identifier (arXiv ID, DOI, title, or search query):
1. If an arXiv ID is provided (e.g. "2301.12345"), use `fetch_arxiv_paper` directly
2. Otherwise use `search_papers` to find the most relevant paper
3. Download and read the full paper using `download_and_read_paper`
4. Extract all MD parameters using `extract_md_settings_from_paper`
5. Present a clear, organised summary

## Output format
After extraction, produce a well-structured summary with these sections:
- **System**: molecule, force field, water model, box type, number of atoms
- **Sampling method**: metadynamics / umbrella / steered / plain MD
- **GROMACS parameters**: integrator, dt, nsteps, temperature, pressure, cutoffs, constraints
- **PLUMED / CVs**: collective variables with atom indices, bias parameters (height, sigma, pace, biasfactor)
- **Settings to confirm**: parameters that were ambiguous or not found in the paper

## Critical rules
- PLUMED atom indices are **1-based** (GROMACS convention after `pdb2gmx`)
- Time unit: ps | Distance: nm | Energy: kJ/mol | Temperature: K | Pressure: bar
- Flag clearly if a required parameter was NOT found in the paper
"""


# ── Agent class ────────────────────────────────────────────────────────

class PaperConfigAgent:
    """LangChain specialist agent that extracts MD settings from papers."""

    def __init__(self) -> None:
        self.executor = build_executor(SYSTEM_PROMPT, TOOLS, max_iterations=10)

    def run(self, query: str) -> str:
        """Synchronous run — returns final text output."""
        return sync_run(self.executor, query)

    async def astream(self, query: str):
        """Async streaming — yields SSE event dicts."""
        async for event in stream_executor(self.executor, query):
            yield event

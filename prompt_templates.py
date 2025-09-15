from __future__ import annotations
from typing import Dict

# Language-specific starter templates
TEMPLATES: Dict[str, str] = {
    "VB/VB.NET": "Analyze repo: architecture, forms/classes, data access, sequence diagram, modernization plan to .NET 8.",
    "XML": "Analyze XML configs: modules/features they drive, dependencies, potential migration to YAML/properties.",
    "Markdown": "Summarize docs: key architectural decisions and constraints.",
    "Other": "Analyze repo: architecture, key modules, interfaces, sequence diagram, modernization plan.",
}

def pick_template(lang: str) -> str:
    return f"""You are a reverse engineer. Summarize {lang} code into documentation:
- Purpose
- Key modules
- Dependencies
- Mermaid diagrams if relevant
"""

# Generic doc prompt
DOC_PROMPT = """You are an expert software architect and technical writer.
Using the provided repository context, produce Markdown with:
1) Executive summary
2) Structure & tech stack
3) Domain model (Mermaid classDiagram)
4) Runtime flow (Mermaid sequenceDiagram)
5) APIs, data, quality/ops
6) Risks & modernization roadmap"""

def doc_prompt_for_language(language: str) -> str:
    return DOC_PROMPT

# Focused documentation prompts (simplified)
ARCHITECTURE_DOC_PROMPT = """Generate a high-level architecture description in Markdown.
Include: context, modules, components, dependencies, and a mermaid flowchart diagram.
"""

CLASS_DIAGRAM_PROMPT = """Generate a class diagram (mermaid classDiagram) for the main entities.
"""

SEQUENCE_DIAGRAM_PROMPT = """Generate a sequence diagram (mermaid sequenceDiagram) showing user → system flow.
"""

DATA_MODEL_PROMPT = """Generate a data model description with a mermaid erDiagram.
"""

API_SPEC_PROMPT = """Generate a summary of APIs in OpenAPI-like YAML, with endpoints, methods, and schemas.
"""

MIGRATION_PROMPT_FOCUSED = """Generate a modernization plan:
- Current vs target architecture
- Migration phases
- Risks and mitigations
- Diagrams where possible
"""

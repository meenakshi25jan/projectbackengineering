# Heuristic Reverse-Engineering Summary
Confidence: 10%

You are an expert software architect and technical writer.
Using the provided repository context (file inventory + excerpts), produce a single Markdown document containing:

# 1) Executive Summary
- Purpose and business context (inferred from code)
- Architecture overview (text + bullet points)

# 2) Project Structure & Technology Stack
- Languages, frameworks, build tools
- Key modules/folders and responsibilities

# 3) Domain Model (Classes / Data Structures)
- List important classes/types (attributes & responsibilities)
- Show a Mermaid class diagram:
```mermaid
classDiagram
%% Add classes and relationships here
```
# 4) Runtime & Request Flow
- Describe primary flows (login, core business use case)
- Show a Mermaid sequence diagram:
```mermaid
sequenceDiagram
%% Participants & messages here
```

# 5) API Surface (if applicable)
# 6) Data & Persistence
# 7) Quality, Observability & Operations
# 8) Risks & Modernization Roadmap

Next Steps:
- Static analyzers per language
- Unit tests for critical modules
- CI/CD and modernization roadmap

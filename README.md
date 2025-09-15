
# ReverseGenAI Migration Suite

## Quick Start
```bash
python -m venv .venv
# Windows PowerShell:
# .\.venv\Scripts\Activate.ps1
# macOS/Linux:
# . .venv/bin/activate

pip install -r requirements.txt

# Optional: LLM and rendering services
# $env:OPENAI_API_KEY="sk-..."           # Windows PowerShell
# export OPENAI_API_KEY="sk-..."         # Bash/Zsh
# export KROKI_URL="https://kroki.io"
# export PLANTUML_SERVER="http://www.plantuml.com/plantuml/png"

python app.py
# Open http://127.0.0.1:5000
```

## Outputs
- `report.json` — scan results, language summary, deep analysis, API heuristics
- `ReverseDoc.md` — executive summary, structure, **Mermaid class & sequence diagram** scaffolds
- `MigrationPlan.md` — target architecture, phased plan, risks, data migration
- `APIs.md` — heuristic endpoints list (if detected)
- `diagrams/*.png` — rendered Mermaid/PlantUML images
- `export-bundle-<run_id>.zip` — everything above

## Notes
- Without `OPENAI_API_KEY`, the suite still works using a heuristic analyzer.
- Diagram rendering requires Internet (Kroki/PlantUML). I can make an offline renderer if needed.

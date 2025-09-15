from __future__ import annotations

import io
import json
import os
import pathlib
import re
import urllib.request
import zipfile
import datetime
import zlib
from typing import List, Dict

from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, flash

from detectors import scan_tree, summarize_by_language, FileInfo
from prompt_templates import (
    pick_template,
    doc_prompt_for_language,
    ARCHITECTURE_DOC_PROMPT,
    CLASS_DIAGRAM_PROMPT,
    SEQUENCE_DIAGRAM_PROMPT,
    DATA_MODEL_PROMPT,
    API_SPEC_PROMPT,
    MIGRATION_PROMPT_FOCUSED,
)
from genai import llm_analyze, generate_markdown_doc
import markdown as mdmod  # from requirements.txt

APP = Flask(__name__)
APP.secret_key = "interactive-secret"
BASE_DIR = pathlib.Path(__file__).parent.resolve()
RUNS_DIR = BASE_DIR / "runs"
UPLOADS_DIR = BASE_DIR / "uploads"
for d in (RUNS_DIR, UPLOADS_DIR):
    d.mkdir(parents=True, exist_ok=True)

# -------------------------
# Utilities
# -------------------------
def unzip_to(path_zip: str, out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    with zipfile.ZipFile(path_zip, "r") as z:
        z.extractall(out_dir)
    return out_dir


def build_context(files: List[FileInfo]) -> str:
    top = sorted(files, key=lambda f: f.lines, reverse=True)[:50]
    parts = ["# File Inventory (Top by LOC)"]
    for f in top:
        parts.append(f"- {f.relpath} ({f.language}, {f.lines} lines)")
    return "\n".join(parts)


def _load_run(run_id: str):
    run_dir = RUNS_DIR / run_id
    if not run_dir.exists():
        return None, None
    with open(run_dir / "report.json", "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return run_dir, data


def _write_doc(run_dir: pathlib.Path, name: str, content: str) -> pathlib.Path:
    p = run_dir / name
    p.write_text(content, encoding="utf-8")
    return p

# ---- PlantUML helpers (for PNG via public server) ----
def _deflate(data: bytes) -> bytes:
    compressor = zlib.compressobj(level=9, wbits=-15)
    return compressor.compress(data) + compressor.flush()


def _plantuml_encode(plantuml_text: str) -> str:
    data = _deflate(plantuml_text.encode("utf-8"))

    def e6(b: int) -> str:
        return "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"[b]

    res: list[str] = []
    i = 0
    while i < len(data):
        b1 = data[i]
        b2 = data[i + 1] if i + 1 < len(data) else 0
        b3 = data[i + 2] if i + 2 < len(data) else 0
        i += 3
        c1 = (b1 >> 2) & 0x3F
        c2 = ((b1 & 3) << 4) | ((b2 >> 4) & 0xF)
        c3 = ((b2 & 0xF) << 2) | ((b3 >> 6) & 0x3)
        c4 = b3 & 0x3F
        res += [e6(c1), e6(c2), e6(c3), e6(c4)]
    return "".join(res)

# -------------------------
# Routes
# -------------------------
@APP.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "zipfile" not in request.files or request.files["zipfile"].filename == "":
            flash("Please choose a .zip to upload")
            return redirect(url_for("index"))

        f = request.files["zipfile"]
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        run_dir = RUNS_DIR / ts
        extracted = run_dir / "extracted"
        uploaded = run_dir / "uploaded.zip"

        run_dir.mkdir(parents=True, exist_ok=True)
        f.save(str(uploaded))
        unzip_to(str(uploaded), str(extracted))

        files = scan_tree(str(extracted))
        summary = summarize_by_language(files)
        lang_prompts = {lang: pick_template(lang) for lang in summary.keys()}
        context = build_context(files)
        analysis = llm_analyze("architect", context)

        data = {
            "summary": summary,
            "files": [fi.__dict__ for fi in files],
            "context": context,
            "analysis": analysis,
            "lang_prompts": lang_prompts,
        }
        with open(run_dir / "report.json", "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

        return redirect(url_for("dashboard", run_id=ts))

    return render_template("index.html")


@APP.route("/dashboard/<run_id>")
def dashboard(run_id: str):
    run_dir = RUNS_DIR / run_id
    if not run_dir.exists():
        return "Run not found", 404
    with open(run_dir / "report.json", "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return render_template("dashboard.html", data=data, run_id=run_id)


@APP.route("/download/<run_id>")
def download_report(run_id: str):
    run_dir = RUNS_DIR / run_id
    return send_file(run_dir / "report.json", as_attachment=True, download_name=f"report-{run_id}.json")


@APP.route("/analyze_prompt/<lang>", methods=["POST"])
def analyze_prompt(lang: str):
    run_id = request.form.get("run_id", "").strip()
    prompt = request.form.get("prompt", "").strip()
    if not run_id or not prompt:
        return jsonify({"error": "Missing run_id or prompt"}), 400

    run_dir = RUNS_DIR / run_id
    if not run_dir.exists():
        return jsonify({"error": "Run not found"}), 404

    with open(run_dir / "report.json", "r", encoding="utf-8") as fh:
        data = json.load(fh)

    context = data.get("context", "")
    md = generate_markdown_doc(context, prompt, system="You are a world-class software architect and reverse-engineer.")
    slug = re.sub(r"[^a-z0-9]+", "-", lang.lower()).strip("-")
    out_name = f"ReverseDoc-{slug}.md"
    (run_dir / out_name).write_text(md, encoding="utf-8")
    return jsonify({"ok": True, "doc": out_name, "preview": md[:1200]})


@APP.route("/download_custom_doc/<run_id>/<lang>")
def download_custom_doc(run_id: str, lang: str):
    run_dir = RUNS_DIR / run_id
    slug = re.sub(r"[^a-z0-9]+", "-", lang.lower()).strip("-")
    path = run_dir / f"ReverseDoc-{slug}.md"
    if not path.exists():
        return "Document not generated yet", 404
    return send_file(path, as_attachment=True, download_name=path.name)


@APP.route("/generate_full_docs/<run_id>", methods=["POST"])
def generate_full_docs(run_id: str):
    run_dir, data = _load_run(run_id)
    if not run_dir:
        return jsonify({"error": "Run not found"}), 404

    context = data.get("context", "")

    docs: Dict[str, str] = {}
    docs["Architecture.md"] = generate_markdown_doc(context, ARCHITECTURE_DOC_PROMPT, system="You are a senior software architect.")
    docs["ClassDiagram.md"] = generate_markdown_doc(context, CLASS_DIAGRAM_PROMPT, system="You are a senior software architect.")
    docs["SequenceDiagram.md"] = generate_markdown_doc(context, SEQUENCE_DIAGRAM_PROMPT, system="You are a senior software architect.")
    docs["DataModel.md"] = generate_markdown_doc(context, DATA_MODEL_PROMPT, system="You are a data/DB architect.")
    docs["APIs.md"] = generate_markdown_doc(context, API_SPEC_PROMPT, system="You are an API designer.")
    docs["MigrationPlan.md"] = generate_markdown_doc(context, MIGRATION_PROMPT_FOCUSED, system="You are an enterprise modernization architect.")

    for name, content in docs.items():
        _write_doc(run_dir, name, content)

    return jsonify({"ok": True, "files": list(docs.keys())})


@APP.route("/download_docfile/<run_id>/<name>")
def download_docfile(run_id: str, name: str):
    run_dir = RUNS_DIR / run_id
    path = run_dir / name
    if not path.exists():
        return "File not found", 404
    return send_file(path, as_attachment=True, download_name=name)


@APP.route("/export_bundle/<run_id>")
def export_bundle(run_id: str):
    run_dir = RUNS_DIR / run_id
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as z:
        for fname in os.listdir(run_dir):
            if fname.endswith(".md") or fname == "report.json":
                z.write(run_dir / fname, fname)
    mem.seek(0)
    return send_file(mem, as_attachment=True, download_name=f"bundle-{run_id}.zip")


# ---- HTML doc viewer: render Mermaid client-side and PlantUML as <img> ----
@APP.route("/doc_view/<run_id>/<name>")
def doc_view(run_id: str, name: str):
    run_dir = RUNS_DIR / run_id
    md_path = run_dir / name
    if not md_path.exists():
        return "Document not found", 404
    md_text = md_path.read_text(encoding="utf-8", errors="ignore")

    # Convert code fences: mermaid -> <div class="mermaid">, plantuml -> <img src=...>
    def repl_mermaid(m: re.Match[str]) -> str:
        code = m.group(1)
        return f'<div class="mermaid">{code}</div>'

    idx = {"n": 0}
    def repl_plantuml(m: re.Match[str]) -> str:
        idx["n"] += 1
        return (
            '<img alt="PlantUML diagram" src="'
            + url_for("uml_img", run_id=run_id, name=name, idx=idx["n"])
            + '">'
        )

    body = re.sub(r"```mermaid\s+([\s\S]*?)```", repl_mermaid, md_text, flags=re.IGNORECASE)
    body = re.sub(r"```plantuml\s+([\s\S]*?)```", repl_plantuml, body, flags=re.IGNORECASE)

    html_body = mdmod.markdown(body, extensions=["fenced_code", "tables", "toc"])
    return render_template("doc_view.html", run_id=run_id, name=name, body=html_body)


@APP.route("/uml_img/<run_id>/<name>/<int:idx>")
def uml_img(run_id: str, name: str, idx: int):
    run_dir = RUNS_DIR / run_id
    md_path = run_dir / name
    if not md_path.exists():
        return "Not found", 404
    md_text = md_path.read_text(encoding="utf-8", errors="ignore")

    matches = list(re.finditer(r"```plantuml\s+([\s\S]*?)```", md_text, flags=re.IGNORECASE))
    if idx <= 0 or idx > len(matches):
        return "No such diagram", 404
    code = matches[idx - 1].group(1).strip()
    encoded = _plantuml_encode(code)
    # Use HTTPS to avoid mixed-content blocking
    url = f"https://www.plantuml.com/plantuml/png/{encoded}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        png = resp.read()
    return png, 200, {"Content-Type": "image/png"}

# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    print("Starting Flask app…")
    APP.run(debug=True)

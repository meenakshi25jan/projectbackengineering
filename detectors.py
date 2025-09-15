from __future__ import annotations
import os, pathlib
from dataclasses import dataclass
from typing import Dict, List

# Rich language mapping for LLM context
LANG_BY_EXT = {
    ".py": "Python", ".java": "Java", ".kt": "Kotlin", ".cs": "C#",
    ".js": "JavaScript", ".jsx": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript",
    ".go": "Go", ".rb": "Ruby", ".php": "PHP", ".rs": "Rust", ".swift": "Swift",
    ".c": "C", ".h": "C/C++ Header", ".hpp": "C++ Header", ".cpp": "C++",
    ".scala": "Scala", ".vb": "VB/VB.NET", ".bas": "VB6", ".frm": "VB6 Form",
    ".xml": "XML", ".md": "Markdown", ".json": "JSON", ".yml": "YAML", ".yaml": "YAML",
    ".sh": "Shell", ".bat": "Batch", ".ps1": "PowerShell",
    ".html": "HTML", ".css": "CSS"
}

SKIP_DIRS = {
    ".git", ".svn", ".hg",
    "node_modules", "dist", "build",
    ".gradle", ".idea", ".vscode", "__pycache__"
}

@dataclass
class FileInfo:
    relpath: str
    language: str
    lines: int
    size_bytes: int

def detect_language(filename: str) -> str:
    name = filename.lower()
    root, ext = os.path.splitext(name)
    if name == "dockerfile":
        return "Dockerfile"
    return LANG_BY_EXT.get(ext, "Other")

def count_lines(filepath: str, max_bytes: int = 2_000_000) -> int:
    """Count lines safely; skip giant binaries > max_bytes."""
    try:
        if os.path.getsize(filepath) > max_bytes:
            return 0
        with open(filepath, "rb") as f:
            return f.read().count(b"\n") + 1
    except Exception:
        return 0

def scan_tree(root: str) -> List[FileInfo]:
    """Walk project tree, skip vendor dirs, return FileInfo list."""
    out: List[FileInfo] = []
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]  # skip unwanted dirs
        for fn in fns:
            full = os.path.join(dp, fn)
            rel = os.path.relpath(full, root)
            lang = detect_language(fn)
            try:
                size = os.path.getsize(full)
            except Exception:
                size = 0
            lines = count_lines(full)
            out.append(FileInfo(rel, lang, lines, size))
    return out

def summarize_by_language(files: List[FileInfo]) -> Dict[str, Dict[str, int]]:
    """Summarize counts per language for LLM prompts."""
    summary: Dict[str, Dict[str, int]] = {}
    for fi in files:
        e = summary.setdefault(fi.language, {"files": 0, "lines": 0, "bytes": 0})
        e["files"] += 1
        e["lines"] += fi.lines
        e["bytes"] += fi.size_bytes
    return summary

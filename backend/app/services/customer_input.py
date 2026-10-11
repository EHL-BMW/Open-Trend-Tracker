"""Turn an uploaded customer document into complaint rows and a backend plot."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from pypdf import PdfReader  # noqa: E402

from app.mapping import Mapper  # noqa: E402
from app.paths import RUNTIME_DIR  # noqa: E402

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
SENTIMENT_RULES = {
    "defect": ("broken", "defect", "failure", "failed", "crash", "fault", "doesn't work", "not work"),
    "difficult_to_use": ("difficult", "confusing", "hard to", "annoying", "awkward", "complicated", "slow"),
    "want": ("want", "wish", "need", "would like", "missing", "please add"),
    "like": ("love", "like", "great", "excellent", "happy", "comfortable", "easy to use"),
}


def extract_text(filename: str, content: bytes) -> str:
    """Extract text from TXT/MD/CSV/JSON/PDF/DOCX without trusting the filename path."""
    if len(content) > MAX_UPLOAD_BYTES:
        raise ValueError("document exceeds the 10 MB upload limit")
    suffix = Path(filename).suffix.casefold()
    if suffix in {".txt", ".md"}:
        return content.decode("utf-8-sig", errors="replace")
    if suffix == ".csv":
        rows = csv.reader(io.StringIO(content.decode("utf-8-sig", errors="replace")))
        return "\n".join(" | ".join(cell for cell in row if cell.strip()) for row in rows)
    if suffix == ".json":
        value = json.loads(content.decode("utf-8-sig"))
        return _json_text(value)
    if suffix == ".pdf":
        return "\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(content)).pages)
    if suffix == ".docx":
        with zipfile.ZipFile(io.BytesIO(content)) as document:
            xml = document.read("word/document.xml")
        root = ElementTree.fromstring(xml)
        return "\n".join(node.text or "" for node in root.iter() if node.tag.endswith("}t"))
    raise ValueError("supported document types: .txt, .md, .csv, .json, .pdf, .docx")


def _json_text(value) -> str:
    if isinstance(value, dict):
        return "\n".join(_json_text(item) for item in value.values())
    if isinstance(value, list):
        return "\n".join(_json_text(item) for item in value)
    return str(value) if value is not None else ""


def _sentiment(text: str) -> str:
    lowered = text.casefold()
    for label in ("defect", "difficult_to_use", "want", "like"):
        if any(term in lowered for term in SENTIMENT_RULES[label]):
            return label
    return "mention"


def complaint_rows(text: str, mapper: Mapper | None = None) -> list[dict]:
    """Split text into traceable statements and map each to taxonomy + sentiment."""
    mapper = mapper or Mapper()
    statements = [part.strip(" \t•-") for part in re.split(r"(?:\r?\n)+|(?<=[.!?])\s+", text) if part.strip()]
    rows = []
    for index, statement in enumerate(statements, start=1):
        feature_id, mapped_by = mapper.lookup(statement)
        info = mapper.attributes.get(feature_id or "", {})
        rows.append({
            "id": index,
            "complaint": statement,
            "sentiment": _sentiment(statement),
            "feature_id": feature_id,
            "feature": info.get("name", "Unclassified"),
            "category": mapper.categories.get(info.get("category", ""), "Unclassified"),
            "mapped_by": mapped_by,
        })
    return rows


def _plot(rows: list[dict], output: Path) -> None:
    counts = Counter(row["feature"] for row in rows if row["sentiment"] != "like")
    ranked = counts.most_common(12)
    fig, ax = plt.subplots(figsize=(9, max(3.2, len(ranked) * 0.42 + 1.5)), constrained_layout=True)
    if ranked:
        labels, values = zip(*reversed(ranked))
        ax.barh(labels, values, color="#2f78a7")
        ax.set_xlabel("Customer statements")
        ax.grid(axis="x", alpha=0.22)
    else:
        ax.text(0.5, 0.5, "No complaint statements detected", ha="center", va="center", transform=ax.transAxes)
        ax.set_axis_off()
    ax.set_title("Customer complaints by mapped feature", loc="left", fontweight="bold")
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=160)
    plt.close(fig)


def process_document(filename: str, content: bytes) -> dict:
    text = extract_text(filename, content)
    rows = complaint_rows(text)
    document_id = hashlib.sha256(content).hexdigest()[:16]
    output_dir = RUNTIME_DIR / "customer-input" / document_id
    figure = output_dir / "complaints.png"
    _plot(rows, figure)
    sentiments = Counter(row["sentiment"] for row in rows)
    features = Counter(row["feature"] for row in rows)
    result = {
        "document_id": document_id,
        "filename": Path(filename).name,
        "statement_count": len(rows),
        "sentiment_counts": dict(sentiments),
        "feature_counts": dict(features.most_common()),
        "complaints": rows,
        "figure_url": f"/api/artifacts/customer-input/{document_id}/complaints.png",
        "method": "deterministic sentence splitting, keyword sentiment rules, and taxonomy mapping",
        "caveat": "Unclassified statements should be reviewed and added to the taxonomy when appropriate.",
    }
    (output_dir / "result.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return result

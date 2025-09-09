from pathlib import Path
from fastapi import APIRouter, HTTPException
import re

router = APIRouter(prefix="/api/doc-titles", tags=["Document Titles"])

@router.get("/docs/titles", response_model=list)
def get_docs_titles():
    """Return document names and their H1-H3 titles from the docs folder."""
    try:
        base_path = Path(__file__).resolve().parents[4]
        docs_path = base_path / "docs"
        result = []
        if not docs_path.is_dir():
            raise FileNotFoundError("Docs directory not found")
        for md_file in sorted(docs_path.glob("*.md")):
            titles = []
            for line in md_file.read_text(encoding="utf-8").splitlines():
                match = re.match(r"^(#{1,3})\s+(.*)", line)
                if match:
                    level = len(match.group(1))
                    title = match.group(2).strip()
                    titles.append({"level": level, "title": title})
            result.append({"document": md_file.name, "titles": titles})
        return result
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(e))

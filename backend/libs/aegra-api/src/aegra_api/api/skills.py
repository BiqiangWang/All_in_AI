"""Skills API endpoints."""
import sys
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

# Add project root to path for agents package
_project_root = Path(__file__).parent.parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


class SkillInfo(BaseModel):
    """Skill information."""
    name: str
    description: str
    triggers: list[str]
    path: str


def get_skills_metadata() -> list[dict]:
    """Scan skills directory and return metadata list."""
    import re

    skills_root = _project_root / "agents" / "skills"
    if not skills_root.exists():
        return []

    skills = []
    for skill_dir in skills_root.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        content = skill_md.read_text(encoding='utf-8')
        name = skill_dir.name
        description = ""
        triggers = []

        # Extract from first markdown heading
        heading_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if heading_match:
            description = heading_match.group(1).strip()

        skills.append({
            "name": name,
            "description": description,
            "triggers": triggers,
            "path": f"/{skill_dir.name}/"
        })

    return skills


router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=list[SkillInfo])
async def list_skills() -> list[SkillInfo]:
    """List all available skills.

    Returns:
        List of skill metadata including name, description, triggers, and path.
    """
    try:
        skills_data = get_skills_metadata()
        return [SkillInfo(**s) for s in skills_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load skills: {str(e)}")


@router.get("/{skill_name}/SKILL.md")
async def get_skill_content(skill_name: str) -> dict:
    """Get the SKILL.md content for a specific skill.

    Args:
        skill_name: Name of the skill directory

    Returns:
        Dict with skill_name and content
    """
    skill_path = _project_root / "agents" / "skills" / skill_name / "SKILL.md"
    if not skill_path.exists():
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")

    content = skill_path.read_text(encoding='utf-8')
    return {"skill_name": skill_name, "content": content}

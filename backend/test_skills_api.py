import pytest
from backend.agents.basic_agent import get_skills_metadata

def test_get_skills_metadata():
    """验证能正确扫描 skills 目录并返回元数据"""
    result = get_skills_metadata()
    assert isinstance(result, list)
    assert len(result) >= 4  # nuwa, elon-musk, trump, zhangxuefeng
    for skill in result:
        assert "name" in skill
        assert "description" in skill
        assert "triggers" in skill
        assert "path" in skill
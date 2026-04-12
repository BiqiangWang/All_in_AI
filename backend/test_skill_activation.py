import pytest
from backend.agents.basic_agent import extract_skill_names, load_skill_content

def test_extract_skill_names():
    """验证从消息中提取 skill 名称"""
    assert extract_skill_names("/nuwa 你好") == ["nuwa"]
    assert extract_skill_names("/nuwa /elon-musk 测试") == ["nuwa", "elon-musk"]
    assert extract_skill_names("没有skill命令") == []

def test_load_skill_content():
    """验证加载 skill 内容"""
    content = load_skill_content("nuwa")
    assert content is not None
    assert len(content) > 0

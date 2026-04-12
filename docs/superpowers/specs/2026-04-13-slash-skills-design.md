# Slash Skills 设计文档

## 概述

实现类似 Claude Code 的 `/skill` 命令功能，用户通过 `/` 快速引用预设的 skills。

## 架构

```
用户输入 "/nuwa xxx"
        ↓
前端：检测到 "/" → 显示下拉列表 → 用户选择 → 输入框变为 "/nuwa xxx"
        ↓
后端 API：GET /skills → 返回 skills 列表
        ↓
后端：接收消息 → 检测 "/skillname" → 自动加载 SKILL.md → 合并到 system prompt
```

## 后端实现

### 1. Skills 列表 API

**Endpoint:** `GET /skills`

**Response:**
```json
{
  "skills": [
    {
      "name": "nuwa",
      "description": "女娲造人：输入人名自动蒸馏思维方式",
      "triggers": ["女娲", "造skill", "蒸馏"]
    },
    {
      "name": "elon-musk",
      "description": "马斯克视角：分析商业决策和第一性原理",
      "triggers": ["马斯克", "elon"]
    }
  ]
}
```

**实现位置:** `backend/agents/basic_agent.py`

```python
from pathlib import Path

def get_available_skills() -> list[dict]:
    """Scan skills directory and return skill metadata."""
    skills_root = Path(__file__).parent.parent / "skills"
    skills = []
    for skill_dir in skills_root.iterdir():
        if skill_dir.is_dir():
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                # Parse SKILL.md frontmatter
                content = skill_md.read_text(encoding='utf-8')
                # Extract name and description from frontmatter
                # ...
                skills.append({
                    "name": skill_dir.name,
                    "description": "...",
                    "triggers": [...]
                })
    return skills
```

### 2. Skill 激活逻辑

**实现位置:** `backend/agents/basic_agent.py` 的 `create_basic_agent` 函数

当用户消息包含 `/skillname` 时：

```python
def extract_skill_commands(message: str) -> list[str]:
    """Extract skill names from message like '/nuwa /elon-musk'."""
    import re
    return re.findall(r'/(\w+)', message)

def load_skill_content(skill_name: str) -> str:
    """Load SKILL.md content for given skill name."""
    skill_path = skills_root / skill_name / "SKILL.md"
    if skill_path.exists():
        return skill_path.read_text(encoding='utf-8')
    return ""

# In message handling:
skill_commands = extract_skill_commands(user_message)
if skill_commands:
    for skill_name in skill_commands:
        skill_content = load_skill_content(skill_name)
        # Prepend skill content to system prompt
        system_prompt = skill_content + "\n\n" + base_system_prompt
```

## 前端实现

### 1. 新增组件

**文件:** `frontend/src/components/thread/SkillDropdown.tsx`

```tsx
interface Skill {
  name: string;
  description: string;
  triggers: string[];
}

interface SkillDropdownProps {
  skills: Skill[];
  filter: string;  // e.g., "nuwa" from "/nuwa"
  onSelect: (skill: Skill) => void;
  onClose: () => void;
}
```

### 2. 修改 Thread 组件

**文件:** `frontend/src/components/thread/index.tsx`

- 添加 `skills` state 从 API 获取
- 监听 textarea 的 `keyDown` 事件
- 检测到 `/` 时显示 SkillDropdown
- 下拉列表支持键盘导航（↑↓ 选择，回车确认，ESC 关闭）

### 3. API 调用

```typescript
const fetchSkills = async (): Promise<Skill[]> => {
  const res = await fetch('/skills');
  const data = await res.json();
  return data.skills;
};
```

## 文件变更清单

| 文件 | 操作 |
|------|------|
| `backend/agents/basic_agent.py` | 修改：添加 `get_available_skills()` 和 skill 激活逻辑 |
| `frontend/src/components/thread/SkillDropdown.tsx` | 新增：技能下拉组件 |
| `frontend/src/components/thread/index.tsx` | 修改：集成 SkillDropdown |

## 现有 Skills

| Name | 描述 |
|------|------|
| nuwa | 女娲造人：蒸馏思维方式 |
| elon-musk | 马斯克视角 |
| trump | 特朗普视角 |
| zhangxuefeng | 张雪峰视角 |

# Slash Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现通过 "/" 引用 skills 的功能，前端下拉列表选择 + 后端自动激活

**Architecture:**
- 后端：添加 `/skills` API 获取列表，消息处理时检测 `/skillname` 并加载 SKILL.md
- 前端：输入框监听 "/" 显示下拉列表，选择后填充输入框

**Tech Stack:** Python (FastAPI/Aegra), TypeScript (Next.js), React

---

## Task 1: 后端 - 添加 Skills 列表 API

**Files:**
- Modify: `backend/agents/basic_agent.py`

**Test:** `backend/test_skills_api.py`

- [ ] **Step 1: 创建测试文件**

```python
# backend/test_skills_api.py
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
```

- [ ] **Step 2: 运行测试验证失败**

Run: `cd D:\Dev\All_in_AI\backend && python -m pytest test_skills_api.py::test_get_skills_metadata -v`
Expected: FAIL - function not defined

- [ ] **Step 3: 实现 get_skills_metadata 函数**

在 `basic_agent.py` 末尾添加：

```python
def get_skills_metadata() -> list[dict]:
    """扫描 skills 目录，返回 skill 元数据列表"""
    import re
    from pathlib import Path

    skills_root = Path(__file__).parent.parent / "skills"
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

        # Parse frontmatter
        name = skill_dir.name
        description = ""
        triggers = []

        # Extract from first markdown heading as fallback
        heading_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if heading_match:
            description = heading_match.group(1).strip()

        # Extract name from frontmatter if present
        fm_name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
        if fm_name_match:
            name = fm_name_match.group(1).strip()

        skills.append({
            "name": name,
            "description": description,
            "triggers": triggers,
            "path": f"/{skill_dir.name}/"
        })

    return skills
```

- [ ] **Step 4: 运行测试验证通过**

Run: `cd D:\Dev\All_in_AI\backend && python -m pytest test_skills_api.py::test_get_skills_metadata -v`
Expected: PASS

- [ ] **Step 5: 提交**

```bash
cd D:\Dev\All_in_AI
git add backend/agents/basic_agent.py backend/test_skills_api.py
git commit -m "feat: add get_skills_metadata for skills listing"
```

---

## Task 2: 后端 - 添加 /skills API 路由

**Files:**
- Modify: `backend/start_aegra_v2.py`

**Test:** `backend/test_skills_endpoint.py`

- [ ] **Step 1: 创建测试文件**

```python
# backend/test_skills_endpoint.py
import pytest

def test_skills_endpoint():
    """验证 GET /skills 返回正确的 JSON"""
    # This test requires the running server
    import requests
    resp = requests.get("http://localhost:2026/skills")
    assert resp.status_code == 200
    data = resp.json()
    assert "skills" in data
    assert isinstance(data["skills"], list)
```

- [ ] **Step 2: 查看 Aegra 路由注册方式**

检查 `start_aegra_v2.py` 了解如何注册新路由

- [ ] **Step 3: 添加 /skills 路由**

在 `start_aegra_v2.py` 中添加：

```python
from fastapi import APIRouter

# 在 create_app() 之前添加
skills_router = APIRouter()

@skills_router.get("/skills")
async def get_skills():
    """返回所有可用 skills 的元数据"""
    from agents.basic_agent import get_skills_metadata
    return {"skills": get_skills_metadata()}

# 在 app = create_app() 之后，return 之前添加
app.include_router(skills_router)
```

- [ ] **Step 4: 验证 API 可用**

Run: `curl -s http://localhost:2026/skills | python -m json.tool`
Expected: `{"skills": [...]}`

- [ ] **Step 5: 提交**

```bash
git add backend/start_aegra_v2.py
git commit -m "feat: add GET /skills endpoint"
```

---

## Task 3: 后端 - 实现 Skill 激活逻辑

**Files:**
- Modify: `backend/agents/basic_agent.py`

**Test:** `backend/test_skill_activation.py`

- [ ] **Step 1: 创建测试文件**

```python
# backend/test_skill_activation.py
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
    assert "女娲" in content or "nuwa" in content.lower()
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest test_skill_activation.py -v`
Expected: FAIL - function not defined

- [ ] **Step 3: 实现 extract_skill_names 和 load_skill_content**

在 `get_skills_metadata` 之后添加：

```python
def extract_skill_names(text: str) -> list[str]:
    """从文本中提取 /skillname 格式的命令"""
    import re
    matches = re.findall(r'/([a-zA-Z0-9_-]+)', text)
    return matches

def load_skill_content(skill_name: str) -> str:
    """加载指定 skill 的 SKILL.md 内容"""
    from pathlib import Path
    skills_root = Path(__file__).parent.parent / "skills"
    skill_path = skills_root / skill_name / "SKILL.md"
    if skill_path.exists():
        return skill_path.read_text(encoding='utf-8')
    return ""

def activate_skills_in_message(message: str, system_prompt: str) -> str:
    """检测消息中的 skill 命令并激活对应的 skill 内容"""
    skill_names = extract_skill_names(message)
    if not skill_names:
        return system_prompt

    activated_content = []
    for skill_name in skill_names:
        content = load_skill_content(skill_name)
        if content:
            activated_content.append(content)

    if activated_content:
        return "\n\n".join(activated_content) + "\n\n" + system_prompt
    return system_prompt
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest test_skill_activation.py -v`
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add backend/agents/basic_agent.py backend/test_skill_activation.py
git commit -m "feat: add skill activation logic for /command extraction"
```

---

## Task 4: 前端 - 创建 SkillDropdown 组件

**Files:**
- Create: `frontend/src/components/thread/SkillDropdown.tsx`

**Test:** `frontend/src/components/thread/__tests__/SkillDropdown.test.tsx`

- [ ] **Step 1: 创建 SkillDropdown 组件**

```tsx
// frontend/src/components/thread/SkillDropdown.tsx
"use client";

import { useEffect, useRef } from "react";

export interface Skill {
  name: string;
  description: string;
  triggers: string[];
}

interface SkillDropdownProps {
  skills: Skill[];
  filter: string;  // e.g., "nuwa" from "/nuwa"
  position: { top: number; left: number };
  onSelect: (skill: Skill) => void;
  onClose: () => void;
}

export function SkillDropdown({
  skills,
  filter,
  position,
  onSelect,
  onClose,
}: SkillDropdownProps) {
  const ref = useRef<HTMLDivElement>(null);

  // Filter skills based on filter text
  const filteredSkills = skills.filter(
    (skill) =>
      skill.name.toLowerCase().includes(filter.toLowerCase()) ||
      skill.description.toLowerCase().includes(filter.toLowerCase())
  );

  // Handle click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        onClose();
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [onClose]);

  if (filteredSkills.length === 0) {
    return null;
  }

  return (
    <div
      ref={ref}
      className="absolute z-50 w-72 rounded-lg border bg-white shadow-lg"
      style={{ top: position.top + 36, left: position.left }}
    >
      <div className="max-h-64 overflow-y-auto p-1">
        {filteredSkills.map((skill) => (
          <button
            key={skill.name}
            className="flex w-full cursor-pointer items-start gap-2 rounded-md p-2 text-left hover:bg-gray-100"
            onClick={() => onSelect(skill)}
          >
            <span className="flex h-6 min-w-6 items-center justify-center rounded bg-primary/10 px-1 text-xs font-medium text-primary">
              /
            </span>
            <div className="flex-1 overflow-hidden">
              <div className="font-medium text-gray-900">{skill.name}</div>
              <div className="truncate text-sm text-gray-500">
                {skill.description}
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: 提交组件**

```bash
git add frontend/src/components/thread/SkillDropdown.tsx
git commit -m "feat: create SkillDropdown component"
```

---

## Task 5: 前端 - 集成 SkillDropdown 到 Thread

**Files:**
- Modify: `frontend/src/components/thread/index.tsx`

**Test:** `frontend/src/components/thread/__tests__/Thread.test.tsx`

- [ ] **Step 1: 添加 state 和 handler**

在 Thread 组件顶部添加 state：

```tsx
const [showSkillDropdown, setShowSkillDropdown] = useState(false);
const [skillFilter, setSkillFilter] = useState("");
const [skillPosition, setSkillPosition] = useState({ top: 0, left: 0 });
const [skills, setSkills] = useState<Skill[]>([]);
```

添加 fetchSkills 逻辑（useEffect 中调用 `/skills`）

- [ ] **Step 2: 添加 textarea 的 keyDown 监听**

```tsx
<textarea
  value={input}
  onChange={(e) => {
    const val = e.target.value;
    setInput(val);

    // Detect "/" to show skill dropdown
    if (val.endsWith("/") && !showSkillDropdown) {
      setShowSkillDropdown(true);
      setSkillFilter("");
      // Get cursor position for dropdown placement
      const rect = e.target.getBoundingClientRect();
      setSkillPosition({ top: rect.top, left: rect.left });
    } else if (showSkillDropdown) {
      // Update filter
      const lastSlashIndex = val.lastIndexOf("/");
      if (lastSlashIndex >= 0) {
        setSkillFilter(val.slice(lastSlashIndex + 1));
      }
    }
  }}
  onKeyDown={(e) => {
    // Handle keyboard navigation
    if (showSkillDropdown && e.key === "Escape") {
      setShowSkillDropdown(false);
    }
    // ... existing Enter handling
  }}
  // ... rest of props
/>
```

- [ ] **Step 3: 渲染 SkillDropdown**

在 textarea 下方添加：

```tsx
{showSkillDropdown && skills.length > 0 && (
  <SkillDropdown
    skills={skills}
    filter={skillFilter}
    position={skillPosition}
    onSelect={(skill) => {
      // Replace "/filter" with "/skillname "
      const lastSlashIndex = input.lastIndexOf("/");
      const newInput = input.slice(0, lastSlashIndex) + "/" + skill.name + " ";
      setInput(newInput);
      setShowSkillDropdown(false);
      setSkillFilter("");
    }}
    onClose={() => {
      setShowSkillDropdown(false);
      setSkillFilter("");
    }}
  />
)}
```

- [ ] **Step 4: 测试手动验证**

启动前端，输入 "/" 查看下拉列表是否显示

- [ ] **Step 5: 提交**

```bash
git add frontend/src/components/thread/index.tsx
git commit -m "feat: integrate SkillDropdown in Thread component"
```

---

## Task 6: 端到端测试

- [ ] **Step 1: 重启后端服务**

```bash
# Kill existing backend
taskkill /F /PID <pid>
# Start backend
cd backend && python start_aegra_v2.py
```

- [ ] **Step 2: 测试完整流程**

1. 启动前端：`cd frontend && pnpm dev`
2. 输入框输入 `/`
3. 验证下拉列表显示所有 skills
4. 点击选择 `/nuwa`
5. 输入框变为 `/nuwa `
6. 发送消息
7. 验证后端正确激活 nuwa skill

- [ ] **Step 3: 提交最终代码**

```bash
git add -A
git commit -m "feat: implement slash skills command support

- Add GET /skills API endpoint
- Add skill activation logic for /command detection
- Add SkillDropdown component for frontend
- Integrate skill selection in Thread component"
```

---

## 验证清单

- [ ] `GET /skills` 返回 skills 列表
- [ ] 输入 `/` 显示下拉列表
- [ ] 点击 skill 填充输入框
- [ ] 发送 `/nuwa 你好` 后端正确提取 skill 命令
- [ ] 后端加载 nuwa 的 SKILL.md 内容

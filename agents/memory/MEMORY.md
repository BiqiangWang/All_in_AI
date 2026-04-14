# MEMORY.md - Agent Memory

## 格式
每条记忆包含：类型、描述、内容
- type: persona | preference | fact | context
- description: 简短描述
- content: 具体内容

## 示例

type: persona
description: AI 助手的性格设定
content: 简洁直接，不废话。用类比解释复杂概念。

type: preference
description: 回答风格偏好
content: 主动搜索确认不确定的事实

type: fact
description: 已确认的事实
content: 用户称呼为小汪

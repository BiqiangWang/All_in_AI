# All_in_AI

基于 Aegra + Agent Chat UI + deepagents 构建的通用 LangChain Agent 对话平台。

## 快速启动

### 前置要求
- Docker Desktop 运行中（PostgreSQL）
- conda 环境 `langchain-next` 已激活
- pnpm 或 npm

### 启动后端（Aegra）

```bash
cd D:/Dev/All_in_AI/agents && conda run -n langchain-next aegra dev
```

### 启动前端

```bash
cd D:/Dev/All_in_AI/frontend && pnpm dev
```

访问 http://localhost:3000

## 一键启动

```bash
python D:/Dev/All_in_AI/start_all.py
```

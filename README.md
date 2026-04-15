# All_in_AI

基于 Aegra + Agent Chat UI + deepagents 构建的通用 LangChain Agent 对话平台。

## 快速启动

### 前置要求
- Docker Desktop 运行中
- conda 环境 `langchain-next`
- npm

### 1. 启动 PostgreSQL

```powershell
docker run -d --name all_in_ai_postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=aegra -p 5432:5432 postgres:16-alpine
```

### 2. 启动后端（Aegra）

```powershell
cd D:/Dev/All_in_AI/agents; conda run -n langchain-next aegra dev --no-db-check
```

### 3. 启动前端

```powershell
cd D:/Dev/All_in_AI/frontend; npm run dev
```

访问 http://localhost:3000

## 一键启动

```powershell
python D:/Dev/All_in_AI/start_all.py
```

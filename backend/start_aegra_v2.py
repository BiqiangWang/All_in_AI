# Enable UTF-8 mode on Windows
import os
os.environ['PYTHONUTF8'] = '1'

# Windows WindowsSelectorEventLoopPolicy - MUST be at the very top
import sys
if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import os
os.environ['DATABASE_URL'] = 'postgresql+asyncpg://postgres:postgres@localhost:5432/aegra'
os.environ['REDIS_BROKER_ENABLED'] = 'false'

import uvicorn
from aegra_api.main import app

# 添加 /skills 路由
@app.get("/skills")
async def get_skills():
    """返回所有可用 skills 的元数据"""
    from agents.basic_agent import get_skills_metadata
    return {"skills": get_skills_metadata()}

if __name__ == "__main__":
    config = uvicorn.Config(app, host="0.0.0.0", port=2026, loop="asyncio")
    server = uvicorn.Server(config)
    import asyncio
    asyncio.run(server.serve())

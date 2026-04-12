# Windows WindowsSelectorEventLoopPolicy
import sys
if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import os
import uvicorn

os.environ['DATABASE_URL'] = 'postgresql+asyncpg://postgres:postgres@localhost:5432/aegra'
os.environ['REDIS_BROKER_ENABLED'] = 'false'

from aegra_api.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=2026)

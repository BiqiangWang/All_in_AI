import sys
import asyncio
print("Python:", sys.version)

# MUST set policy BEFORE any other async code
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
print("Policy set to Selector")

# Now import and test
import asyncpg
print("asyncpg imported OK")

# Test connection
import asyncio
async def test():
    try:
        conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/aegra', timeout=5)
        print("Connected to DB!")
        await conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")

asyncio.run(test())

import asyncio
from datetime import datetime, timezone
from sqlalchemy import update
from db import async_session
from models import Task

async def process_fake_job(ctx, total_steps: int = 10):
    redis = ctx['redis']
    job_id = ctx['job_id']
    key = f"progress:{job_id}"
    channel = f"progress-channel:{job_id}"

    async with async_session() as session:
        await session.execute(
            update(Task).where(Task.id == job_id).values(status="running")
        )
        await session.commit()

    for step in range(1, total_steps +  1):
        await asyncio.sleep(1)
        percent = int(step / total_steps * 100)
        await redis.set(key, percent)
        await redis.publish(channel, percent)

    async with async_session() as session:
        await session.execute(
            update(Task).where(Task.id == job_id).values(
                status="success",
                finished_at=datetime.now(timezone.utc),
            )
        )
        await session.commit()

    return {"status": "done", "steps": total_steps}    
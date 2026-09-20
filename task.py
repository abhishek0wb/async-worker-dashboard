import asyncio

async def process_fake_job(ctx, total_steps: int = 10):
    redis = ctx['redis']
    job_id = ctx['job_id']
    key = f"progress:{job_id}"

    for step in range(1, total_steps +  1):
        await asyncio.sleep(1)
        percent = int(step / total_steps * 100)
        await redis.set(key, percent)
    return {"status": "done", "steps": total_steps}    
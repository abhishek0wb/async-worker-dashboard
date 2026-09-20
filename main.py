from fastapi import FastAPI, HTTPException
from arq import create_pool
from arq.connections import RedisSettings

app = FastAPI()
REDIS = RedisSettings(host="localhost", port=6379)

@app.post("/task/submit")
async def submit_task(total_steps:int = 10):
    redis = await create_pool(REDIS)
    job = await redis.enqueue_job("process_fake_job", total_steps)
    return {"task_id": job.job_id}

@app.get("/task/{task_id}")
async def get_progress(task_id: str):
    redis = await create_pool(REDIS)
    percent = await redis.get(f"progress:{task_id}")
    if percent is None:
        return {"task_id": task_id, "progress": 0 , "note": "queued or unknow"}
    return {"task_id": task_id, "progress": int(percent)}        
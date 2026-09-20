from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from arq import create_pool
from arq.connections import RedisSettings
from contextlib import asynccontextmanager
import asyncio

REDIS = RedisSettings(host="localhost", port=6379)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = await create_pool(REDIS)
    yield
    await app.state.redis.close()

app = FastAPI(lifespan=lifespan)

@app.websocket("/ws/task/{task_id}")
async def task_progress_ws(websocket:  WebSocket, task_id:str):
    await websocket.accept()
    channel = f"progress-channel:{task_id}"

    current = await app.state.redis.get(f"progress:{task_id}")
    current = int(current) if current is not None else 0
    await websocket.send_json({"task_id": task_id, "progress": current})
    if current >= 100:
        return

    pubsub = app.state.redis.pubsub()
    await pubsub.subscribe(channel)
    try:
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            percent = int(message["data"])
            await websocket.send_json({"task_id": task_id, "progress": percent})
            if percent >= 100:
                break
    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe(channel)                    

            

@app.post("/task/submit")
async def submit_task(total_steps:int = 10):
    job = await app.state.redis.enqueue_job("process_fake_job", total_steps)
    return {"task_id": job.job_id}

@app.get("/task/{task_id}")
async def get_progress(task_id: str):
    percent = await app.state.redis.get(f"progress:{task_id}")
    if percent is None:
        return {"task_id": task_id, "progress": 0 , "note": "queued or unknow"}
    return {"task_id": task_id, "progress": int(percent)}        
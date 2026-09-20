from arq.connections import RedisSettings
from task import process_fake_job

class WorkerSettings:
    functions = [process_fake_job]
    redis_settings = RedisSettings(host="localhost", port=6379)
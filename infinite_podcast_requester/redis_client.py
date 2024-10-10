import redis
import logging
from config import configuration
logger = logging.getLogger()

class RedisClient:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=configuration["redis"]["host"], port=configuration["redis"]["port"] or 6379
        )
        self.script_queue = configuration["redis"]["job_queue"]
        self.priority_job_queue = configuration["redis"]["priority_job_queue"]

    def get_length(self, queue=None):
        queue = queue or self.script_queue
        return self.redis_client.llen(queue)

"""
Redis-backed job status store for sharing state between API and Celery worker.
"""
import os
import json
import redis

# Connect to Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

JOB_KEY_PREFIX = "job:"
JOB_TTL = 86400  # 24 hours


class JobStore:
    """Redis-backed job store that works across processes"""

    def __setitem__(self, job_id: str, value: dict):
        """Store job status in Redis"""
        key = f"{JOB_KEY_PREFIX}{job_id}"
        redis_client.setex(key, JOB_TTL, json.dumps(value))

    def __getitem__(self, job_id: str) -> dict:
        """Get job status from Redis"""
        key = f"{JOB_KEY_PREFIX}{job_id}"
        data = redis_client.get(key)
        if data is None:
            raise KeyError(job_id)
        return json.loads(data)

    def __contains__(self, job_id: str) -> bool:
        """Check if job exists in Redis"""
        key = f"{JOB_KEY_PREFIX}{job_id}"
        return redis_client.exists(key) > 0

    def get(self, job_id: str, default=None):
        """Get job status with default fallback"""
        try:
            return self[job_id]
        except KeyError:
            return default


# Global job store instance
job_store = JobStore()


def update_job_status(job_id: str, **kwargs):
    """Update job status in Redis"""
    # Get current status or create new one
    current = job_store.get(job_id, {})
    current.update(kwargs)
    job_store[job_id] = current

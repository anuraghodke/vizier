"""
In-memory job status store.
In production, this should be replaced with Redis.
"""

# Job status store: {job_id: status_dict}
job_store = {}


def update_job_status(job_id: str, **kwargs):
    """Update job status in the store"""
    if job_id in job_store:
        job_store[job_id].update(kwargs)

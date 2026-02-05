import json
import time
import uuid

import redis

from pr_agent import config


class JobStore:
    def __init__(self) -> None:
        self.client = redis.Redis.from_url(config.REDIS_URL, decode_responses=True)
        self.queue_name = config.REDIS_QUEUE_NAME

    def enqueue(self, payload: dict) -> str:
        job_id = str(uuid.uuid4())
        job_key = self._job_key(job_id)
        now = int(time.time())
        body = {
            "id": job_id,
            "status": "queued",
            "created_at": now,
            "updated_at": now,
            "payload": json.dumps(payload),
        }
        self.client.hset(job_key, mapping=body)
        self.client.lpush(self.queue_name, job_id)
        return job_id

    def pop(self, timeout_seconds: int = 5) -> dict | None:
        result = self.client.brpop(self.queue_name, timeout=timeout_seconds)
        if result is None:
            return None
        _, job_id = result
        return self.get(job_id)

    def get(self, job_id: str) -> dict:
        job_key = self._job_key(job_id)
        data = self.client.hgetall(job_key)
        payload = json.loads(data.get("payload", "{}"))
        data["payload"] = payload
        return data

    def update_status(self, job_id: str, status: str) -> None:
        job_key = self._job_key(job_id)
        self.client.hset(
            job_key,
            mapping={
                "status": status,
                "updated_at": int(time.time()),
            },
        )

    def set_artifact(self, job_id: str, name: str, value: str) -> None:
        key = f"{self._job_key(job_id)}:artifact:{name}"
        self.client.set(key, value)

    def try_claim_issue(self, issue_key: str, ttl_seconds: int = 86400) -> bool:
        key = f"issue:seen:{issue_key}"
        claimed = self.client.setnx(key, str(int(time.time())))
        if claimed:
            self.client.expire(key, ttl_seconds)
        return bool(claimed)

    def _job_key(self, job_id: str) -> str:
        return f"job:{job_id}"

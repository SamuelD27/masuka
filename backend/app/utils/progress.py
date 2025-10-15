import json
import redis
from typing import Dict, Any, Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class ProgressManager:
    """Manage training progress in Redis for real-time updates."""

    def __init__(self):
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )

    def set_progress(self, session_id: str, data: Dict[str, Any], expire_seconds: int = 3600):
        """Set progress data for a training session."""
        key = f"training:{session_id}:progress"
        try:
            self.redis_client.set(
                key,
                json.dumps(data),
                ex=expire_seconds
            )
            logger.info(f"Progress updated for session {session_id}: {data.get('status')}")
        except Exception as e:
            logger.error(f"Failed to set progress: {e}")

    def get_progress(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get progress data for a training session."""
        key = f"training:{session_id}:progress"
        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Failed to get progress: {e}")
            return None

    def delete_progress(self, session_id: str):
        """Delete progress data for a training session."""
        key = f"training:{session_id}:progress"
        try:
            self.redis_client.delete(key)
            logger.info(f"Progress deleted for session {session_id}")
        except Exception as e:
            logger.error(f"Failed to delete progress: {e}")

    def update_step(self, session_id: str, step: int, total_steps: int, loss: float = None):
        """Quick update for training step progress."""
        progress_pct = int((step / total_steps) * 100) if total_steps > 0 else 0
        data = {
            "status": "training",
            "progress": progress_pct,
            "current_step": step,
            "total_steps": total_steps,
            "current_loss": loss
        }
        self.set_progress(session_id, data)

# Global instance
progress_manager = ProgressManager()

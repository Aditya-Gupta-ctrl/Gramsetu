"""
Session management for browser state persistence
Handles session recovery on timeouts
"""
from typing import Optional, Dict, Any
import json
from shared.redis_client import RedisClient
from shared.logging_config import logger

redis_client = RedisClient()


class SessionManager:
    """Manages browser session state for recovery"""
    
    async def initialize(self):
        """Initialize Redis connection"""
        await redis_client.connect()
        logger.info("Session manager initialized")
    
    async def save_session(self, task_id: str, session_state: Dict[str, Any]):
        """
        Save session state to Redis
        
        Args:
            task_id: Task identifier
            session_state: Dict with cookies, local storage, etc.
        """
        try:
            await redis_client.set_json(
                f"session:{task_id}",
                session_state,
                expire=1800  # 30 minutes
            )
            logger.info(f"Session saved for task {task_id}")
        except Exception as e:
            logger.error(f"Failed to save session: {str(e)}")
    
    async def restore_session(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Restore session state from Redis
        
        Args:
            task_id: Task identifier
        
        Returns:
            Session state dict or None
        """
        try:
            session_state = await redis_client.get_json(f"session:{task_id}")
            if session_state:
                logger.info(f"Session restored for task {task_id}")
            return session_state
        except Exception as e:
            logger.error(f"Failed to restore session: {str(e)}")
            return None

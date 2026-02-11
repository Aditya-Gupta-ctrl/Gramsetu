"""
Job manager for orchestrating workflow across services
Coordinates Voice -> Document -> Agent -> WhatsApp
"""
import httpx
from datetime import datetime
from typing import Optional
from shared.config import get_settings
from shared.schemas import JobRequest, JobStatusResponse, JobStatus
from shared.redis_client import RedisClient
from shared.logging_config import logger

settings = get_settings()
redis_client = RedisClient()


class JobManager:
    """Orchestrates multi-service workflows"""
    
    def __init__(self):
        self.http_client: Optional[httpx.AsyncClient] = None
    
    async def initialize(self):
        """Initialize HTTP client and Redis"""
        self.http_client = httpx.AsyncClient(timeout=30.0)
        await redis_client.connect()
        logger.info("Job manager initialized")
    
    async def create_job(self, job_id: str, job_request: JobRequest):
        """
        Create and start processing job
        
        Workflow:
        1. Process voice input (if provided)
        2. Process documents (if provided)
        3. Combine results and send to agent
        4. Send WhatsApp notification on completion
        """
        try:
            # Store job metadata
            job_data = {
                "job_id": job_id,
                "vle_id": job_request.vle_id,
                "citizen_name": job_request.citizen_name,
                "citizen_phone": job_request.citizen_phone,
                "status": JobStatus.QUEUED,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            await redis_client.set_json(f"job:{job_id}", job_data, expire=86400)
            
            # Enqueue for processing
            await redis_client.enqueue_job("job_queue", job_data)
            
            logger.info(f"Job {job_id} created and queued")
            
        except Exception as e:
            logger.error(f"Job creation failed: {str(e)}")
            raise
    
    async def get_status(self, job_id: str) -> Optional[JobStatusResponse]:
        """Get current job status"""
        try:
            job_data = await redis_client.get_json(f"job:{job_id}")
            if not job_data:
                return None
            
            return JobStatusResponse(
                job_id=job_id,
                status=job_data.get("status", JobStatus.QUEUED),
                progress_percentage=job_data.get("progress", 0),
                current_step=job_data.get("current_step", "Initializing"),
                result=job_data.get("result"),
                created_at=datetime.fromisoformat(job_data["created_at"]),
                updated_at=datetime.fromisoformat(job_data["updated_at"])
            )
            
        except Exception as e:
            logger.error(f"Status retrieval failed: {str(e)}")
            return None

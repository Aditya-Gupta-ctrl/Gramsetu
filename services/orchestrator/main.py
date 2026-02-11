"""
Member 4: Orchestrator Service
Main API gateway, job queue management, WhatsApp integration
"""
from fastapi import FastAPI, HTTPException, Depends, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uuid
from datetime import datetime

from shared.config import get_settings
from shared.schemas import (
    JobRequest, JobResponse, JobStatusResponse,
    JobStatus, WhatsAppNotification
)
from shared.logging_config import setup_logging
from shared.redis_client import get_redis, RedisClient

from services.orchestrator.job_manager import JobManager
from services.orchestrator.whatsapp_client import WhatsAppClient

# Initialize
settings = get_settings()
logger = setup_logging("orchestrator")
app = FastAPI(title="GramSetu Orchestrator", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service components
job_manager = JobManager()
whatsapp_client = WhatsAppClient()


@app.on_event("startup")
async def startup():
    """Initialize connections"""
    logger.info("Orchestrator starting up")
    await job_manager.initialize()
    await whatsapp_client.initialize()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "orchestrator"}


@app.post("/jobs", response_model=JobResponse)
async def create_job(
    job_request: JobRequest,
    redis: RedisClient = Depends(get_redis)
):
    """
    Create new job from VLE
    
    Flow:
    1. Generate job ID
    2. Validate consent
    3. Enqueue voice processing
    4. Enqueue document processing
    5. Return job ID to VLE
    """
    try:
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        logger.info(
            "Creating job",
            job_id=job_id,
            vle_id=job_request.vle_id,
            citizen=job_request.citizen_name
        )
        
        # Validate consent
        if not job_request.consent_recorded:
            raise HTTPException(
                status_code=400,
                detail="Verbal consent must be recorded before processing"
            )
        
        # Create job in manager
        await job_manager.create_job(job_id, job_request)
        
        return JobResponse(
            job_id=job_id,
            status=JobStatus.QUEUED,
            estimated_completion_seconds=60,
            message=f"Job created for {job_request.citizen_name}. Processing started."
        )
        
    except Exception as e:
        logger.error(f"Job creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get job status"""
    try:
        status = await job_manager.get_status(job_id)
        if not status:
            raise HTTPException(status_code=404, detail="Job not found")
        return status
    except Exception as e:
        logger.error(f"Status retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/{vle_id}")
async def websocket_endpoint(websocket: WebSocket, vle_id: str):
    """
    WebSocket for real-time updates to VLE mobile app
    """
    await websocket.accept()
    logger.info(f"WebSocket connected: {vle_id}")
    
    try:
        while True:
            # Keep connection alive and send updates
            data = await websocket.receive_text()
            # Echo for now (implement real-time job updates)
            await websocket.send_text(f"Received: {data}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        logger.info(f"WebSocket disconnected: {vle_id}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=(settings.environment == "development")
    )

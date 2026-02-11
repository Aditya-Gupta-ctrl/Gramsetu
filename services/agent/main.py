"""
Member 2: Browser Agent Service
Autonomous web navigation using AWS Bedrock Agents + Visual Navigation
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from shared.config import get_settings
from shared.schemas import AgentTask, AgentResult, JobStatus
from shared.logging_config import setup_logging
from shared.redis_client import get_redis, RedisClient

from services.agent.bedrock_agent import BedrockAgentController
from services.agent.visual_navigator import VisualNavigator
from services.agent.session_manager import SessionManager

# Initialize
settings = get_settings()
logger = setup_logging("agent-service")
app = FastAPI(title="GramSetu Agent Service", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service components
bedrock_controller = BedrockAgentController()
visual_navigator = VisualNavigator()
session_manager = SessionManager()


@app.on_event("startup")
async def startup():
    """Initialize browser and connections"""
    logger.info("Agent service starting up")
    await visual_navigator.initialize()
    await session_manager.initialize()


@app.on_event("shutdown")
async def shutdown():
    """Cleanup browsers"""
    logger.info("Agent service shutting down")
    await visual_navigator.cleanup()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "agent"}


@app.post("/execute-task", response_model=AgentResult)
async def execute_task(
    task: AgentTask,
    background_tasks: BackgroundTasks,
    redis: RedisClient = Depends(get_redis)
):
    """
    Execute autonomous browser task
    
    Flow:
    1. Load portal-specific driver (PM-KISAN, e-Shram, etc.)
    2. Restore session if available
    3. Navigate using visual cues
    4. Solve CAPTCHAs
    5. Fill form with data
    6. Submit and capture acknowledgement
    7. Return result
    """
    try:
        logger.info(
            "Executing agent task",
            task_id=task.task_id,
            scheme=task.scheme,
            action=task.action
        )
        
        # Update status to processing
        await redis.set_json(
            f"task:{task.task_id}:status",
            {"status": JobStatus.PROCESSING, "step": "Initializing browser"},
            expire=3600
        )
        
        # Get portal-specific driver
        driver = await bedrock_controller.get_driver(task.scheme)
        
        # Execute task using visual navigator
        result = await visual_navigator.execute(
            driver=driver,
            task=task,
            session_state=task.session_state
        )
        
        # Save session for future use
        if result.status == JobStatus.COMPLETED:
            await session_manager.save_session(
                task.task_id,
                driver.get_session_state()
            )
        
        logger.info(
            "Task execution complete",
            task_id=task.task_id,
            status=result.status
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Task execution failed: {str(e)}", exc_info=True)
        return AgentResult(
            task_id=task.task_id,
            status=JobStatus.FAILED,
            error_message=str(e),
            steps_completed=[]
        )


@app.get("/task-status/{task_id}")
async def get_task_status(
    task_id: str,
    redis: RedisClient = Depends(get_redis)
):
    """Get real-time task status"""
    status = await redis.get_json(f"task:{task_id}:status")
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=8002,
        reload=(settings.environment == "development")
    )

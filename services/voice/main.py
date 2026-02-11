"""
Member 1: Voice Interface Service
Handles Bhashini ASR, translation, and intent classification
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import base64
import io
from typing import Optional

from shared.config import get_settings
from shared.schemas import VoiceInput, VoiceOutput, IntentType, SchemeType
from shared.logging_config import setup_logging
from shared.redis_client import get_redis, RedisClient

from services.voice.bhashini_client import BhashiniClient
from services.voice.audio_processor import AudioProcessor
from services.voice.intent_classifier import IntentClassifier

# Initialize
settings = get_settings()
logger = setup_logging("voice-service")
app = FastAPI(title="GramSetu Voice Service", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service components
bhashini_client = BhashiniClient()
audio_processor = AudioProcessor()
intent_classifier = IntentClassifier()


@app.on_event("startup")
async def startup():
    """Initialize connections"""
    logger.info("Voice service starting up")
    await bhashini_client.initialize()


@app.on_event("shutdown")
async def shutdown():
    """Cleanup"""
    logger.info("Voice service shutting down")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "voice"}


@app.post("/process-audio", response_model=VoiceOutput)
async def process_audio(
    voice_input: VoiceInput,
    redis: RedisClient = Depends(get_redis)
):
    """
    Process voice input through complete pipeline:
    1. Decode audio
    2. Apply noise suppression
    3. Bhashini ASR (Speech -> Text)
    4. Bhashini NMT (Hindi -> English)
    5. Intent classification (LLM)
    6. Entity extraction
    """
    try:
        logger.info(
            "Processing voice input",
            vle_id=voice_input.vle_id,
            session_id=voice_input.session_id
        )
        
        # Step 1: Decode audio
        audio_bytes = base64.b64decode(voice_input.audio_base64)
        
        # Step 2: Preprocess (noise suppression, VAD)
        processed_audio = await audio_processor.preprocess(audio_bytes)
        
        # Step 3: Bhashini ASR
        transcript = await bhashini_client.speech_to_text(
            processed_audio,
            source_language=voice_input.language_hint
        )
        logger.info(f"Transcript: {transcript}")
        
        # Step 4: Translate to English (for agent)
        english_text = await bhashini_client.translate(
            transcript,
            source_lang=voice_input.language_hint,
            target_lang="en"
        )
        
        # Step 5: Intent classification
        intent_result = await intent_classifier.classify(
            english_text,
            context=voice_input.session_id
        )
        
        # Build response
        output = VoiceOutput(
            transcript=transcript,
            intent=intent_result["intent"],
            scheme=intent_result.get("scheme"),
            entities=intent_result.get("entities", {}),
            missing_info=intent_result.get("missing_info", []),
            confidence=intent_result.get("confidence", 0.0)
        )
        
        # Cache for session continuity
        if voice_input.session_id:
            await redis.set_json(
                f"voice:session:{voice_input.session_id}",
                output.dict(),
                expire=3600
            )
        
        logger.info(
            "Voice processing complete",
            intent=output.intent,
            scheme=output.scheme,
            confidence=output.confidence
        )
        
        return output
        
    except Exception as e:
        logger.error(f"Voice processing failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/text-to-speech")
async def text_to_speech(text: str, language: str = "hi"):
    """
    Convert text to speech for VLE feedback
    (Future enhancement for voice responses)
    """
    try:
        audio_bytes = await bhashini_client.text_to_speech(text, language)
        audio_base64 = base64.b64encode(audio_bytes).decode()
        return {"audio_base64": audio_base64}
    except Exception as e:
        logger.error(f"TTS failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=8001,
        reload=(settings.environment == "development")
    )

"""
Bhashini API client for ASR and NMT
Implements the National Language Translation Mission pipeline
"""
import httpx
from typing import Optional
from shared.config import get_settings
from shared.logging_config import logger
import base64

settings = get_settings()


class BhashiniClient:
    """Client for Bhashini ULCA API"""
    
    def __init__(self):
        self.base_url = settings.bhashini_base_url
        self.api_key = settings.bhashini_api_key
        self.user_id = settings.bhashini_user_id
        self.pipeline_id = settings.bhashini_pipeline_id
        self.client: Optional[httpx.AsyncClient] = None
    
    async def initialize(self):
        """Initialize HTTP client"""
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        logger.info("Bhashini client initialized")
    
    async def speech_to_text(
        self,
        audio_bytes: bytes,
        source_language: str = "hi"
    ) -> str:
        """
        Convert speech to text using Bhashini ASR
        
        Args:
            audio_bytes: WAV audio data
            source_language: Language code (hi, bn, ta, etc.)
        
        Returns:
            Transcribed text
        """
        try:
            # Encode audio to base64
            audio_base64 = base64.b64encode(audio_bytes).decode()
            
            # Bhashini ASR request
            payload = {
                "pipelineTasks": [
                    {
                        "taskType": "asr",
                        "config": {
                            "language": {
                                "sourceLanguage": source_language
                            },
                            "serviceId": "ai4bharat/conformer-hi-gpu--t4",
                            "audioFormat": "wav",
                            "samplingRate": settings.audio_sample_rate
                        }
                    }
                ],
                "inputData": {
                    "audio": [
                        {
                            "audioContent": audio_base64
                        }
                    ]
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/ulca/apis/v0/model/compute",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            transcript = result["pipelineResponse"][0]["output"][0]["source"]
            
            logger.info(f"ASR successful: {transcript[:50]}...")
            return transcript
            
        except Exception as e:
            logger.error(f"Bhashini ASR failed: {str(e)}")
            # Fallback to Sarvam AI if configured
            if settings.sarvam_api_key:
                return await self._sarvam_fallback(audio_bytes, source_language)
            raise
    
    async def translate(
        self,
        text: str,
        source_lang: str = "hi",
        target_lang: str = "en"
    ) -> str:
        """
        Translate text using Bhashini NMT
        
        Args:
            text: Input text
            source_lang: Source language code
            target_lang: Target language code
        
        Returns:
            Translated text
        """
        try:
            payload = {
                "pipelineTasks": [
                    {
                        "taskType": "translation",
                        "config": {
                            "language": {
                                "sourceLanguage": source_lang,
                                "targetLanguage": target_lang
                            },
                            "serviceId": "ai4bharat/indictrans-v2-all-gpu--t4"
                        }
                    }
                ],
                "inputData": {
                    "input": [
                        {
                            "source": text
                        }
                    ]
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/ulca/apis/v0/model/compute",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            translation = result["pipelineResponse"][0]["output"][0]["target"]
            
            logger.info(f"Translation: {text[:30]}... -> {translation[:30]}...")
            return translation
            
        except Exception as e:
            logger.error(f"Bhashini NMT failed: {str(e)}")
            # If translation fails, return original (agent can try to work with it)
            return text
    
    async def text_to_speech(self, text: str, language: str = "hi") -> bytes:
        """
        Convert text to speech (for future voice responses)
        
        Args:
            text: Text to synthesize
            language: Language code
        
        Returns:
            Audio bytes (WAV)
        """
        try:
            payload = {
                "pipelineTasks": [
                    {
                        "taskType": "tts",
                        "config": {
                            "language": {
                                "sourceLanguage": language
                            },
                            "serviceId": "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4",
                            "gender": "female",
                            "samplingRate": settings.audio_sample_rate
                        }
                    }
                ],
                "inputData": {
                    "input": [
                        {
                            "source": text
                        }
                    ]
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/ulca/apis/v0/model/compute",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            audio_base64 = result["pipelineResponse"][0]["audio"][0]["audioContent"]
            audio_bytes = base64.b64decode(audio_base64)
            
            return audio_bytes
            
        except Exception as e:
            logger.error(f"Bhashini TTS failed: {str(e)}")
            raise
    
    async def _sarvam_fallback(self, audio_bytes: bytes, language: str) -> str:
        """Fallback to Sarvam AI for ASR"""
        logger.info("Using Sarvam AI fallback for ASR")
        # TODO: Implement Sarvam AI integration
        raise NotImplementedError("Sarvam AI fallback not yet implemented")

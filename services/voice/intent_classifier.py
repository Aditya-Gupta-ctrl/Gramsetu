"""
Intent classification and entity extraction using LLM
Converts transcribed text to structured action + entities
"""
import json
from typing import Dict, Any
from shared.config import get_settings
from shared.schemas import IntentType, SchemeType
from shared.logging_config import logger

# Try Bedrock first, fallback to OpenAI
try:
    import boto3
    USE_BEDROCK = True
except ImportError:
    USE_BEDROCK = False

try:
    from openai import AsyncOpenAI
    USE_OPENAI = True
except ImportError:
    USE_OPENAI = False

settings = get_settings()


class IntentClassifier:
    """LLM-powered intent classification for government schemes"""
    
    SYSTEM_PROMPT = """You are an expert Indian Government Scheme intent classifier.

Your task is to analyze user requests (spoken in rural Indian dialects, translated to English) and extract:
1. **intent**: The action the user wants (check_status, apply_new, update_details, download_certificate, register)
2. **scheme**: The government scheme (pm_kisan, e_shram, epfo, widow_pension, ration_card, ayushman_bharat)
3. **entities**: Any mentioned data (name, aadhaar, mobile, account_number, etc.)
4. **missing_info**: Required fields not yet provided

Common patterns:
- "Check PM-Kisan money" → intent: check_status, scheme: pm_kisan
- "Register for e-Shram" → intent: register, scheme: e_shram
- "My widow pension not coming" → intent: check_status, scheme: widow_pension

Respond ONLY with valid JSON:
{
  "intent": "check_status",
  "scheme": "pm_kisan",
  "entities": {"name": "Ramesh Kumar"},
  "missing_info": ["aadhaar_number", "mobile_number"],
  "confidence": 0.95
}

If unsure, set confidence < 0.7 and ask for clarification."""
    
    def __init__(self):
        if USE_BEDROCK:
            self.bedrock = boto3.client(
                'bedrock-runtime',
                region_name=settings.aws_region,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key
            )
            self.model_id = settings.bedrock_llm_model
            logger.info("Using AWS Bedrock for intent classification")
        elif USE_OPENAI and settings.openai_api_key:
            self.openai = AsyncOpenAI(api_key=settings.openai_api_key)
            logger.info("Using OpenAI for intent classification")
        else:
            logger.warning("No LLM configured, using rule-based fallback")
    
    async def classify(self, text: str, context: str = None) -> Dict[str, Any]:
        """
        Classify intent and extract entities
        
        Args:
            text: Transcribed/translated text
            context: Optional session context
        
        Returns:
            Dict with intent, scheme, entities, missing_info, confidence
        """
        try:
            if USE_BEDROCK:
                return await self._classify_bedrock(text)
            elif USE_OPENAI:
                return await self._classify_openai(text)
            else:
                return self._classify_rules(text)
        except Exception as e:
            logger.error(f"Intent classification failed: {str(e)}")
            # Fallback to rule-based
            return self._classify_rules(text)
    
    async def _classify_bedrock(self, text: str) -> Dict[str, Any]:
        """Use AWS Bedrock (Claude) for classification"""
        try:
            payload = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 500,
                "temperature": 0.1,
                "messages": [
                    {
                        "role": "user",
                        "content": f"{self.SYSTEM_PROMPT}\n\nUser request: {text}"
                    }
                ]
            }
            
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps(payload)
            )
            
            result = json.loads(response['body'].read())
            content = result['content'][0]['text']
            
            # Parse JSON from response
            parsed = json.loads(content)
            logger.info(f"Bedrock classification: {parsed}")
            return parsed
            
        except Exception as e:
            logger.error(f"Bedrock classification failed: {str(e)}")
            raise
    
    async def _classify_openai(self, text: str) -> Dict[str, Any]:
        """Use OpenAI for classification"""
        try:
            response = await self.openai.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": f"User request: {text}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            parsed = json.loads(content)
            logger.info(f"OpenAI classification: {parsed}")
            return parsed
            
        except Exception as e:
            logger.error(f"OpenAI classification failed: {str(e)}")
            raise
    
    def _classify_rules(self, text: str) -> Dict[str, Any]:
        """
        Rule-based fallback classification
        Simple keyword matching for demo purposes
        """
        text_lower = text.lower()
        
        # Detect scheme
        scheme = None
        if any(kw in text_lower for kw in ["pm-kisan", "kisan", "farmer"]):
            scheme = SchemeType.PM_KISAN
        elif any(kw in text_lower for kw in ["e-shram", "eshram", "labor", "labour"]):
            scheme = SchemeType.E_SHRAM
        elif any(kw in text_lower for kw in ["epfo", "pf", "provident"]):
            scheme = SchemeType.EPFO
        elif any(kw in text_lower for kw in ["widow", "pension"]):
            scheme = SchemeType.WIDOW_PENSION
        
        # Detect intent
        intent = IntentType.CHECK_STATUS  # Default
        if any(kw in text_lower for kw in ["apply", "register", "new"]):
            intent = IntentType.APPLY_NEW
        elif any(kw in text_lower for kw in ["update", "change", "modify"]):
            intent = IntentType.UPDATE_DETAILS
        elif any(kw in text_lower for kw in ["download", "certificate", "proof"]):
            intent = IntentType.DOWNLOAD_CERTIFICATE
        
        logger.warning(f"Using rule-based classification: {intent}, {scheme}")
        
        return {
            "intent": intent,
            "scheme": scheme,
            "entities": {},
            "missing_info": ["aadhaar_number", "mobile_number"],
            "confidence": 0.6  # Low confidence for rule-based
        }

# Bhashini API Integration Guide

## Overview

Bhashini (National Language Translation Mission) provides ASR, NMT, and TTS capabilities for 22+ Indian languages. This guide covers integration for GramSetu's voice interface.

## Registration

1. **Visit ULCA Portal**: https://bhashini.gov.in/ulca
2. **Sign Up**: Create account with email
3. **Get API Key**: Navigate to "API Access" section
4. **Note Credentials**:
   - API Key
   - User ID
   - Pipeline ID (optional, for custom pipelines)

## API Endpoints

### Base URL
```
https://meity-auth.ulcacontrib.org
```

### Authentication
All requests require Bearer token in header:
```
Authorization: Bearer <your_api_key>
```

## Speech-to-Text (ASR)

### Request Format

```json
{
  "pipelineTasks": [
    {
      "taskType": "asr",
      "config": {
        "language": {
          "sourceLanguage": "hi"
        },
        "serviceId": "ai4bharat/conformer-hi-gpu--t4",
        "audioFormat": "wav",
        "samplingRate": 16000
      }
    }
  ],
  "inputData": {
    "audio": [
      {
        "audioContent": "<base64_encoded_audio>"
      }
    ]
  }
}
```

### Supported Languages

| Code | Language | Service ID |
|------|----------|------------|
| `hi` | Hindi | `ai4bharat/conformer-hi-gpu--t4` |
| `bn` | Bengali | `ai4bharat/conformer-bn-gpu--t4` |
| `ta` | Tamil | `ai4bharat/conformer-ta-gpu--t4` |
| `te` | Telugu | `ai4bharat/conformer-te-gpu--t4` |
| `mr` | Marathi | `ai4bharat/conformer-mr-gpu--t4` |

### Response Format

```json
{
  "pipelineResponse": [
    {
      "output": [
        {
          "source": "मुझे पीएम किसान का स्टेटस चेक करना है"
        }
      ]
    }
  ]
}
```

## Translation (NMT)

### Request Format

```json
{
  "pipelineTasks": [
    {
      "taskType": "translation",
      "config": {
        "language": {
          "sourceLanguage": "hi",
          "targetLanguage": "en"
        },
        "serviceId": "ai4bharat/indictrans-v2-all-gpu--t4"
      }
    }
  ],
  "inputData": {
    "input": [
      {
        "source": "मुझे पीएम किसान का स्टेटस चेक करना है"
      }
    ]
  }
}
```

### Response Format

```json
{
  "pipelineResponse": [
    {
      "output": [
        {
          "target": "I need to check PM-Kisan status"
        }
      ]
    }
  ]
}
```

## Text-to-Speech (TTS)

### Request Format

```json
{
  "pipelineTasks": [
    {
      "taskType": "tts",
      "config": {
        "language": {
          "sourceLanguage": "hi"
        },
        "serviceId": "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4",
        "gender": "female",
        "samplingRate": 16000
      }
    }
  ],
  "inputData": {
    "input": [
      {
        "source": "आपका आवेदन सफलतापूर्वक जमा हो गया है"
      }
    ]
  }
}
```

### Response Format

```json
{
  "pipelineResponse": [
    {
      "audio": [
        {
          "audioContent": "<base64_encoded_audio>"
        }
      ]
    }
  ]
}
```

## Error Handling

### Common Errors

| Status Code | Error | Solution |
|-------------|-------|----------|
| 401 | Unauthorized | Check API key |
| 429 | Rate limit exceeded | Implement exponential backoff |
| 500 | Server error | Retry with delay |
| 504 | Gateway timeout | Reduce audio size or retry |

### Retry Strategy

```python
import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def call_bhashini_api(payload):
    response = await client.post(url, json=payload)
    response.raise_for_status()
    return response.json()
```

## Best Practices

### Audio Preprocessing

1. **Format**: Convert to WAV, 16kHz, mono
2. **Noise Reduction**: Apply before sending
3. **Silence Trimming**: Remove leading/trailing silence
4. **Chunk Size**: Keep under 10 seconds for best results

### Optimization

1. **Caching**: Cache translations for common phrases
2. **Batching**: Combine multiple requests when possible
3. **Compression**: Use gzip for large payloads
4. **Streaming**: Use WebSocket for real-time ASR (if available)

## Testing

### Sample Request (curl)

```bash
curl -X POST https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/compute \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "pipelineTasks": [{
      "taskType": "asr",
      "config": {
        "language": {"sourceLanguage": "hi"},
        "serviceId": "ai4bharat/conformer-hi-gpu--t4",
        "audioFormat": "wav",
        "samplingRate": 16000
      }
    }],
    "inputData": {
      "audio": [{"audioContent": "BASE64_AUDIO_HERE"}]
    }
  }'
```

### Python Example

```python
import httpx
import base64

async def test_bhashini_asr():
    # Load audio file
    with open("test_audio.wav", "rb") as f:
        audio_bytes = f.read()
    
    audio_base64 = base64.b64encode(audio_bytes).decode()
    
    # Prepare request
    payload = {
        "pipelineTasks": [{
            "taskType": "asr",
            "config": {
                "language": {"sourceLanguage": "hi"},
                "serviceId": "ai4bharat/conformer-hi-gpu--t4",
                "audioFormat": "wav",
                "samplingRate": 16000
            }
        }],
        "inputData": {
            "audio": [{"audioContent": audio_base64}]
        }
    }
    
    # Send request
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/compute",
            json=payload,
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        
        result = response.json()
        transcript = result["pipelineResponse"][0]["output"][0]["source"]
        print(f"Transcript: {transcript}")
```

## Rate Limits

- **Free Tier**: 100 requests/hour
- **Paid Tier**: Contact Bhashini team for higher limits
- **Concurrent Requests**: Max 5 simultaneous

## Support

- **Documentation**: https://bhashini.gitbook.io/bhashini-apis
- **Forum**: https://community.bhashini.gov.in
- **Email**: support@bhashini.gov.in

## Fallback Strategy

If Bhashini is unavailable, use Sarvam AI:

```python
# In bhashini_client.py
async def _sarvam_fallback(self, audio_bytes, language):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.sarvam.ai/speech-to-text",
            headers={"Authorization": f"Bearer {SARVAM_API_KEY}"},
            files={"audio": audio_bytes},
            data={"language": language}
        )
        return response.json()["transcript"]
```

---

**Last Updated**: 2026-02-08  
**Version**: 1.0

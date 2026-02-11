# GramSetu Quick Start Guide

## Prerequisites

Before starting, ensure you have:

- **Python 3.11+** installed
- **Node.js 18+** (for mobile app)
- **Docker Desktop** running
- **Git** installed
- **AWS Account** with Bedrock access
- **Bhashini API** credentials
- **Twilio Account** for WhatsApp

## Step 1: Clone and Setup

```bash
# Clone repository
git clone <your-repo-url>
cd GramSetu

# Copy environment template
cp .env.example .env
```

## Step 2: Configure Environment

Edit `.env` and fill in your credentials:

```bash
# CRITICAL: These MUST be set
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
BHASHINI_API_KEY=your_bhashini_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
```

## Step 3: Start Infrastructure

```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Wait for services to be healthy (30 seconds)
docker-compose ps
```

## Step 4: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Verify installation
python -c "import playwright; print('Playwright OK')"
```

## Step 5: Run Services

Open **4 terminal windows** (one for each service):

### Terminal 1: Voice Service
```bash
python -m services.voice.main
# Should start on http://localhost:8001
```

### Terminal 2: Agent Service
```bash
python -m services.agent.main
# Should start on http://localhost:8002
```

### Terminal 3: Document Service
```bash
python -m services.document.main
# Should start on http://localhost:8003
```

### Terminal 4: Orchestrator
```bash
python -m services.orchestrator.main
# Should start on http://localhost:8000
```

## Step 6: Test Individual Services

### Test Voice Service
```bash
# In a new terminal
curl http://localhost:8001/health
# Expected: {"status": "healthy", "service": "voice"}
```

### Test Agent Service
```bash
curl http://localhost:8002/health
# Expected: {"status": "healthy", "service": "agent"}
```

### Test Document Service
```bash
curl http://localhost:8003/health
# Expected: {"status": "healthy", "service": "document"}
```

### Test Orchestrator
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "service": "orchestrator"}
```

## Step 7: Run End-to-End Demo

### Prepare Test Data

Create `demo_request.json`:
```json
{
  "vle_id": "VLE001",
  "citizen_name": "Ramesh Kumar",
  "citizen_phone": "+919876543210",
  "consent_recorded": true,
  "voice_input": {
    "audio_base64": "<your_audio_base64>",
    "vle_id": "VLE001",
    "language_hint": "hi"
  },
  "documents": [
    {
      "image_base64": "<your_aadhaar_image_base64>",
      "document_type": "aadhaar",
      "vle_id": "VLE001",
      "apply_masking": true
    }
  ]
}
```

### Submit Job
```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d @demo_request.json

# Response will include job_id
```

### Check Status
```bash
curl http://localhost:8000/jobs/{job_id}

# Monitor status progression:
# queued → processing → solving_captcha → completed
```

## Troubleshooting

### Issue: "Bhashini API timeout"
**Solution**: Check your Bhashini API key and network connection.

### Issue: "Browser not found"
**Solution**: Run `playwright install chromium` again.

### Issue: "Redis connection failed"
**Solution**: Ensure Docker containers are running: `docker-compose ps`

### Issue: "AWS credentials invalid"
**Solution**: Verify IAM user has Bedrock and Textract permissions.

## Docker Deployment (Production)

For full containerized deployment:

```bash
# Build all services
docker-compose build

# Start everything
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## Next Steps

1. **Read Implementation Plan**: See `implementation_plan.md` for detailed architecture
2. **Configure Portals**: Add more portal drivers in `services/agent/bedrock_agent.py`
3. **Test with Real Data**: Record actual voice samples and scan real documents
4. **Deploy Mobile App**: See `mobile-app/README.md` for React Native setup

## Support

For hackathon support, contact:
- **Member 1** (Voice): [email]
- **Member 2** (Agent): [email]
- **Member 3** (Document): [email]
- **Member 4** (Orchestrator): [email]

---

**Ready to transform rural India's digital access! 🚀**

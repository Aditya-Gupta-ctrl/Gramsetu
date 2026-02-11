"""
Member 3: Document Processing Service
Privacy-preserving OCR with edge-based Aadhaar masking
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import base64
import io
from PIL import Image
import cv2
import numpy as np

from shared.config import get_settings
from shared.schemas import DocumentInput, DocumentOutput, DocumentType
from shared.logging_config import setup_logging

from services.document.aadhaar_masker import AadhaarMasker
from services.document.ocr_engine import OCREngine
from services.document.document_verifier import DocumentVerifier

# Initialize
settings = get_settings()
logger = setup_logging("document-service")
app = FastAPI(title="GramSetu Document Service", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service components
aadhaar_masker = AadhaarMasker()
ocr_engine = OCREngine()
document_verifier = DocumentVerifier()


@app.on_event("startup")
async def startup():
    """Initialize OCR models"""
    logger.info("Document service starting up")
    await ocr_engine.initialize()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "document"}


@app.post("/process-document", response_model=DocumentOutput)
async def process_document(doc_input: DocumentInput):
    """
    Process document with privacy-preserving OCR
    
    Flow:
    1. Decode image
    2. Apply masking if Aadhaar (DPDP compliance)
    3. Run OCR extraction
    4. Verify authenticity
    5. Return structured data
    """
    try:
        logger.info(
            "Processing document",
            document_type=doc_input.document_type,
            vle_id=doc_input.vle_id
        )
        
        # Decode image
        image_bytes = base64.b64decode(doc_input.image_base64)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Apply masking if Aadhaar
        masked_image = image
        if doc_input.document_type == DocumentType.AADHAAR and doc_input.apply_masking:
            masked_image = await aadhaar_masker.mask(image)
            logger.info("Aadhaar masking applied")
        
        # Run OCR
        extracted_data, confidence_scores = await ocr_engine.extract(
            masked_image,
            doc_input.document_type
        )
        
        # Verify authenticity
        is_authentic, warnings = await document_verifier.verify(
            masked_image,
            doc_input.document_type,
            extracted_data
        )
        
        logger.info(
            "Document processing complete",
            extracted_fields=len(extracted_data),
            is_authentic=is_authentic
        )
        
        return DocumentOutput(
            document_type=doc_input.document_type,
            extracted_data=extracted_data,
            confidence_scores=confidence_scores,
            is_authentic=is_authentic,
            warnings=warnings
        )
        
    except Exception as e:
        logger.error(f"Document processing failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=8003,
        reload=(settings.environment == "development")
    )

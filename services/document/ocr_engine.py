"""
OCR engine using AWS Textract
Extracts structured data from documents
"""
import boto3
from PIL import Image
import io
from typing import Dict, Any, Tuple
from shared.config import get_settings
from shared.schemas import DocumentType
from shared.logging_config import logger

settings = get_settings()


class OCREngine:
    """Document OCR using AWS Textract"""
    
    def __init__(self):
        self.textract = None
    
    async def initialize(self):
        """Initialize AWS Textract client"""
        self.textract = boto3.client(
            'textract',
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key
        )
        logger.info("Textract client initialized")
    
    async def extract(
        self,
        image: Image.Image,
        document_type: DocumentType
    ) -> Tuple[Dict[str, Any], Dict[str, float]]:
        """
        Extract structured data from document
        
        Args:
            image: PIL Image
            document_type: Type of document
        
        Returns:
            (extracted_data dict, confidence_scores dict)
        """
        try:
            # Convert image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            
            # Call Textract
            response = self.textract.analyze_document(
                Document={'Bytes': img_bytes},
                FeatureTypes=['FORMS', 'TABLES']
            )
            
            # Parse based on document type
            if document_type == DocumentType.AADHAAR:
                return await self._parse_aadhaar(response)
            elif document_type == DocumentType.PAN:
                return await self._parse_pan(response)
            else:
                return await self._parse_generic(response)
                
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            return {}, {}
    
    async def _parse_aadhaar(self, response: Dict) -> Tuple[Dict, Dict]:
        """Parse Aadhaar card response"""
        extracted = {}
        confidences = {}
        
        # Extract key-value pairs
        for block in response.get('Blocks', []):
            if block['BlockType'] == 'LINE':
                text = block['Text']
                confidence = block['Confidence']
                
                # Look for name (usually first line after "Government of India")
                if 'Name' in text or len(text.split()) <= 3:
                    extracted['name'] = text
                    confidences['name'] = confidence / 100
                
                # Look for DOB
                if 'DOB' in text or '/' in text:
                    extracted['dob'] = text
                    confidences['dob'] = confidence / 100
                
                # Last 4 digits of Aadhaar (only visible part)
                if text.isdigit() and len(text) == 4:
                    extracted['aadhaar_last4'] = text
                    confidences['aadhaar_last4'] = confidence / 100
        
        logger.info(f"Extracted Aadhaar fields: {list(extracted.keys())}")
        return extracted, confidences
    
    async def _parse_pan(self, response: Dict) -> Tuple[Dict, Dict]:
        """Parse PAN card response"""
        # TODO: Implement PAN parsing
        return {}, {}
    
    async def _parse_generic(self, response: Dict) -> Tuple[Dict, Dict]:
        """Parse generic document"""
        extracted = {}
        confidences = {}
        
        # Extract all text
        for block in response.get('Blocks', []):
            if block['BlockType'] == 'LINE':
                text = block['Text']
                extracted[f'line_{block["Id"]}'] = text
                confidences[f'line_{block["Id"]}'] = block['Confidence'] / 100
        
        return extracted, confidences

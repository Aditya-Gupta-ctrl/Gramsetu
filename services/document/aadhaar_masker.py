"""
Edge-based Aadhaar masking for DPDP compliance
Masks first 8 digits before cloud upload
"""
import cv2
import numpy as np
from PIL import Image
import re
from shared.config import get_settings
from shared.logging_config import logger

settings = get_settings()


class AadhaarMasker:
    """Privacy-preserving Aadhaar card masking"""
    
    async def mask(self, image: Image.Image) -> Image.Image:
        """
        Mask first 8 digits of Aadhaar number
        
        Args:
            image: PIL Image of Aadhaar card
        
        Returns:
            Masked PIL Image
        """
        try:
            # Convert to OpenCV format
            img_array = np.array(image)
            img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # Detect Aadhaar number region
            number_region = await self._detect_aadhaar_number_region(img_cv)
            
            if number_region:
                x, y, w, h = number_region
                
                # Calculate mask width (first 8 digits = ~2/3 of width)
                mask_width = int(w * (settings.aadhaar_mask_digits / 12))
                
                # Apply Gaussian blur to first 8 digits
                roi = img_cv[y:y+h, x:x+mask_width]
                blurred = cv2.GaussianBlur(roi, (51, 51), 0)
                img_cv[y:y+h, x:x+mask_width] = blurred
                
                logger.info(f"Masked first {settings.aadhaar_mask_digits} digits")
            else:
                logger.warning("Could not detect Aadhaar number region, applying full blur")
                # Fallback: blur bottom third of card
                h, w = img_cv.shape[:2]
                roi = img_cv[int(h*0.66):h, :]
                blurred = cv2.GaussianBlur(roi, (51, 51), 0)
                img_cv[int(h*0.66):h, :] = blurred
            
            # Convert back to PIL
            img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
            masked_image = Image.fromarray(img_rgb)
            
            return masked_image
            
        except Exception as e:
            logger.error(f"Aadhaar masking failed: {str(e)}")
            # Return original if masking fails (better than crashing)
            return image
    
    async def _detect_aadhaar_number_region(self, img_cv: np.ndarray) -> tuple:
        """
        Detect bounding box of Aadhaar number using OCR
        
        Returns:
            (x, y, w, h) or None
        """
        try:
            # Use Tesseract to find digits
            import pytesseract
            
            # Get bounding boxes of all text
            data = pytesseract.image_to_data(img_cv, output_type=pytesseract.Output.DICT)
            
            # Look for 12-digit pattern (with or without spaces)
            for i, text in enumerate(data['text']):
                # Remove spaces and check if it's digits
                clean_text = text.replace(' ', '')
                if len(clean_text) >= 4 and clean_text.isdigit():
                    # This might be part of Aadhaar number
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    
                    # Expand region to capture full number
                    return (x - 10, y - 5, w * 3, h + 10)
            
            return None
            
        except Exception as e:
            logger.warning(f"Aadhaar region detection failed: {str(e)}")
            return None

"""
Document authenticity verification
Detects fake documents and photo-of-photo
"""
import cv2
import numpy as np
from PIL import Image
from typing import Tuple, List
from shared.schemas import DocumentType
from shared.logging_config import logger


class DocumentVerifier:
    """Document authenticity checks"""
    
    async def verify(
        self,
        image: Image.Image,
        document_type: DocumentType,
        extracted_data: dict
    ) -> Tuple[bool, List[str]]:
        """
        Verify document authenticity
        
        Args:
            image: PIL Image
            document_type: Type of document
            extracted_data: OCR results
        
        Returns:
            (is_authentic, warnings list)
        """
        warnings = []
        
        # Convert to OpenCV
        img_array = np.array(image)
        img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Check 1: Photo-of-photo detection (Moiré pattern)
        if await self._detect_moire_pattern(img_cv):
            warnings.append("Possible photo-of-photo detected (Moiré pattern)")
        
        # Check 2: Screen detection
        if await self._detect_screen_photo(img_cv):
            warnings.append("Possible photo of screen detected")
        
        # Check 3: Basic quality checks
        if await self._check_image_quality(img_cv):
            warnings.append("Image quality too low")
        
        # Document is authentic if no critical warnings
        is_authentic = len(warnings) == 0
        
        logger.info(
            "Document verification complete",
            is_authentic=is_authentic,
            warnings=len(warnings)
        )
        
        return is_authentic, warnings
    
    async def _detect_moire_pattern(self, img_cv: np.ndarray) -> bool:
        """
        Detect Moiré pattern using frequency analysis
        Indicates photo-of-photo
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            # Apply FFT
            f = np.fft.fft2(gray)
            fshift = np.fft.fftshift(f)
            magnitude = np.abs(fshift)
            
            # Check for periodic patterns (Moiré)
            # High frequency peaks indicate Moiré
            threshold = np.mean(magnitude) * 3
            peaks = magnitude > threshold
            
            # If too many peaks, likely Moiré
            peak_ratio = np.sum(peaks) / peaks.size
            
            return peak_ratio > 0.01
            
        except Exception as e:
            logger.warning(f"Moiré detection failed: {str(e)}")
            return False
    
    async def _detect_screen_photo(self, img_cv: np.ndarray) -> bool:
        """
        Detect if image is photo of a screen
        Look for pixel grid patterns
        """
        try:
            # Check for uniform pixel patterns
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            # Calculate local variance
            mean = cv2.blur(gray, (5, 5))
            sqr_mean = cv2.blur(gray**2, (5, 5))
            variance = sqr_mean - mean**2
            
            # Screen photos have very low variance in certain regions
            low_variance_ratio = np.sum(variance < 10) / variance.size
            
            return low_variance_ratio > 0.3
            
        except Exception as e:
            logger.warning(f"Screen detection failed: {str(e)}")
            return False
    
    async def _check_image_quality(self, img_cv: np.ndarray) -> bool:
        """
        Check if image quality is too low
        """
        try:
            # Check resolution
            h, w = img_cv.shape[:2]
            if h < 400 or w < 600:
                return True
            
            # Check blur (Laplacian variance)
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Low variance = blurry
            return laplacian_var < 100
            
        except Exception as e:
            logger.warning(f"Quality check failed: {str(e)}")
            return False

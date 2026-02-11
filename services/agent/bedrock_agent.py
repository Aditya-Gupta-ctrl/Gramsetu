"""
Portal-specific drivers for different government schemes
Each driver knows the URL and expected workflow
"""
from typing import Dict, Any
from shared.schemas import SchemeType
from shared.logging_config import logger


class PortalDriver:
    """Base class for portal-specific drivers"""
    
    def __init__(self, scheme: SchemeType):
        self.scheme = scheme
    
    def get_url(self) -> str:
        """Get portal URL"""
        raise NotImplementedError
    
    def get_workflow(self) -> list[str]:
        """Get expected workflow steps"""
        raise NotImplementedError


class PMKisanDriver(PortalDriver):
    """Driver for PM-KISAN portal"""
    
    def __init__(self):
        super().__init__(SchemeType.PM_KISAN)
    
    def get_url(self) -> str:
        return "https://pmkisan.gov.in/BeneficiaryStatus.aspx"
    
    def get_workflow(self) -> list[str]:
        return [
            "Navigate to beneficiary status page",
            "Select Aadhaar number option",
            "Enter Aadhaar number",
            "Solve CAPTCHA",
            "Click 'Get Data' button",
            "Extract status information",
            "Capture screenshot"
        ]


class EShramDriver(PortalDriver):
    """Driver for e-Shram portal"""
    
    def __init__(self):
        super().__init__(SchemeType.E_SHRAM)
    
    def get_url(self) -> str:
        return "https://eshram.gov.in/user/register"
    
    def get_workflow(self) -> list[str]:
        return [
            "Navigate to registration page",
            "Enter Aadhaar number",
            "Request OTP",
            "Enter OTP",
            "Fill personal details",
            "Upload documents",
            "Submit registration",
            "Capture UAN"
        ]


class BedrockAgentController:
    """Controller for AWS Bedrock Agent integration"""
    
    def __init__(self):
        self.drivers = {
            SchemeType.PM_KISAN: PMKisanDriver(),
            SchemeType.E_SHRAM: EShramDriver(),
            # Add more drivers as needed
        }
        logger.info("Bedrock Agent Controller initialized")
    
    async def get_driver(self, scheme: SchemeType) -> PortalDriver:
        """Get portal-specific driver"""
        driver = self.drivers.get(scheme)
        if not driver:
            raise ValueError(f"No driver available for scheme: {scheme}")
        return driver

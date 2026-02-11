"""
Dialect mapping configuration for rural Indian languages
Maps common rural slang to formal government scheme terms
"""

DIALECT_MAPPINGS = {
    # PM-KISAN scheme variations
    "pm_kisan": {
        "keywords": [
            "pm kisan", "pradhan mantri kisan", "kisan samman nidhi",
            "kisan ka paisa", "khet ka paisa", "farmer money",
            "किसान सम्मान निधि", "किसान का पैसा"
        ],
        "regional_names": {
            "bhojpuri": ["kisan ke paise", "kheti ke rupiya"],
            "marwari": ["kisan ro paiso", "kheti ka dhan"],
            "maithili": ["kisan ke dam", "kheti ke rupiya"]
        }
    },
    
    # e-Shram scheme variations
    "e_shram": {
        "keywords": [
            "e-shram", "eshram", "shram card", "labour card",
            "mazdoor card", "kamgar card", "श्रम कार्ड", "मजदूर कार्ड"
        ],
        "regional_names": {
            "bhojpuri": ["mazdoor ke card", "kamgar patra"],
            "marwari": ["mazdoor ro card", "kamgar patro"],
            "gujarati": ["majur card", "kamdar card"]
        }
    },
    
    # Widow pension variations
    "widow_pension": {
        "keywords": [
            "widow pension", "vidhwa pension", "widow scheme",
            "विधवा पेंशन", "विधवा योजना", "bewa pension"
        ],
        "regional_names": {
            "bhojpuri": ["bidhwa pension", "rand pension"],
            "marwari": ["vidhwa ro pension"],
            "awadhi": ["bidhwa ke pension"]
        }
    },
    
    # Ration card variations
    "ration_card": {
        "keywords": [
            "ration card", "rashan card", "food card",
            "राशन कार्ड", "खाद्य कार्ड", "pds card"
        ],
        "regional_names": {
            "bhojpuri": ["rashan ke card"],
            "marwari": ["rashan ro card"],
            "bengali": ["rashon card"]
        }
    }
}

# Common intent phrase mappings
INTENT_PHRASES = {
    "check_status": [
        "status check", "status dekho", "check karo", "dekhna hai",
        "kya hua", "mila ki nahi", "aaya ki nahi", "status batao",
        "स्टेटस देखो", "क्या हुआ", "मिला की नहीं"
    ],
    
    "apply_new": [
        "apply", "registration", "naya", "new", "banwana hai",
        "form bharna", "apply karna", "registration karna",
        "आवेदन करना", "नया बनवाना", "फॉर्म भरना"
    ],
    
    "update_details": [
        "update", "change", "modify", "badalna", "sudhar",
        "update karna", "change karna", "बदलना", "सुधार"
    ]
}

# Document field name mappings (spoken to formal)
FIELD_MAPPINGS = {
    # Aadhaar variations
    "aadhaar": {
        "spoken": ["aadhar", "uid", "aadhaar number", "आधार"],
        "formal": "aadhaar_number"
    },
    
    # Name variations
    "name": {
        "spoken": ["naam", "name", "नाम", "pura naam"],
        "formal": "full_name"
    },
    
    # Mobile variations
    "mobile": {
        "spoken": ["mobile", "phone", "number", "मोबाइल", "फोन"],
        "formal": "mobile_number"
    },
    
    # Account number variations
    "account": {
        "spoken": ["account", "khata", "bank account", "खाता नंबर"],
        "formal": "account_number"
    },
    
    # Land record variations
    "land": {
        "spoken": ["khata", "khasra", "khatauni", "7/12", "खाता", "खसरा"],
        "formal": "land_record_number"
    }
}

# Phonetic name corrections (common OCR/ASR errors)
PHONETIC_CORRECTIONS = {
    "kumar": ["kumarr", "kumer", "kumaar"],
    "singh": ["sing", "shingh", "singha"],
    "devi": ["debi", "devee", "dewi"],
    "ram": ["raam", "rahm"],
    "sharma": ["sharmaaa", "sharmaa"],
    "yadav": ["yadava", "yadhav"],
    "prasad": ["prashad", "parsad"]
}


def normalize_scheme_name(text: str) -> str:
    """
    Normalize spoken scheme name to formal enum value
    
    Args:
        text: Spoken text (e.g., "kisan ka paisa")
    
    Returns:
        Formal scheme name (e.g., "pm_kisan") or None
    """
    text_lower = text.lower()
    
    for scheme, config in DIALECT_MAPPINGS.items():
        # Check main keywords
        for keyword in config["keywords"]:
            if keyword in text_lower:
                return scheme
        
        # Check regional variations
        for dialect, phrases in config.get("regional_names", {}).items():
            for phrase in phrases:
                if phrase in text_lower:
                    return scheme
    
    return None


def normalize_intent(text: str) -> str:
    """
    Normalize spoken intent to formal enum value
    
    Args:
        text: Spoken text (e.g., "status dekho")
    
    Returns:
        Formal intent (e.g., "check_status") or None
    """
    text_lower = text.lower()
    
    for intent, phrases in INTENT_PHRASES.items():
        for phrase in phrases:
            if phrase in text_lower:
                return intent
    
    return None


def normalize_field_name(spoken_field: str) -> str:
    """
    Normalize spoken field name to formal field name
    
    Args:
        spoken_field: Spoken field (e.g., "aadhar")
    
    Returns:
        Formal field name (e.g., "aadhaar_number")
    """
    spoken_lower = spoken_field.lower()
    
    for field, config in FIELD_MAPPINGS.items():
        for spoken_variant in config["spoken"]:
            if spoken_variant in spoken_lower:
                return config["formal"]
    
    return spoken_field


def correct_name_phonetically(name: str) -> str:
    """
    Correct common phonetic errors in names
    
    Args:
        name: Name with potential errors
    
    Returns:
        Corrected name
    """
    name_lower = name.lower()
    
    for correct, variants in PHONETIC_CORRECTIONS.items():
        for variant in variants:
            if variant in name_lower:
                name_lower = name_lower.replace(variant, correct)
    
    return name_lower.title()

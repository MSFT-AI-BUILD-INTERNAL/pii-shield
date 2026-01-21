"""
Korean-specific PII Recognizers.

Custom recognizers for Korean PII entities such as:
- Korean resident registration number (주민등록번호)
- Korean phone numbers
- Korean names
"""

import re
from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts


class KoreanResidentRegistrationNumberRecognizer(PatternRecognizer):
    """
    Recognizer for Korean Resident Registration Numbers (주민등록번호).
    
    Format: YYMMDD-GNNNNNN (13 digits with hyphen)
    - YYMMDD: Birth date
    - G: Gender and century indicator (1-4 for Korean, 5-8 for foreigners)
    - NNNNNN: Unique identifier
    """
    
    PATTERNS = [
        Pattern(
            "Korean RRN (with hyphen)",
            r"\b\d{6}[-]\d{7}\b",
            0.85,
        ),
        Pattern(
            "Korean RRN (without hyphen)",
            r"\b\d{13}\b",
            0.5,  # Lower confidence without hyphen
        ),
    ]
    
    CONTEXT = [
        "주민등록번호",
        "주민번호",
        "resident registration",
        "rrn",
        "주민",
    ]
    
    def __init__(
        self,
        supported_language: str = "ko",
        supported_entity: str = "KR_RESIDENT_REGISTRATION_NUMBER",
    ):
        super().__init__(
            supported_entity=supported_entity,
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language=supported_language,
        )
    
    def validate_result(self, pattern_text: str) -> Optional[bool]:
        """Validate Korean RRN using checksum."""
        # Remove hyphen if present
        digits = pattern_text.replace("-", "")
        
        if len(digits) != 13:
            return False
        
        # Validate checksum
        weights = [2, 3, 4, 5, 6, 7, 8, 9, 2, 3, 4, 5]
        total = sum(int(d) * w for d, w in zip(digits[:12], weights))
        check_digit = (11 - (total % 11)) % 10
        
        return check_digit == int(digits[12])


class KoreanPhoneNumberRecognizer(PatternRecognizer):
    """
    Recognizer for Korean Phone Numbers.
    
    Formats:
    - Mobile: 010-XXXX-XXXX, 010XXXXXXXX
    - Landline: 02-XXX-XXXX, 031-XXX-XXXX
    """
    
    PATTERNS = [
        Pattern(
            "Korean Mobile (with hyphen)",
            r"\b01[0-9][-]\d{3,4}[-]\d{4}\b",
            0.85,
        ),
        Pattern(
            "Korean Mobile (without hyphen)",
            r"\b01[0-9]\d{7,8}\b",
            0.6,
        ),
        Pattern(
            "Korean Landline (with hyphen)",
            r"\b0\d{1,2}[-]\d{3,4}[-]\d{4}\b",
            0.8,
        ),
    ]
    
    CONTEXT = [
        "전화번호",
        "휴대폰",
        "핸드폰",
        "연락처",
        "phone",
        "mobile",
        "tel",
    ]
    
    def __init__(
        self,
        supported_language: str = "ko",
        supported_entity: str = "KR_PHONE_NUMBER",
    ):
        super().__init__(
            supported_entity=supported_entity,
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language=supported_language,
        )


class KoreanBankAccountRecognizer(PatternRecognizer):
    """
    Recognizer for Korean Bank Account Numbers.
    
    Note: Korean bank account numbers vary by bank (10-14 digits).
    This recognizer uses pattern + context for detection.
    """
    
    PATTERNS = [
        Pattern(
            "Korean Bank Account",
            r"\b\d{3,4}[-]?\d{2,4}[-]?\d{4,6}\b",
            0.4,  # Low base confidence, relies on context
        ),
    ]
    
    CONTEXT = [
        "계좌번호",
        "계좌",
        "은행",
        "bank account",
        "account number",
        "입금",
        "출금",
    ]
    
    def __init__(
        self,
        supported_language: str = "ko",
        supported_entity: str = "KR_BANK_ACCOUNT",
    ):
        super().__init__(
            supported_entity=supported_entity,
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language=supported_language,
        )


class KoreanNameRecognizer(PatternRecognizer):
    """
    Recognizer for Korean Names.
    
    Korean names typically consist of 2-4 Korean characters (Hangul).
    """
    
    PATTERNS = [
        Pattern(
            "Korean Name Pattern",
            r"([가-힣]{2,4})",  # 2-4 character Korean name
            0.7,
        ),
    ]
    
    CONTEXT = [
        "이름",
        "성명",
        "name",
        "씨",
        "님",
    ]
    
    def __init__(
        self,
        supported_language: str = "ko",
        supported_entity: str = "KR_NAME",
    ):
        super().__init__(
            supported_entity=supported_entity,
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language=supported_language,
        )


class KoreanEmailRecognizer(PatternRecognizer):
    """
    Recognizer for Email Addresses (Korean context).
    
    Standard email pattern with Korean context words.
    """
    
    PATTERNS = [
        Pattern(
            "Email Pattern",
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            0.8,
        ),
    ]
    
    CONTEXT = [
        "이메일",
        "메일",
        "email",
        "e-mail",
    ]
    
    def __init__(
        self,
        supported_language: str = "ko",
        supported_entity: str = "KR_EMAIL",
    ):
        super().__init__(
            supported_entity=supported_entity,
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language=supported_language,
        )


class KoreanSSNRecognizer(PatternRecognizer):
    """
    Recognizer for Korean Social Security Numbers (Resident Registration Numbers).
    
    Format: YYMMDD-SXXXXXX
    - YYMMDD: Birth date (Year, Month, Day)
    - S: Gender/Century indicator (1-4 for Korean citizens, 5-8 for foreigners)
    - XXXXXX: Unique identifier
    """
    
    PATTERNS = [
        Pattern(
            "Korean SSN Pattern",
            r"\d{2}[0-1]\d[0-3]\d-?[1-4]\d{6}",  # YYMMDD-SXXXXXX format
            0.9,
        ),
    ]
    
    CONTEXT = [
        "주민등록번호",
        "주민번호",
        "ssn",
        "resident registration",
    ]
    
    def __init__(
        self,
        supported_language: str = "ko",
        supported_entity: str = "KR_SSN",
    ):
        super().__init__(
            supported_entity=supported_entity,
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language=supported_language,
        )


class KoreanRecognizers:
    """
    Factory class for Korean PII recognizers.
    
    Provides methods to get all Korean recognizers for registration
    with Presidio AnalyzerEngine.
    """
    
    @staticmethod
    def get_all_recognizers() -> List[PatternRecognizer]:
        """
        Get all Korean PII recognizers.
        
        Returns:
            List of Korean-specific PatternRecognizer instances.
        """
        return [
            KoreanResidentRegistrationNumberRecognizer(),
            KoreanPhoneNumberRecognizer(),
            KoreanBankAccountRecognizer(),
            KoreanNameRecognizer(),
            KoreanEmailRecognizer(),
            KoreanSSNRecognizer(),
        ]
    
    @staticmethod
    def get_recognizer(entity_type: str) -> Optional[PatternRecognizer]:
        """
        Get a specific Korean recognizer by entity type.
        
        Args:
            entity_type: Entity type name (e.g., "KR_RESIDENT_REGISTRATION_NUMBER").
        
        Returns:
            PatternRecognizer instance or None if not found.
        """
        recognizers = {
            "KR_RESIDENT_REGISTRATION_NUMBER": KoreanResidentRegistrationNumberRecognizer,
            "KR_PHONE_NUMBER": KoreanPhoneNumberRecognizer,
            "KR_BANK_ACCOUNT": KoreanBankAccountRecognizer,
            "KR_NAME": KoreanNameRecognizer,
            "KR_EMAIL": KoreanEmailRecognizer,
            "KR_SSN": KoreanSSNRecognizer,
        }
        
        recognizer_class = recognizers.get(entity_type)
        return recognizer_class() if recognizer_class else None

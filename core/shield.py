"""
PII Shield Module

High-level interface combining PII detection and masking.
Provides a simple API for common PII protection operations.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any

from presidio_analyzer import RecognizerResult

from core.detector import PIIDetector
from core.masker import PIIMasker, MaskingStrategy


@dataclass
class PIIResult:
    """
    Result of PII detection and masking operation.
    
    Attributes:
        original_text: The original input text.
        masked_text: The text with PII masked.
        detected_entities: List of detected PII entities.
        entity_count: Count of each entity type detected.
    """
    original_text: str
    masked_text: str
    detected_entities: List[RecognizerResult]
    entity_count: Dict[str, int]


class PIIShield:
    """
    High-level interface for PII detection and masking.
    
    Combines PIIDetector and PIIMasker into a simple, unified API.
    
    Example:
        >>> shield = PIIShield()
        >>> result = shield.protect("My email is john@example.com")
        >>> print(result.masked_text)  # My email is <EMAIL_ADDRESS>
    """
    
    def __init__(
        self,
        languages: Optional[List[str]] = None,
        default_language: str = "en",
        default_strategy: MaskingStrategy = MaskingStrategy.REPLACE,
    ):
        """
        Initialize PII Shield.
        
        Args:
            languages: List of language codes to support. Defaults to ["en", "ko"].
            default_language: Default language for detection. Defaults to "en".
            default_strategy: Default masking strategy. Defaults to REPLACE.
        """
        self.detector = PIIDetector(
            languages=languages,
            default_language=default_language,
        )
        self.masker = PIIMasker(default_strategy=default_strategy)
        self.default_language = default_language
        self.default_strategy = default_strategy
    
    def protect(
        self,
        text: str,
        language: Optional[str] = None,
        entities: Optional[List[str]] = None,
        strategy: Optional[MaskingStrategy] = None,
        score_threshold: float = 0.5,
    ) -> PIIResult:
        """
        Detect and mask PII in the given text.
        
        Args:
            text: Input text to protect.
            language: Language code of the text. Defaults to default_language.
            entities: List of entity types to detect. Defaults to all.
            strategy: Masking strategy to use. Defaults to default_strategy.
            score_threshold: Minimum confidence score. Defaults to 0.5.
        
        Returns:
            PIIResult containing original text, masked text, and detection details.
        
        Example:
            >>> shield = PIIShield()
            >>> result = shield.protect("Contact: john@example.com, 555-1234")
            >>> print(result.masked_text)
            >>> print(result.entity_count)
        """
        language = language or self.default_language
        strategy = strategy or self.default_strategy
        
        # Detect PII
        detected_entities = self.detector.detect(
            text=text,
            language=language,
            entities=entities,
            score_threshold=score_threshold,
        )
        
        # Mask PII
        masked_text = self.masker.mask(
            text=text,
            analyzer_results=detected_entities,
            strategy=strategy,
        )
        
        # Count entities
        entity_count = self._count_entities(detected_entities)
        
        return PIIResult(
            original_text=text,
            masked_text=masked_text,
            detected_entities=detected_entities,
            entity_count=entity_count,
        )
    
    def protect_batch(
        self,
        texts: List[str],
        language: Optional[str] = None,
        entities: Optional[List[str]] = None,
        strategy: Optional[MaskingStrategy] = None,
        score_threshold: float = 0.5,
    ) -> List[PIIResult]:
        """
        Detect and mask PII in multiple texts.
        
        Args:
            texts: List of input texts to protect.
            language: Language code of the texts. Defaults to default_language.
            entities: List of entity types to detect. Defaults to all.
            strategy: Masking strategy to use. Defaults to default_strategy.
            score_threshold: Minimum confidence score. Defaults to 0.5.
        
        Returns:
            List of PIIResult for each input text.
        """
        return [
            self.protect(text, language, entities, strategy, score_threshold)
            for text in texts
        ]
    
    def detect_only(
        self,
        text: str,
        language: Optional[str] = None,
        entities: Optional[List[str]] = None,
        score_threshold: float = 0.5,
    ) -> List[RecognizerResult]:
        """
        Detect PII without masking.
        
        Args:
            text: Input text to analyze.
            language: Language code. Defaults to default_language.
            entities: List of entity types to detect. Defaults to all.
            score_threshold: Minimum confidence score. Defaults to 0.5.
        
        Returns:
            List of detected PII entities.
        """
        return self.detector.detect(
            text=text,
            language=language,
            entities=entities,
            score_threshold=score_threshold,
        )
    
    def get_supported_entities(self, language: Optional[str] = None) -> List[str]:
        """
        Get list of supported entity types.
        
        Args:
            language: Language code. Defaults to default_language.
        
        Returns:
            List of supported entity type names.
        """
        return self.detector.get_supported_entities(language)
    
    def _count_entities(
        self,
        entities: List[RecognizerResult]
    ) -> Dict[str, int]:
        """Count occurrences of each entity type."""
        count = {}
        for entity in entities:
            entity_type = entity.entity_type
            count[entity_type] = count.get(entity_type, 0) + 1
        return count
    
    def to_dict(self, result: PIIResult) -> Dict[str, Any]:
        """
        Convert PIIResult to dictionary.
        
        Useful for JSON serialization.
        
        Args:
            result: PIIResult to convert.
        
        Returns:
            Dictionary representation of the result.
        """
        return {
            "original_text": result.original_text,
            "masked_text": result.masked_text,
            "detected_entities": [
                {
                    "entity_type": e.entity_type,
                    "start": e.start,
                    "end": e.end,
                    "score": e.score,
                }
                for e in result.detected_entities
            ],
            "entity_count": result.entity_count,
        }

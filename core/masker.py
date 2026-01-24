"""
PII Masker Module

Uses Microsoft Presidio Anonymizer for PII masking/anonymization.
Supports various masking strategies.
"""

from enum import Enum
from typing import Dict, List, Optional, Union

from presidio_analyzer import RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig, OperatorResult


class MaskingStrategy(Enum):
    """Supported masking strategies."""
    
    REPLACE = "replace"  # Replace with a fixed string (e.g., <PERSON>)
    REDACT = "redact"  # Remove completely
    HASH = "hash"  # Replace with hash value
    MASK = "mask"  # Replace with mask characters (e.g., ****)
    ENCRYPT = "encrypt"  # Encrypt the value
    CUSTOM = "custom"  # Custom anonymization


class PIIMasker:
    """
    PII Masker using Microsoft Presidio Anonymizer.
    
    Provides various masking strategies for detected PII entities.
    """
    
    def __init__(self, default_strategy: MaskingStrategy = MaskingStrategy.REPLACE):
        """
        Initialize PII Masker.
        
        Args:
            default_strategy: Default masking strategy to use. Defaults to REPLACE.
        """
        self.default_strategy = default_strategy
        self.anonymizer = AnonymizerEngine()
    
    def mask(
        self,
        text: str,
        analyzer_results: List[RecognizerResult],
        strategy: Optional[MaskingStrategy] = None,
        operators: Optional[Dict[str, OperatorConfig]] = None,
    ) -> str:
        """
        Mask PII entities in the given text.
        
        Args:
            text: Original text containing PII.
            analyzer_results: List of detected PII entities from PIIDetector.
            strategy: Masking strategy to use. Defaults to default_strategy.
            operators: Custom operators for specific entity types.
        
        Returns:
            Anonymized text with PII masked.
        
        Example:
            >>> masker = PIIMasker()
            >>> masked_text = masker.mask(
            ...     "My email is john@example.com",
            ...     analyzer_results
            ... )
            >>> print(masked_text)  # My email is <EMAIL_ADDRESS>
        """
        strategy = strategy or self.default_strategy
        
        if operators is None:
            operators = self._get_default_operators(strategy, analyzer_results)
        
        result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=analyzer_results,
            operators=operators,
        )
        
        return result.text
    
    def mask_with_details(
        self,
        text: str,
        analyzer_results: List[RecognizerResult],
        strategy: Optional[MaskingStrategy] = None,
        operators: Optional[Dict[str, OperatorConfig]] = None,
    ) -> tuple:
        """
        Mask PII entities and return detailed results.
        
        Args:
            text: Original text containing PII.
            analyzer_results: List of detected PII entities from PIIDetector.
            strategy: Masking strategy to use. Defaults to default_strategy.
            operators: Custom operators for specific entity types.
        
        Returns:
            Tuple of (anonymized_text, list of OperatorResult).
        """
        strategy = strategy or self.default_strategy
        
        if operators is None:
            operators = self._get_default_operators(strategy, analyzer_results)
        
        result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=analyzer_results,
            operators=operators,
        )
        
        return result.text, result.items
    
    def _get_default_operators(
        self,
        strategy: MaskingStrategy,
        analyzer_results: List[RecognizerResult],
    ) -> Dict[str, OperatorConfig]:
        """
        Get default operators based on masking strategy.
        
        Args:
            strategy: Masking strategy to use.
            analyzer_results: List of detected entities.
        
        Returns:
            Dictionary mapping entity types to OperatorConfig.
        """
        entity_types = set(result.entity_type for result in analyzer_results)
        operators = {}
        
        for entity_type in entity_types:
            if strategy == MaskingStrategy.REPLACE:
                operators[entity_type] = OperatorConfig(
                    "replace",
                    {"new_value": f"<{entity_type}>"}
                )
            elif strategy == MaskingStrategy.REDACT:
                operators[entity_type] = OperatorConfig("redact")
            elif strategy == MaskingStrategy.HASH:
                operators[entity_type] = OperatorConfig(
                    "hash",
                    {"hash_type": "sha256"}
                )
            elif strategy == MaskingStrategy.MASK:
                # Mask with '*' characters only (no labels)
                operators[entity_type] = OperatorConfig(
                    "mask",
                    {"chars_to_mask": 100, "masking_char": "*", "from_end": False}
                )
            elif strategy == MaskingStrategy.ENCRYPT:
                # Note: Encryption requires a key to be provided
                operators[entity_type] = OperatorConfig(
                    "replace",
                    {"new_value": f"[ENCRYPTED:{entity_type}]"}
                )
        
        return operators
    
    def create_custom_operator(
        self,
        operator_type: str,
        params: Optional[Dict] = None,
    ) -> OperatorConfig:
        """
        Create a custom operator configuration.
        
        Args:
            operator_type: Type of operator (replace, redact, hash, mask, encrypt).
            params: Parameters for the operator.
        
        Returns:
            OperatorConfig instance.
        
        Example:
            >>> masker = PIIMasker()
            >>> custom_op = masker.create_custom_operator(
            ...     "replace",
            ...     {"new_value": "[HIDDEN]"}
            ... )
        """
        return OperatorConfig(operator_type, params or {})

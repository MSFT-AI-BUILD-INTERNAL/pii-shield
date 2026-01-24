"""
PII Shield Module

High-level interface combining PII detection and masking.
Provides a simple API for common PII protection operations.

Supports both:
- Azure Language Service (cloud-based, requires AZURE_FOUNDRY_ENDPOINT)
- Presidio (local, used as fallback or when Azure not configured)
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

from presidio_analyzer import RecognizerResult

from core.detector import PIIDetector
from core.masker import PIIMasker, MaskingStrategy

# Try to import Azure PII components
try:
    from core.azure_pii import (
        AzurePIIDetector,
        AzureRedactionPolicy,
        is_azure_sdk_available,
        is_azure_identity_available,
    )
    AZURE_AVAILABLE = is_azure_sdk_available() and is_azure_identity_available()
except ImportError:
    AZURE_AVAILABLE = False
    AzurePIIDetector = None
    AzureRedactionPolicy = None


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
    
    Detection Modes:
    - Auto-detect (default): If AZURE_FOUNDRY_ENDPOINT is set, uses BOTH 
      Azure and Presidio, merging results for maximum coverage.
    - azure_only=True: Uses only Azure without Presidio.
    - use_azure=False: Uses only Presidio without Azure.
    
    Example:
        >>> shield = PIIShield()
        >>> result = shield.protect("My email is john@example.com")
        >>> print(result.masked_text)  # Uses both Azure and Presidio
    """
    
    def __init__(
        self,
        languages: Optional[List[str]] = None,
        default_language: str = "en",
        default_strategy: MaskingStrategy = MaskingStrategy.REPLACE,
        use_azure: Optional[bool] = None,
        azure_only: bool = False,
    ):
        """
        Initialize PII Shield.
        
        Args:
            languages: List of language codes to support. Defaults to ["en", "ko"].
            default_language: Default language for detection. Defaults to "en".
            default_strategy: Default masking strategy. Defaults to REPLACE.
            use_azure: Force Azure usage. If None, auto-detects from AZURE_FOUNDRY_ENDPOINT.
                       If True, requires Azure credentials. If False, uses only Presidio.
            azure_only: If True, uses Azure only without Presidio fallback. 
                        Requires AZURE_FOUNDRY_ENDPOINT to be set. Defaults to False.
        """
        self.default_language = default_language
        self.default_strategy = default_strategy
        self.azure_only = azure_only
        
        # Check if Azure should be used
        azure_endpoint = os.environ.get("AZURE_FOUNDRY_ENDPOINT") or os.environ.get("AZURE_LANGUAGE_ENDPOINT")
        
        # If azure_only is True, require Azure endpoint
        if azure_only and azure_endpoint is None:
            raise ValueError(
                "azure_only=True requires AZURE_FOUNDRY_ENDPOINT to be set.\n"
                "Please set AZURE_FOUNDRY_ENDPOINT environment variable."
            )
        
        # If Azure endpoint is configured but SDK is not available, fail immediately
        if azure_endpoint is not None and not AZURE_AVAILABLE:
            raise ImportError(
                f"AZURE_FOUNDRY_ENDPOINT is set to '{azure_endpoint}' but Azure SDK is not installed.\n"
                "Please install Azure dependencies with: pip install pii-shield[azure]\n"
                "Or unset AZURE_FOUNDRY_ENDPOINT to use Presidio-only mode."
            )
        
        if use_azure is None:
            # Auto-detect: use Azure if endpoint is configured and SDK is available
            self.use_azure = AZURE_AVAILABLE and azure_endpoint is not None
        else:
            # Explicit configuration
            self.use_azure = use_azure and AZURE_AVAILABLE and azure_endpoint is not None
        
        # Initialize Azure detector if enabled
        self.azure_detector = None
        if self.use_azure:
            try:
                self.azure_detector = AzurePIIDetector(
                    endpoint=azure_endpoint,
                    default_language=default_language,
                    redaction_policy=AzureRedactionPolicy.CHARACTER_MASK,
                )
            except Exception as e:
                if azure_only:
                    # In azure_only mode, fail immediately if Azure initialization fails
                    raise RuntimeError(
                        f"Failed to initialize Azure PII Detector in azure_only mode: {e}"
                    ) from e
                else:
                    # Failed to initialize Azure, will fallback to Presidio
                    print(f"Warning: Failed to initialize Azure PII Detector: {e}")
                    print("Falling back to Presidio local detection.")
                    self.use_azure = False
                    self.azure_detector = None
        
        # Initialize Presidio detector unless in azure_only mode
        self.detector = None
        self.masker = PIIMasker(default_strategy=default_strategy)  # Always initialize masker
        
        if not azure_only:
            self.detector = PIIDetector(
                languages=languages,
                default_language=default_language,
            )
    
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
        
        In default mode (auto-detect): Uses BOTH Azure and Presidio, merging results.
        In azure_only mode: Uses only Azure.
        In use_azure=False mode: Uses only Presidio.
        
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
        
        detected_entities = []
        
        # Azure-only mode: Use only Azure
        if self.azure_only:
            azure_entities = self._detect_with_azure(text, language)
            detected_entities = azure_entities
        # Default mode with Azure available: Use BOTH Azure and Presidio
        elif self.use_azure and self.azure_detector and self.detector:
            # Run both detectors
            azure_entities = self._detect_with_azure(text, language, raise_on_error=False)
            presidio_entities = self._detect_with_presidio(text, language, entities, score_threshold)
            
            # Merge results (union of both)
            detected_entities = self._merge_entities(azure_entities, presidio_entities)
        # Presidio-only mode or Azure not available
        else:
            detected_entities = self._detect_with_presidio(
                text, language, entities, score_threshold
            )
        
        # Mask PII
        masked_text = self.masker.mask(text, detected_entities, strategy)
        
        # Count entities
        entity_count = self._count_entities(detected_entities)
        
        return PIIResult(
            original_text=text,
            masked_text=masked_text,
            detected_entities=detected_entities,
            entity_count=entity_count,
        )
    
    def _detect_with_azure(
        self,
        text: str,
        language: str,
        raise_on_error: bool = True,
    ) -> List[RecognizerResult]:
        """
        Helper method to detect PII using Azure.
        
        Args:
            text: Input text to analyze.
            language: Language code.
            raise_on_error: If True, raise RuntimeError on failure. 
                           If False, return empty list on failure.
        
        Returns:
            List of detected entities in Presidio format.
        """
        try:
            azure_result = self.azure_detector.detect(text, language=language)
            
            if not azure_result.is_error:
                # Azure succeeded - convert to Presidio format
                return self._convert_azure_to_presidio(azure_result)
            else:
                # Azure failed
                if raise_on_error:
                    raise RuntimeError(
                        f"Azure PII detection failed: {azure_result.error_message}"
                    )
                else:
                    print(f"Warning: Azure detection failed: {azure_result.error_message}")
                    return []
        except Exception as e:
            if raise_on_error:
                raise RuntimeError(f"Azure detection failed: {e}") from e
            else:
                print(f"Warning: Azure detection error: {e}")
                return []
    
    def _detect_with_presidio(
        self,
        text: str,
        language: str,
        entities: Optional[List[str]],
        score_threshold: float,
    ) -> List[RecognizerResult]:
        """Helper method to detect PII using Presidio."""
        if self.detector is None:
            raise RuntimeError(
                "Presidio detector is not initialized. "
                "This should not happen unless azure_only=True."
            )
        return self.detector.detect(
            text=text,
            language=language,
            entities=entities,
            score_threshold=score_threshold,
        )
    
    def _convert_azure_to_presidio(self, azure_result) -> List[RecognizerResult]:
        """Convert Azure PII entities to Presidio RecognizerResult format."""
        presidio_results = []
        
        for entity in azure_result.entities:
            # Map Azure category to Presidio entity type
            entity_type = AzurePIIDetector.CATEGORY_MAPPING.get(
                entity.category, 
                entity.category.upper()
            )
            
            # Create RecognizerResult
            result = RecognizerResult(
                entity_type=entity_type,
                start=entity.offset,
                end=entity.offset + entity.length,
                score=entity.confidence_score,
            )
            presidio_results.append(result)
        
        return presidio_results
    
    def _merge_entities(
        self,
        azure_entities: List[RecognizerResult],
        presidio_entities: List[RecognizerResult],
    ) -> List[RecognizerResult]:
        """
        Merge entities from Azure and Presidio with strict rule:
        When entities overlap, choose the one with wider coverage.
        
        This ensures maximum PII masking. For example:
        - Azure detects "세종" (positions 0-2)
        - Presidio detects "세종대왕" (positions 0-4)
        - Result: "세종대왕" is chosen (wider coverage)
        
        Args:
            azure_entities: Entities detected by Azure.
            presidio_entities: Entities detected by Presidio.
        
        Returns:
            Merged list with maximum coverage entities.
        """
        # Combine all entities
        all_entities = azure_entities + presidio_entities
        
        if not all_entities:
            return []
        
        # Sort by start position, then by length (descending) for priority
        all_entities.sort(key=lambda x: (x.start, -(x.end - x.start)))
        
        # Use a greedy approach: select entities that don't overlap with already selected ones
        # But when they do overlap, keep the one with wider coverage
        merged = []
        
        for entity in all_entities:
            should_add = True
            entities_to_remove = []
            
            for i, existing in enumerate(merged):
                # Check if current entity overlaps with existing
                if self._entities_overlap_simple(entity, existing):
                    # They overlap - keep the wider one
                    entity_length = entity.end - entity.start
                    existing_length = existing.end - existing.start
                    
                    if entity_length > existing_length:
                        # Current entity is wider, remove existing and add current
                        entities_to_remove.append(i)
                    else:
                        # Existing is wider or equal, skip current
                        should_add = False
                        break
            
            # Remove entities that are narrower
            for i in reversed(entities_to_remove):
                merged.pop(i)
            
            if should_add:
                merged.append(entity)
        
        # Sort by start position for final result
        merged.sort(key=lambda x: x.start)
        
        return merged
    
    def _entities_overlap_simple(
        self,
        entity1: RecognizerResult,
        entity2: RecognizerResult,
    ) -> bool:
        """
        Check if two entities overlap.
        
        Args:
            entity1: First entity.
            entity2: Second entity.
        
        Returns:
            True if entities overlap.
        """
        # Check if there's any overlap
        return not (entity1.end <= entity2.start or entity1.start >= entity2.end)
    
    def _entities_overlap(
        self,
        entity1: RecognizerResult,
        entity2: RecognizerResult,
        overlap_threshold: float = 0.5,
    ) -> bool:
        """
        Check if two entities overlap significantly.
        
        Args:
            entity1: First entity.
            entity2: Second entity.
            overlap_threshold: Minimum overlap ratio to consider as duplicate.
        
        Returns:
            True if entities overlap significantly.
        """
        # Calculate overlap
        start = max(entity1.start, entity2.start)
        end = min(entity1.end, entity2.end)
        
        if start >= end:
            # No overlap
            return False
        
        overlap_length = end - start
        entity1_length = entity1.end - entity1.start
        entity2_length = entity2.end - entity2.start
        
        # Calculate overlap ratio relative to shorter entity
        min_length = min(entity1_length, entity2_length)
        overlap_ratio = overlap_length / min_length if min_length > 0 else 0
        
        return overlap_ratio >= overlap_threshold
    
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
        
        In default mode (auto-detect): Uses BOTH Azure and Presidio, merging results.
        In azure_only mode: Uses only Azure.
        In use_azure=False mode: Uses only Presidio.
        
        Args:
            text: Input text to analyze.
            language: Language code. Defaults to default_language.
            entities: List of entity types to detect. Defaults to all.
            score_threshold: Minimum confidence score. Defaults to 0.5.
        
        Returns:
            List of detected PII entities.
        """
        language = language or self.default_language
        
        # Azure-only mode: Use only Azure
        if self.azure_only:
            return self._detect_with_azure(text, language, raise_on_error=True)
        # Default mode with Azure available: Use BOTH Azure and Presidio
        elif self.use_azure and self.azure_detector and self.detector:
            # Run both detectors
            azure_entities = self._detect_with_azure(text, language, raise_on_error=False)
            presidio_entities = self._detect_with_presidio(text, language, entities, score_threshold)
            
            # Merge results (union of both)
            return self._merge_entities(azure_entities, presidio_entities)
        # Presidio-only mode or Azure not available
        else:
            return self._detect_with_presidio(
                text, language, entities, score_threshold
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

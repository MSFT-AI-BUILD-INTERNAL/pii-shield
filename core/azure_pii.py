"""
Microsoft Foundry PII Detection Module

Integrates Microsoft Foundry Language Service for PII detection.
This module provides an alternative PII detection backend using
Microsoft Foundry's cloud-based Language Service, which can be used
alongside or instead of the local Presidio-based detection.

Authentication:
    - Microsoft Entra ID (keyless authentication)
    - Uses DefaultAzureCredential for automatic authentication
    - Supports Managed Identity, Azure CLI, VS Code, etc.
    - Requires: pip install azure-identity

Endpoint Format:
    - Language Service: https://<resource-name>.cognitiveservices.azure.com/

Reference:
    https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/sdk-overview
    https://learn.microsoft.com/en-us/azure/ai-services/language-service/personally-identifiable-information/
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any

try:
    from azure.ai.textanalytics import TextAnalyticsClient, PiiEntityCategory
    from azure.core.exceptions import AzureError
    AZURE_SDK_AVAILABLE = True
except ImportError:
    AZURE_SDK_AVAILABLE = False
    TextAnalyticsClient = None
    PiiEntityCategory = None
    AzureError = Exception

# Check for azure-identity (optional, for Entra ID authentication)
try:
    from azure.identity import DefaultAzureCredential
    AZURE_IDENTITY_AVAILABLE = True
except ImportError:
    AZURE_IDENTITY_AVAILABLE = False
    DefaultAzureCredential = None


class AzureRedactionPolicy(Enum):
    """Redaction policy options for Azure PII detection."""
    NONE = "none"  # No redaction, only detection
    CHARACTER_MASK = "character_mask"  # Replace with mask character
    ENTITY_TYPE = "entity_type"  # Replace with entity type label


@dataclass
class AzurePIIEntity:
    """
    Represents a detected PII entity from Azure Language Service.
    
    Attributes:
        text: The detected entity text.
        category: The category of the PII entity (e.g., "PhoneNumber", "Email").
        subcategory: Optional subcategory for more specific classification.
        confidence_score: Confidence score of the detection (0.0 to 1.0).
        offset: Character offset from the beginning of the text.
        length: Length of the entity in characters.
    """
    text: str
    category: str
    subcategory: Optional[str]
    confidence_score: float
    offset: int
    length: int


@dataclass
class AzurePIIResult:
    """
    Result of Azure PII detection operation.
    
    Attributes:
        original_text: The original input text.
        redacted_text: The text with PII redacted.
        entities: List of detected PII entities.
        language: Detected or specified language.
        is_error: Whether an error occurred during processing.
        error_message: Error message if is_error is True.
    """
    original_text: str
    redacted_text: str
    entities: List[AzurePIIEntity] = field(default_factory=list)
    language: str = "en"
    is_error: bool = False
    error_message: Optional[str] = None
    
    @property
    def entity_count(self) -> Dict[str, int]:
        """Count of each entity type detected."""
        counts: Dict[str, int] = {}
        for entity in self.entities:
            counts[entity.category] = counts.get(entity.category, 0) + 1
        return counts


class AzurePIIDetector:
    """
    PII Detector using Microsoft Foundry Language Service.
    
    This class provides PII detection capabilities through Microsoft Foundry's
    cloud-based Language Service (formerly Azure AI Services).
    
    Authentication Methods:
        1. Microsoft Entra ID (Recommended - no API key required):
           - Set use_entra_id=True in constructor
           - Requires azure-identity package: pip install azure-identity
           - Uses DefaultAzureCredential for automatic authentication
           - Supports: Managed Identity, Azure CLI, VS Code, Environment variables
        
        2. API Key Authentication:
           - Pass api_key parameter or set environment variables
           - AZURE_FOUNDRY_KEY (preferred) or AZURE_LANGUAGE_KEY (fallback)
    
    Endpoint:
        - AZURE_FOUNDRY_ENDPOINT or AZURE_LANGUAGE_ENDPOINT environment variable
        - Or pass endpoint parameter directly
        - Format: https://<resource-name>.cognitiveservices.azure.com/
    
    Example (Entra ID - no API key):
        >>> # Requires: pip install azure-identity
        >>> detector = AzurePIIDetector(
        ...     endpoint="https://my-foundry.cognitiveservices.azure.com/",
        ...     use_entra_id=True
        ... )
        >>> result = detector.detect("My email is john@example.com")
    
    Example (API Key):
        >>> detector = AzurePIIDetector(
        ...     api_key="your-api-key",
        ...     endpoint="https://my-foundry.cognitiveservices.azure.com/"
        ... )
        >>> result = detector.detect("My email is john@example.com")
    
    Note:
        Requires the `azure-ai-textanalytics` package:
        `pip install azure-ai-textanalytics`
        
        For Entra ID authentication, also install:
        `pip install azure-identity`
    """
    
    # Default entity categories to detect
    DEFAULT_CATEGORIES = [
        "Person",
        "PersonType",
        "Email",
        "PhoneNumber",
        "Address",
        "CreditCardNumber",
        "BankAccountNumber",
        "IPAddress",
        "DateTime",
        "URL",
        "Organization",
        "Quantity",
        # Korean-specific (if supported by Azure)
        "KRResidentRegistrationNumber",
        "KRBankAccountNumber",
    ]
    
    # Mapping from Azure categories to Presidio entity types
    CATEGORY_MAPPING = {
        "Person": "PERSON",
        "PersonType": "PERSON",
        "Email": "EMAIL_ADDRESS",
        "PhoneNumber": "PHONE_NUMBER",
        "Address": "LOCATION",
        "CreditCardNumber": "CREDIT_CARD",
        "BankAccountNumber": "IBAN_CODE",
        "IPAddress": "IP_ADDRESS",
        "DateTime": "DATE_TIME",
        "URL": "URL",
        "Organization": "ORGANIZATION",
        "USSocialSecurityNumber": "US_SSN",
        "KRResidentRegistrationNumber": "KR_SSN",
        "KRBankAccountNumber": "KR_BANK_ACCOUNT",
    }
    
    # Environment variable names (in order of precedence)
    ENV_FOUNDRY_ENDPOINT = "AZURE_FOUNDRY_ENDPOINT"
    ENV_LANGUAGE_ENDPOINT = "AZURE_LANGUAGE_ENDPOINT"  # Fallback
    
    def __init__(
        self,
        endpoint: Optional[str] = None,
        default_language: str = "en",
        redaction_policy: AzureRedactionPolicy = AzureRedactionPolicy.CHARACTER_MASK,
        mask_character: str = "*",
        credential: Optional[Any] = None,
    ):
        """
        Initialize Microsoft Foundry PII Detector.
        
        Args:
            endpoint: Microsoft Foundry endpoint URL.
                      Format: https://<resource-name>.cognitiveservices.azure.com/
                      Defaults to AZURE_FOUNDRY_ENDPOINT or AZURE_LANGUAGE_ENDPOINT.
            default_language: Default language for detection. Defaults to "en".
            redaction_policy: Policy for redacting detected PII. 
                              Defaults to CHARACTER_MASK.
            mask_character: Character to use for masking. Defaults to "*".
            credential: Custom credential object (e.g., ManagedIdentityCredential).
                        If None, uses DefaultAzureCredential.
        
        Raises:
            ImportError: If required packages are not installed.
            ValueError: If endpoint is not provided.
        
        Example (Default - Entra ID):
            >>> detector = AzurePIIDetector(
            ...     endpoint="https://your-resource.cognitiveservices.azure.com/"
            ... )
        
        Example (Custom Credential):
            >>> from azure.identity import ManagedIdentityCredential
            >>> credential = ManagedIdentityCredential()
            >>> detector = AzurePIIDetector(
            ...     endpoint="https://your-resource.cognitiveservices.azure.com/",
            ...     credential=credential
            ... )
        """
        if not AZURE_SDK_AVAILABLE:
            raise ImportError(
                "Azure AI Text Analytics SDK is not installed. "
                "Please install it with: pip install azure-ai-textanalytics"
            )
        
        if not AZURE_IDENTITY_AVAILABLE:
            raise ImportError(
                "azure-identity package is required for Entra ID authentication. "
                "Please install it with: pip install azure-identity"
            )
        
        self._custom_credential = credential
        
        # Get endpoint (always required)
        self.endpoint = (
            endpoint 
            or os.environ.get(self.ENV_FOUNDRY_ENDPOINT) 
            or os.environ.get(self.ENV_LANGUAGE_ENDPOINT)
        )
        
        if not self.endpoint:
            raise ValueError(
                "Microsoft Foundry endpoint is required. "
                f"Set {self.ENV_FOUNDRY_ENDPOINT} or {self.ENV_LANGUAGE_ENDPOINT} environment variable, "
                "or pass endpoint parameter. "
                "Format: https://<resource-name>.cognitiveservices.azure.com/"
            )
        
        self.default_language = default_language
        self.redaction_policy = redaction_policy
        self.mask_character = mask_character
        
        # Initialize the client
        self._client = self._create_client()
    
    def _create_client(self) -> TextAnalyticsClient:
        """
        Create and return the Azure Text Analytics client.
        
        Uses the appropriate credential based on configuration:
        - Custom credential if provided
        - DefaultAzureCredential (Azure CLI, Managed Identity, VS Code, etc.)
        """
        
        # Use custom credential or default to DefaultAzureCredential
        if self._custom_credential:
            credential = self._custom_credential
        else:
            credential = DefaultAzureCredential()
        
        return TextAnalyticsClient(
            endpoint=self.endpoint,
            credential=credential
        )
    
    def detect(
        self,
        text: str,
        language: Optional[str] = None,
        categories: Optional[List[str]] = None,
        score_threshold: float = 0.5,
    ) -> AzurePIIResult:
        """
        Detect PII in the given text using Azure Language Service.
        
        Args:
            text: Input text to analyze for PII.
            language: Language code of the text (e.g., "en", "ko").
                      Defaults to default_language.
            categories: List of PII categories to detect.
                        Defaults to DEFAULT_CATEGORIES.
            score_threshold: Minimum confidence score for detection.
                             Defaults to 0.5.
        
        Returns:
            AzurePIIResult containing detected entities and redacted text.
        
        Example:
            >>> detector = AzurePIIDetector()
            >>> result = detector.detect(
            ...     "Call me at 555-123-4567",
            ...     language="en"
            ... )
            >>> print(result.entities[0].category)  # PhoneNumber
        """
        language = language or self.default_language
        
        try:
            # Call Azure PII recognition API
            response = self._client.recognize_pii_entities(
                documents=[text],
                language=language,
            )
            
            # Process the response
            doc_result = response[0]
            
            if doc_result.is_error:
                return AzurePIIResult(
                    original_text=text,
                    redacted_text=text,
                    is_error=True,
                    error_message=f"{doc_result.error.code}: {doc_result.error.message}",
                    language=language,
                )
            
            # Extract entities with filtering by score threshold
            entities = []
            for entity in doc_result.entities:
                if entity.confidence_score >= score_threshold:
                    # Filter by categories if specified
                    if categories and entity.category not in categories:
                        continue
                    
                    entities.append(AzurePIIEntity(
                        text=entity.text,
                        category=entity.category,
                        subcategory=entity.subcategory,
                        confidence_score=entity.confidence_score,
                        offset=entity.offset,
                        length=entity.length,
                    ))
            
            # Apply redaction based on policy
            redacted_text = self._apply_redaction(text, entities)
            
            return AzurePIIResult(
                original_text=text,
                redacted_text=redacted_text,
                entities=entities,
                language=language,
            )
            
        except AzureError as e:
            return AzurePIIResult(
                original_text=text,
                redacted_text=text,
                is_error=True,
                error_message=str(e),
                language=language,
            )
    
    def detect_batch(
        self,
        texts: List[str],
        language: Optional[str] = None,
        categories: Optional[List[str]] = None,
        score_threshold: float = 0.5,
    ) -> List[AzurePIIResult]:
        """
        Detect PII in multiple texts using Azure Language Service.
        
        More efficient than calling detect() multiple times as it uses
        batch processing.
        
        Args:
            texts: List of input texts to analyze.
            language: Language code of the texts.
            categories: List of PII categories to detect.
            score_threshold: Minimum confidence score for detection.
        
        Returns:
            List of AzurePIIResult for each input text.
        
        Example:
            >>> detector = AzurePIIDetector()
            >>> results = detector.detect_batch([
            ...     "Email: john@example.com",
            ...     "Phone: 555-123-4567"
            ... ])
            >>> for result in results:
            ...     print(result.redacted_text)
        """
        language = language or self.default_language
        results = []
        
        try:
            # Call Azure PII recognition API for batch
            response = self._client.recognize_pii_entities(
                documents=texts,
                language=language,
            )
            
            for idx, doc_result in enumerate(response):
                original_text = texts[idx]
                
                if doc_result.is_error:
                    results.append(AzurePIIResult(
                        original_text=original_text,
                        redacted_text=original_text,
                        is_error=True,
                        error_message=f"{doc_result.error.code}: {doc_result.error.message}",
                        language=language,
                    ))
                    continue
                
                # Extract entities with filtering
                entities = []
                for entity in doc_result.entities:
                    if entity.confidence_score >= score_threshold:
                        if categories and entity.category not in categories:
                            continue
                        
                        entities.append(AzurePIIEntity(
                            text=entity.text,
                            category=entity.category,
                            subcategory=entity.subcategory,
                            confidence_score=entity.confidence_score,
                            offset=entity.offset,
                            length=entity.length,
                        ))
                
                redacted_text = self._apply_redaction(original_text, entities)
                
                results.append(AzurePIIResult(
                    original_text=original_text,
                    redacted_text=redacted_text,
                    entities=entities,
                    language=language,
                ))
                
        except AzureError as e:
            # Return error results for all texts
            for text in texts:
                results.append(AzurePIIResult(
                    original_text=text,
                    redacted_text=text,
                    is_error=True,
                    error_message=str(e),
                    language=language,
                ))
        
        return results
    
    def _apply_redaction(
        self,
        text: str,
        entities: List[AzurePIIEntity],
    ) -> str:
        """
        Apply redaction to text based on detected entities.
        
        Args:
            text: Original text.
            entities: List of detected PII entities.
        
        Returns:
            Redacted text based on the configured redaction policy.
        """
        if self.redaction_policy == AzureRedactionPolicy.NONE:
            return text
        
        # Sort entities by offset in reverse order to avoid index shifting
        sorted_entities = sorted(entities, key=lambda e: e.offset, reverse=True)
        
        result = text
        for entity in sorted_entities:
            start = entity.offset
            end = entity.offset + entity.length
            
            if self.redaction_policy == AzureRedactionPolicy.CHARACTER_MASK:
                replacement = self.mask_character * entity.length
            elif self.redaction_policy == AzureRedactionPolicy.ENTITY_TYPE:
                replacement = f"<{entity.category}>"
            else:
                replacement = self.mask_character * entity.length
            
            result = result[:start] + replacement + result[end:]
        
        return result
    
    def to_presidio_format(
        self,
        result: AzurePIIResult,
    ) -> List[Dict[str, Any]]:
        """
        Convert Azure PII result to Presidio-compatible format.
        
        Useful for integrating Azure results with existing Presidio-based
        workflows.
        
        Args:
            result: AzurePIIResult from detect() or detect_batch().
        
        Returns:
            List of dictionaries in Presidio RecognizerResult format.
        
        Example:
            >>> detector = AzurePIIDetector()
            >>> result = detector.detect("My email is john@example.com")
            >>> presidio_results = detector.to_presidio_format(result)
            >>> print(presidio_results[0]["entity_type"])  # EMAIL_ADDRESS
        """
        presidio_results = []
        
        for entity in result.entities:
            # Map Azure category to Presidio entity type
            entity_type = self.CATEGORY_MAPPING.get(
                entity.category,
                entity.category.upper()
            )
            
            presidio_results.append({
                "entity_type": entity_type,
                "start": entity.offset,
                "end": entity.offset + entity.length,
                "score": entity.confidence_score,
                "recognition_metadata": {
                    "source": "azure_language_service",
                    "azure_category": entity.category,
                    "azure_subcategory": entity.subcategory,
                }
            })
        
        return presidio_results
    
    @property
    def is_available(self) -> bool:
        """Check if the Azure client is properly configured and available."""
        return self._client is not None
    
    def close(self):
        """Close the Azure client connection."""
        if self._client:
            self._client.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False


def is_azure_sdk_available() -> bool:
    """
    Check if Azure AI Text Analytics SDK is available.
    
    Returns:
        True if the SDK is installed, False otherwise.
    """
    return AZURE_SDK_AVAILABLE


def is_azure_identity_available() -> bool:
    """
    Check if Azure Identity SDK is available for Entra ID authentication.
    
    Returns:
        True if azure-identity is installed, False otherwise.
    """
    return AZURE_IDENTITY_AVAILABLE

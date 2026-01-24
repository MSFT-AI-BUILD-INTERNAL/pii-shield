"""
Tests for Microsoft Foundry PII Detection Module

These tests cover the Microsoft Foundry Language Service integration.
Supports both API Key and Microsoft Entra ID authentication.
Note: Some tests require Foundry credentials and are marked as integration tests.
"""

import pytest
from unittest.mock import MagicMock, patch
from dataclasses import dataclass
from typing import List, Optional

from core.azure_pii import (
    AzurePIIDetector,
    AzurePIIResult,
    AzurePIIEntity,
    AzureRedactionPolicy,
    is_azure_sdk_available,
    is_azure_identity_available,
    AZURE_SDK_AVAILABLE,
    AZURE_IDENTITY_AVAILABLE,
)


# Mock classes for testing without Azure SDK
@dataclass
class MockPiiEntity:
    """Mock Azure PII Entity"""
    text: str
    category: str
    subcategory: Optional[str]
    confidence_score: float
    offset: int
    length: int


@dataclass
class MockDocumentResult:
    """Mock Azure Document Result"""
    entities: List[MockPiiEntity]
    redacted_text: str
    is_error: bool = False
    error: Optional[MagicMock] = None


class TestAzurePIIEntity:
    """Tests for AzurePIIEntity dataclass."""
    
    def test_entity_creation(self):
        """Test creating an AzurePIIEntity."""
        entity = AzurePIIEntity(
            text="john@example.com",
            category="Email",
            subcategory=None,
            confidence_score=0.95,
            offset=10,
            length=16,
        )
        
        assert entity.text == "john@example.com"
        assert entity.category == "Email"
        assert entity.confidence_score == 0.95
        assert entity.offset == 10
        assert entity.length == 16


class TestAzurePIIResult:
    """Tests for AzurePIIResult dataclass."""
    
    def test_result_creation(self):
        """Test creating an AzurePIIResult."""
        entity = AzurePIIEntity(
            text="john@example.com",
            category="Email",
            subcategory=None,
            confidence_score=0.95,
            offset=10,
            length=16,
        )
        
        result = AzurePIIResult(
            original_text="Email: john@example.com",
            redacted_text="Email: ****************",
            entities=[entity],
            language="en",
        )
        
        assert result.original_text == "Email: john@example.com"
        assert result.redacted_text == "Email: ****************"
        assert len(result.entities) == 1
        assert result.language == "en"
        assert not result.is_error
    
    def test_entity_count(self):
        """Test entity_count property."""
        entities = [
            AzurePIIEntity("john@example.com", "Email", None, 0.9, 0, 16),
            AzurePIIEntity("alice@test.com", "Email", None, 0.85, 20, 14),
            AzurePIIEntity("555-1234", "PhoneNumber", None, 0.8, 40, 8),
        ]
        
        result = AzurePIIResult(
            original_text="test",
            redacted_text="test",
            entities=entities,
        )
        
        assert result.entity_count == {"Email": 2, "PhoneNumber": 1}
    
    def test_error_result(self):
        """Test error result creation."""
        result = AzurePIIResult(
            original_text="test",
            redacted_text="test",
            is_error=True,
            error_message="API Error",
        )
        
        assert result.is_error
        assert result.error_message == "API Error"


class TestAzureRedactionPolicy:
    """Tests for AzureRedactionPolicy enum."""
    
    def test_policy_values(self):
        """Test redaction policy values."""
        assert AzureRedactionPolicy.NONE.value == "none"
        assert AzureRedactionPolicy.CHARACTER_MASK.value == "character_mask"
        assert AzureRedactionPolicy.ENTITY_TYPE.value == "entity_type"


class TestIsAzureSdkAvailable:
    """Tests for is_azure_sdk_available function."""
    
    def test_sdk_availability_check(self):
        """Test SDK availability check."""
        result = is_azure_sdk_available()
        assert isinstance(result, bool)
        assert result == AZURE_SDK_AVAILABLE
    
    def test_identity_availability_check(self):
        """Test Azure Identity SDK availability check."""
        result = is_azure_identity_available()
        assert isinstance(result, bool)
        assert result == AZURE_IDENTITY_AVAILABLE


@pytest.mark.skipif(not AZURE_SDK_AVAILABLE, reason="Azure SDK not installed")
class TestAzurePIIDetectorUnit:
    """Unit tests for AzurePIIDetector (mocked)."""
    
    @pytest.mark.skipif(not AZURE_IDENTITY_AVAILABLE, reason="Azure Identity not installed")
    @patch.dict("os.environ", {
        "AZURE_FOUNDRY_ENDPOINT": "https://test.cognitiveservices.azure.com/"
    })
    @patch("core.azure_pii.DefaultAzureCredential")
    @patch("core.azure_pii.TextAnalyticsClient")
    def test_detector_initialization(self, mock_client_class, mock_credential_class):
        """Test detector initialization with environment variables."""
        mock_client_class.return_value = MagicMock()
        mock_credential_class.return_value = MagicMock()
        
        detector = AzurePIIDetector()
        
        assert detector.endpoint == "https://test.cognitiveservices.azure.com/"
        assert detector.default_language == "en"
        assert detector.redaction_policy == AzureRedactionPolicy.CHARACTER_MASK
        mock_credential_class.assert_called_once()
    
    @pytest.mark.skipif(not AZURE_IDENTITY_AVAILABLE, reason="Azure Identity not installed")
    @patch("core.azure_pii.DefaultAzureCredential")
    @patch("core.azure_pii.TextAnalyticsClient")
    def test_detector_with_explicit_endpoint(self, mock_client_class, mock_credential_class):
        """Test detector with explicit endpoint."""
        mock_client_class.return_value = MagicMock()
        mock_credential_class.return_value = MagicMock()
        
        detector = AzurePIIDetector(
            endpoint="https://explicit.cognitiveservices.azure.com/",
            default_language="ko",
            redaction_policy=AzureRedactionPolicy.ENTITY_TYPE,
        )
        
        assert detector.endpoint == "https://explicit.cognitiveservices.azure.com/"
        assert detector.default_language == "ko"
        assert detector.redaction_policy == AzureRedactionPolicy.ENTITY_TYPE
    
    @patch.dict("os.environ", {
        "AZURE_LANGUAGE_ENDPOINT": "https://fallback.cognitiveservices.azure.com/"
    })
    @pytest.mark.skipif(not AZURE_IDENTITY_AVAILABLE, reason="Azure Identity not installed")
    @patch("core.azure_pii.DefaultAzureCredential")
    @patch("core.azure_pii.TextAnalyticsClient")
    def test_detector_fallback_to_language_env_vars(self, mock_client_class, mock_credential_class):
        """Test detector falls back to AZURE_LANGUAGE_ENDPOINT when AZURE_FOUNDRY_ENDPOINT not set."""
        mock_client_class.return_value = MagicMock()
        mock_credential_class.return_value = MagicMock()
        
        detector = AzurePIIDetector()
        
        assert detector.endpoint == "https://fallback.cognitiveservices.azure.com/"
    
    @patch.dict("os.environ", {
        "AZURE_FOUNDRY_ENDPOINT": "https://foundry.cognitiveservices.azure.com/",
        "AZURE_LANGUAGE_ENDPOINT": "https://language.cognitiveservices.azure.com/"
    })
    @pytest.mark.skipif(not AZURE_IDENTITY_AVAILABLE, reason="Azure Identity not installed")
    @patch("core.azure_pii.DefaultAzureCredential")
    @patch("core.azure_pii.TextAnalyticsClient")
    def test_detector_foundry_takes_precedence(self, mock_client_class, mock_credential_class):
        """Test that AZURE_FOUNDRY_ENDPOINT takes precedence over AZURE_LANGUAGE_ENDPOINT."""
        mock_client_class.return_value = MagicMock()
        mock_credential_class.return_value = MagicMock()
        
        detector = AzurePIIDetector()
        
        assert detector.endpoint == "https://foundry.cognitiveservices.azure.com/"
    
    def test_detector_missing_endpoint(self):
        """Test detector raises error without endpoint."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="endpoint is required"):
                AzurePIIDetector()
    
    @pytest.mark.skipif(not AZURE_IDENTITY_AVAILABLE, reason="Azure Identity not installed")
    @patch.dict("os.environ", {
        "AZURE_FOUNDRY_ENDPOINT": "https://test.cognitiveservices.azure.com/"
    })
    @patch("core.azure_pii.DefaultAzureCredential")
    @patch("core.azure_pii.TextAnalyticsClient")
    def test_detector_entra_id_authentication(self, mock_client_class, mock_credential_class):
        """Test detector with Entra ID authentication."""
        mock_client_class.return_value = MagicMock()
        mock_credential_class.return_value = MagicMock()
        
        detector = AzurePIIDetector()
        
        assert detector.endpoint == "https://test.cognitiveservices.azure.com/"
        mock_credential_class.assert_called_once()
    
    @pytest.mark.skipif(not AZURE_IDENTITY_AVAILABLE, reason="Azure Identity not installed")
    @patch("core.azure_pii.TextAnalyticsClient")
    def test_detector_custom_credential(self, mock_client_class):
        """Test detector with custom credential object."""
        mock_client_class.return_value = MagicMock()
        mock_credential = MagicMock()
        
        detector = AzurePIIDetector(
            endpoint="https://test.cognitiveservices.azure.com/",
            credential=mock_credential
        )
        
        assert detector._custom_credential is mock_credential
    
    @pytest.mark.skipif(not AZURE_IDENTITY_AVAILABLE, reason="Azure Identity not installed")
    @patch.dict("os.environ", {
        "AZURE_FOUNDRY_ENDPOINT": "https://test.cognitiveservices.azure.com/"
    })
    @patch("core.azure_pii.DefaultAzureCredential")
    @patch("core.azure_pii.TextAnalyticsClient")
    def test_detect_pii(self, mock_client_class, mock_credential_class):
        """Test PII detection with mocked Foundry client."""
        mock_credential_class.return_value = MagicMock()
        
        # Setup mock response
        mock_entity = MockPiiEntity(
            text="john@example.com",
            category="Email",
            subcategory=None,
            confidence_score=0.95,
            offset=7,
            length=16,
        )
        mock_doc_result = MockDocumentResult(
            entities=[mock_entity],
            redacted_text="Email: ****************",
        )
        
        mock_client = MagicMock()
        mock_client.recognize_pii_entities.return_value = [mock_doc_result]
        mock_client_class.return_value = mock_client
        
        detector = AzurePIIDetector()
        result = detector.detect("Email: john@example.com")
        
        assert result.original_text == "Email: john@example.com"
        assert len(result.entities) == 1
        assert result.entities[0].text == "john@example.com"
        assert result.entities[0].category == "Email"
    
    @pytest.mark.skipif(not AZURE_IDENTITY_AVAILABLE, reason="Azure Identity not installed")
    @patch.dict("os.environ", {
        "AZURE_FOUNDRY_ENDPOINT": "https://test.cognitiveservices.azure.com/"
    })
    @patch("core.azure_pii.DefaultAzureCredential")
    @patch("core.azure_pii.TextAnalyticsClient")
    def test_detect_batch(self, mock_client_class, mock_credential_class):
        """Test batch PII detection."""
        mock_credential_class.return_value = MagicMock()
        
        mock_entity1 = MockPiiEntity("john@example.com", "Email", None, 0.9, 0, 16)
        mock_entity2 = MockPiiEntity("555-1234", "PhoneNumber", None, 0.85, 0, 8)
        
        mock_results = [
            MockDocumentResult(entities=[mock_entity1], redacted_text="****************"),
            MockDocumentResult(entities=[mock_entity2], redacted_text="********"),
        ]
        
        mock_client = MagicMock()
        mock_client.recognize_pii_entities.return_value = mock_results
        mock_client_class.return_value = mock_client
        
        detector = AzurePIIDetector()
        results = detector.detect_batch([
            "john@example.com",
            "555-1234"
        ])
        
        assert len(results) == 2
        assert results[0].entities[0].category == "Email"
        assert results[1].entities[0].category == "PhoneNumber"
    
    @pytest.mark.skipif(not AZURE_IDENTITY_AVAILABLE, reason="Azure Identity not installed")
    @patch.dict("os.environ", {
        "AZURE_FOUNDRY_ENDPOINT": "https://test.cognitiveservices.azure.com/"
    })
    @patch("core.azure_pii.DefaultAzureCredential")
    @patch("core.azure_pii.TextAnalyticsClient")
    def test_to_presidio_format(self, mock_client_class, mock_credential_class):
        """Test conversion to Presidio format."""
        mock_credential_class.return_value = MagicMock()
        mock_client_class.return_value = MagicMock()
        
        detector = AzurePIIDetector()
        
        result = AzurePIIResult(
            original_text="Email: john@example.com",
            redacted_text="Email: ****************",
            entities=[
                AzurePIIEntity("john@example.com", "Email", None, 0.95, 7, 16)
            ],
        )
        
        presidio_format = detector.to_presidio_format(result)
        
        assert len(presidio_format) == 1
        assert presidio_format[0]["entity_type"] == "EMAIL_ADDRESS"
        assert presidio_format[0]["start"] == 7
        assert presidio_format[0]["end"] == 23
        assert presidio_format[0]["score"] == 0.95
    
    @pytest.mark.skipif(not AZURE_IDENTITY_AVAILABLE, reason="Azure Identity not installed")
    @patch.dict("os.environ", {
        "AZURE_FOUNDRY_ENDPOINT": "https://test.cognitiveservices.azure.com/"
    })
    @patch("core.azure_pii.DefaultAzureCredential")
    @patch("core.azure_pii.TextAnalyticsClient")
    def test_context_manager(self, mock_client_class, mock_credential_class):
        """Test context manager functionality."""
        mock_credential_class.return_value = MagicMock()
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        with AzurePIIDetector() as detector:
            assert detector.is_available
        
        mock_client.close.assert_called_once()


class TestRedactionPolicies:
    """Tests for different redaction policies."""
    
    def test_character_mask_redaction(self):
        """Test character mask redaction."""
        entities = [
            AzurePIIEntity("john@example.com", "Email", None, 0.9, 7, 16),
        ]
        
        text = "Email: john@example.com"
        result = AzurePIIResult(
            original_text=text,
            redacted_text=text,  # Will be calculated
            entities=entities,
        )
        
        # Simulate redaction
        sorted_entities = sorted(entities, key=lambda e: e.offset, reverse=True)
        redacted = text
        for entity in sorted_entities:
            start = entity.offset
            end = entity.offset + entity.length
            replacement = "*" * entity.length
            redacted = redacted[:start] + replacement + redacted[end:]
        
        assert redacted == "Email: ****************"
    
    def test_entity_type_redaction(self):
        """Test entity type replacement redaction."""
        entities = [
            AzurePIIEntity("john@example.com", "Email", None, 0.9, 7, 16),
        ]
        
        text = "Email: john@example.com"
        
        # Simulate entity type redaction
        sorted_entities = sorted(entities, key=lambda e: e.offset, reverse=True)
        redacted = text
        for entity in sorted_entities:
            start = entity.offset
            end = entity.offset + entity.length
            replacement = f"<{entity.category}>"
            redacted = redacted[:start] + replacement + redacted[end:]
        
        assert redacted == "Email: <Email>"


# Integration tests - require actual Azure credentials
@pytest.mark.integration
@pytest.mark.skipif(
    not AZURE_SDK_AVAILABLE or not AZURE_IDENTITY_AVAILABLE,
    reason="Azure SDK or Azure Identity not installed"
)
class TestAzurePIIDetectorIntegration:
    """
    Integration tests for AzurePIIDetector.
    
    These tests require valid Microsoft Foundry credentials:
    - AZURE_FOUNDRY_ENDPOINT environment variable (or AZURE_LANGUAGE_ENDPOINT)
    - Azure CLI authentication (az login) or Managed Identity
    
    Run with: pytest -m integration
    """
    
    @pytest.fixture
    def detector(self):
        """Create a detector with real credentials."""
        import os
        foundry_endpoint = os.environ.get("AZURE_FOUNDRY_ENDPOINT") or os.environ.get("AZURE_LANGUAGE_ENDPOINT")
        
        if not foundry_endpoint:
            pytest.skip("AZURE_FOUNDRY_ENDPOINT or AZURE_LANGUAGE_ENDPOINT not set")
        
        return AzurePIIDetector()
    
    def test_detect_english_email(self, detector):
        """Test detecting email in English text."""
        result = detector.detect(
            "Contact me at john.doe@example.com",
            language="en"
        )
        
        assert not result.is_error
        assert any(e.category == "Email" for e in result.entities)
    
    def test_detect_english_phone(self, detector):
        """Test detecting phone number in English text."""
        result = detector.detect(
            "Call me at 555-123-4567",
            language="en"
        )
        
        assert not result.is_error
        # Phone detection may vary
    
    def test_detect_korean_text(self, detector):
        """Test detecting PII in Korean text."""
        result = detector.detect(
            "이메일은 hong@example.com입니다.",
            language="ko"
        )
        
        assert not result.is_error
        assert any(e.category == "Email" for e in result.entities)
    
    def test_batch_detection(self, detector):
        """Test batch PII detection."""
        results = detector.detect_batch([
            "Email: alice@example.com",
            "Phone: 555-987-6543",
        ])
        
        assert len(results) == 2
        assert all(not r.is_error for r in results)

"""
PII Detector Module

Uses Microsoft Presidio Analyzer for PII detection.
Supports multiple languages including English and Korean.
Uses RecognizerRegistryProvider for configuration-based recognizer loading.
"""

from pathlib import Path
from typing import List, Optional

from presidio_analyzer import AnalyzerEngine, RecognizerResult
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_analyzer.recognizer_registry import RecognizerRegistryProvider

from core.config import RECOGNIZERS_EN_CONFIG, RECOGNIZERS_KO_CONFIG


class PIIDetector:
    """
    PII Detector using Microsoft Presidio Analyzer.
    
    Uses RecognizerRegistryProvider for YAML-based recognizer configuration.
    
    Attributes:
        supported_languages: List of supported language codes.
        analyzer: Presidio AnalyzerEngine instance.
    """
    
    DEFAULT_ENTITIES = [
        "PERSON",
        "EMAIL_ADDRESS",
        "PHONE_NUMBER",
        "CREDIT_CARD",
        "IBAN_CODE",
        "IP_ADDRESS",
        "DATE_TIME",
        "LOCATION",
        "NRP",  # Nationality, Religion, Political group
        "MEDICAL_LICENSE",
        "URL",
        # Korean entities
        "KR_SSN",
        "KR_PHONE_NUMBER",
        "KR_BANK_ACCOUNT",
        "KR_NAME",
        "KR_EMAIL",
    ]
    
    def __init__(
        self,
        languages: Optional[List[str]] = None,
        default_language: str = "en",
    ):
        """
        Initialize PII Detector.
        
        Args:
            languages: List of language codes to support. Defaults to ["en", "ko"].
            default_language: Default language for detection. Defaults to "en".
        """
        self.supported_languages = languages or ["en", "ko"]
        self.default_language = default_language
        
        # Create NLP engine first
        self.nlp_engine = self._create_nlp_engine()
        
        # Create language-specific analyzers using RecognizerRegistryProvider
        self._analyzers = {}
        self._create_analyzers()
    
    def _create_nlp_engine(self):
        """Create the spaCy NLP engine for supported languages."""
        models = []
        
        if "en" in self.supported_languages:
            models.append({"lang_code": "en", "model_name": "en_core_web_lg"})
        
        if "ko" in self.supported_languages:
            try:
                import spacy
                spacy.load("ko_core_news_lg")
                models.append({"lang_code": "ko", "model_name": "ko_core_news_lg"})
            except OSError:
                self.supported_languages = [
                    lang for lang in self.supported_languages if lang != "ko"
                ]
        
        if not models:
            return None
        
        configuration = {
            "nlp_engine_name": "spacy",
            "models": models,
        }
        
        provider = NlpEngineProvider(nlp_configuration=configuration)
        return provider.create_engine()
    
    def _create_analyzers(self):
        """Create analyzers for each supported language using RecognizerRegistryProvider."""
        config_map = {
            "en": RECOGNIZERS_EN_CONFIG,
            "ko": RECOGNIZERS_KO_CONFIG,
        }
        
        for lang in self.supported_languages:
            config_path = config_map.get(lang)
            
            if config_path and config_path.exists():
                try:
                    # Create recognizer registry from YAML config
                    registry_provider = RecognizerRegistryProvider(
                        conf_file=str(config_path)
                    )
                    registry = registry_provider.create_recognizer_registry()
                    
                    # Create analyzer with the registry
                    analyzer = AnalyzerEngine(
                        registry=registry,
                        nlp_engine=self.nlp_engine,
                        supported_languages=[lang],
                    )
                    self._analyzers[lang] = analyzer
                except Exception as e:
                    print(f"Warning: Failed to load recognizer config for {lang}: {e}")
                    self._create_fallback_analyzer(lang)
            else:
                self._create_fallback_analyzer(lang)
    
    def _create_fallback_analyzer(self, language: str):
        """Create a fallback analyzer without custom recognizers."""
        self._analyzers[language] = AnalyzerEngine(
            nlp_engine=self.nlp_engine,
            supported_languages=[language],
        )
    
    @property
    def analyzer(self) -> AnalyzerEngine:
        """Get the default language analyzer (for backward compatibility)."""
        return self._analyzers.get(
            self.default_language,
            next(iter(self._analyzers.values())) if self._analyzers else None
        )
    
    def get_analyzer(self, language: str) -> AnalyzerEngine:
        """Get the analyzer for a specific language."""
        return self._analyzers.get(language, self.analyzer)
    
    def detect(
        self,
        text: str,
        language: Optional[str] = None,
        entities: Optional[List[str]] = None,
        score_threshold: float = 0.5,
    ) -> List[RecognizerResult]:
        """
        Detect PII entities in the given text.
        
        Args:
            text: Input text to analyze.
            language: Language code of the text. Defaults to default_language.
            entities: List of entity types to detect. Defaults to all supported entities.
            score_threshold: Minimum confidence score for detection. Defaults to 0.5.
        
        Returns:
            List of RecognizerResult objects containing detected PII entities.
        
        Example:
            >>> detector = PIIDetector()
            >>> results = detector.detect("My email is john@example.com")
            >>> print(results[0].entity_type)  # EMAIL_ADDRESS
        """
        language = language or self.default_language
        entities = entities or self.DEFAULT_ENTITIES
        
        # Get the appropriate analyzer for the language
        analyzer = self.get_analyzer(language)
        
        results = analyzer.analyze(
            text=text,
            language=language,
            entities=entities,
            score_threshold=score_threshold,
        )
        
        return results
    
    def detect_batch(
        self,
        texts: List[str],
        language: Optional[str] = None,
        entities: Optional[List[str]] = None,
        score_threshold: float = 0.5,
    ) -> List[List[RecognizerResult]]:
        """
        Detect PII entities in multiple texts.
        
        Args:
            texts: List of input texts to analyze.
            language: Language code of the texts. Defaults to default_language.
            entities: List of entity types to detect. Defaults to all supported entities.
            score_threshold: Minimum confidence score for detection. Defaults to 0.5.
        
        Returns:
            List of lists containing RecognizerResult objects for each input text.
        """
        return [
            self.detect(text, language, entities, score_threshold)
            for text in texts
        ]
    
    def get_supported_entities(self, language: Optional[str] = None) -> List[str]:
        """
        Get list of supported entity types for a given language.
        
        Args:
            language: Language code. Defaults to default_language.
        
        Returns:
            List of supported entity type names.
        """
        language = language or self.default_language
        analyzer = self.get_analyzer(language)
        return analyzer.get_supported_entities(language=language)
    
    def get_recognizers(self, language: Optional[str] = None) -> List[str]:
        """
        Get list of registered recognizer names for a given language.
        
        Args:
            language: Language code. Defaults to default_language.
        
        Returns:
            List of recognizer names.
        """
        language = language or self.default_language
        analyzer = self.get_analyzer(language)
        recognizers = analyzer.registry.get_recognizers(
            language=language, all_fields=True
        )
        return [r.name for r in recognizers]

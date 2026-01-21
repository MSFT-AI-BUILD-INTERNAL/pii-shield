"""
PII Detector Module

Uses Microsoft Presidio Analyzer for PII detection.
Supports multiple languages including English and Korean.
"""

from typing import List, Optional

from presidio_analyzer import AnalyzerEngine, RecognizerResult
from presidio_analyzer.nlp_engine import NlpEngineProvider


class PIIDetector:
    """
    PII Detector using Microsoft Presidio Analyzer.
    
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
        self.analyzer = self._create_analyzer()
    
    def _create_analyzer(self) -> AnalyzerEngine:
        """
        Create and configure the Presidio Analyzer Engine.
        
        Returns:
            Configured AnalyzerEngine instance.
        """
        # Try to use spacy models, fallback to basic analyzer if not available
        try:
            # Configure NLP engine for supported languages
            configuration = {
                "nlp_engine_name": "spacy",
                "models": [
                    {"lang_code": "en", "model_name": "en_core_web_sm"},
                ],
            }
            
            # Add Korean model if supported
            if "ko" in self.supported_languages:
                try:
                    import spacy
                    spacy.load("ko_core_news_sm")
                    configuration["models"].append(
                        {"lang_code": "ko", "model_name": "ko_core_news_sm"}
                    )
                except OSError:
                    # Korean model not available, remove from supported languages
                    self.supported_languages = [
                        lang for lang in self.supported_languages if lang != "ko"
                    ]
            
            provider = NlpEngineProvider(nlp_configuration=configuration)
            nlp_engine = provider.create_engine()
            
            analyzer = AnalyzerEngine(
                nlp_engine=nlp_engine,
                supported_languages=self.supported_languages,
            )
        except OSError:
            # Fallback: create analyzer without NLP engine (pattern-based only)
            self.supported_languages = ["en"]
            analyzer = AnalyzerEngine(
                supported_languages=self.supported_languages,
            )
        
        return analyzer
    
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
        
        results = self.analyzer.analyze(
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
        return self.analyzer.get_supported_entities(language=language)

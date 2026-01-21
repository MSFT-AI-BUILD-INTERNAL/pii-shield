"""
Custom Recognizer Example for PII Shield.

Demonstrates how to create and register custom PII recognizers.
"""

from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer
from presidio_analyzer.nlp_engine import NlpEngineProvider

from core import PIIShield, PIIDetector


class EmployeeIDRecognizer(PatternRecognizer):
    """
    Custom recognizer for Employee IDs.
    
    Detects employee IDs in the format: EMP-XXXX-XXXX
    """
    
    PATTERNS = [
        Pattern(
            "Employee ID",
            r"\bEMP[-]\d{4}[-]\d{4}\b",
            0.9,
        ),
    ]
    
    CONTEXT = ["employee", "emp", "id", "staff"]
    
    def __init__(self):
        super().__init__(
            supported_entity="EMPLOYEE_ID",
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language="en",
        )


class CustomProductCodeRecognizer(PatternRecognizer):
    """
    Custom recognizer for Product Codes.
    
    Detects product codes in the format: PROD-ABC-12345
    """
    
    PATTERNS = [
        Pattern(
            "Product Code",
            r"\bPROD[-][A-Z]{3}[-]\d{5}\b",
            0.85,
        ),
    ]
    
    CONTEXT = ["product", "code", "item", "sku"]
    
    def __init__(self):
        super().__init__(
            supported_entity="PRODUCT_CODE",
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language="en",
        )


def create_custom_detector() -> PIIDetector:
    """
    Create a PIIDetector with custom recognizers.
    
    Returns:
        PIIDetector instance with custom recognizers registered.
    """
    # Create base detector
    detector = PIIDetector(languages=["en"])
    
    # Register custom recognizers
    detector.analyzer.registry.add_recognizer(EmployeeIDRecognizer())
    detector.analyzer.registry.add_recognizer(CustomProductCodeRecognizer())
    
    return detector


def example_custom_recognizers():
    """
    Example: Using custom recognizers.
    """
    print("=" * 60)
    print("Custom Recognizer Example")
    print("=" * 60)
    
    # Create detector with custom recognizers
    detector = create_custom_detector()
    
    # Sample text with custom entities
    text = """
    Employee EMP-1234-5678 ordered product PROD-ABC-12345.
    Contact: john@example.com
    """
    
    # Detect all entities including custom ones
    results = detector.detect(text)
    
    print(f"Text: {text.strip()}")
    print(f"\nDetected {len(results)} entities:")
    
    for result in results:
        entity_text = text[result.start:result.end]
        print(f"  • {result.entity_type}: '{entity_text}' (score: {result.score:.2f})")
    
    # Show supported entities
    print("\nSupported entities:")
    entities = detector.get_supported_entities()
    for entity in sorted(entities):
        print(f"  - {entity}")


def example_regex_recognizer():
    """
    Example: Creating a simple regex-based recognizer.
    """
    print("\n" + "=" * 60)
    print("Simple Regex Recognizer Example")
    print("=" * 60)
    
    # Create a recognizer for internal reference numbers
    internal_ref_recognizer = PatternRecognizer(
        supported_entity="INTERNAL_REF",
        patterns=[
            Pattern(
                "Internal Reference",
                r"\bREF[-]?\d{8}\b",
                0.8,
            ),
        ],
        context=["reference", "ref", "number"],
        supported_language="en",
    )
    
    # Create detector and register
    detector = PIIDetector(languages=["en"])
    detector.analyzer.registry.add_recognizer(internal_ref_recognizer)
    
    # Test
    text = "Please refer to REF-12345678 for more details."
    results = detector.detect(text, entities=["INTERNAL_REF"])
    
    print(f"Text: {text}")
    print(f"\nDetected entities:")
    for result in results:
        entity_text = text[result.start:result.end]
        print(f"  • {result.entity_type}: '{entity_text}'")


def main():
    """Run examples."""
    print("\n🔧 Custom Recognizer Examples\n")
    
    try:
        example_custom_recognizers()
        example_regex_recognizer()
        
    except ImportError as e:
        print(f"Import Error: {e}")
        print("Make sure to install required packages first.")


if __name__ == "__main__":
    main()

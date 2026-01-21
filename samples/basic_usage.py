"""
Basic Usage Examples for PII Shield.

This file demonstrates how to use the core PII Shield functionality.
"""

from core import PIIShield, PIIDetector, PIIMasker
from core.masker import MaskingStrategy


def example_basic_protection():
    """
    Basic example: Detect and mask PII in a single step.
    """
    print("=" * 60)
    print("Example 1: Basic PII Protection")
    print("=" * 60)
    
    # Initialize PII Shield
    shield = PIIShield()
    
    # Sample text with PII
    text = "Contact John Doe at john.doe@example.com or call 555-123-4567."
    
    # Protect the text (detect and mask)
    result = shield.protect(text)
    
    print(f"Original: {result.original_text}")
    print(f"Masked:   {result.masked_text}")
    print(f"Detected: {result.entity_count}")
    print()


def example_detection_only():
    """
    Example: Detect PII without masking.
    """
    print("=" * 60)
    print("Example 2: Detection Only")
    print("=" * 60)
    
    shield = PIIShield()
    
    text = "My credit card number is 4111-1111-1111-1111 and SSN is 123-45-6789."
    
    # Detect only
    entities = shield.detect_only(text)
    
    print(f"Text: {text}")
    print(f"\nDetected {len(entities)} PII entities:")
    for entity in entities:
        pii_text = text[entity.start:entity.end]
        print(f"  • {entity.entity_type}: '{pii_text}' (score: {entity.score:.2f})")
    print()


def example_different_strategies():
    """
    Example: Using different masking strategies.
    """
    print("=" * 60)
    print("Example 3: Different Masking Strategies")
    print("=" * 60)
    
    text = "Email: alice@company.com, Phone: 555-987-6543"
    
    strategies = [
        MaskingStrategy.REPLACE,
        MaskingStrategy.REDACT,
        MaskingStrategy.HASH,
        MaskingStrategy.MASK,
    ]
    
    print(f"Original: {text}\n")
    
    for strategy in strategies:
        shield = PIIShield(default_strategy=strategy)
        result = shield.protect(text)
        print(f"{strategy.value.upper():10} → {result.masked_text}")
    print()


def example_korean_text():
    """
    Example: Processing Korean text.
    """
    print("=" * 60)
    print("Example 4: Korean Language Support")
    print("=" * 60)
    
    shield = PIIShield(languages=["en", "ko"], default_language="ko")
    
    text = "김철수님의 이메일은 chulsoo.kim@example.com입니다."
    
    result = shield.protect(text, language="ko")
    
    print(f"Original: {result.original_text}")
    print(f"Masked:   {result.masked_text}")
    print(f"Detected: {result.entity_count}")
    print()


def example_batch_processing():
    """
    Example: Processing multiple texts at once.
    """
    print("=" * 60)
    print("Example 5: Batch Processing")
    print("=" * 60)
    
    shield = PIIShield()
    
    texts = [
        "Contact: john@example.com",
        "Call us at 555-111-2222",
        "Visit our website at https://example.com",
    ]
    
    results = shield.protect_batch(texts)
    
    for i, result in enumerate(results, 1):
        print(f"Text {i}:")
        print(f"  Original: {result.original_text}")
        print(f"  Masked:   {result.masked_text}")
    print()


def example_custom_entities():
    """
    Example: Detecting specific entity types only.
    """
    print("=" * 60)
    print("Example 6: Custom Entity Types")
    print("=" * 60)
    
    shield = PIIShield()
    
    text = "Contact John at john@example.com or visit https://example.com"
    
    # Only detect EMAIL_ADDRESS
    result = shield.protect(
        text,
        entities=["EMAIL_ADDRESS"],
    )
    
    print(f"Original: {result.original_text}")
    print(f"Masked (email only): {result.masked_text}")
    print(f"Detected: {result.entity_count}")
    print()


def example_json_output():
    """
    Example: Converting results to JSON format.
    """
    print("=" * 60)
    print("Example 7: JSON Output")
    print("=" * 60)
    
    import json
    
    shield = PIIShield()
    text = "Send to alice@example.com"
    
    result = shield.protect(text)
    json_output = shield.to_dict(result)
    
    print(json.dumps(json_output, indent=2))
    print()


def main():
    """Run all examples."""
    print("\n🛡️  PII Shield - Usage Examples\n")
    
    try:
        example_basic_protection()
        example_detection_only()
        example_different_strategies()
        # example_korean_text()  # Requires Korean model
        example_batch_processing()
        example_custom_entities()
        example_json_output()
        
    except ImportError as e:
        print(f"Import Error: {e}")
        print("Make sure to install required packages:")
        print("  pip install presidio-analyzer presidio-anonymizer spacy")
        print("  python -m spacy download en_core_web_lg")


if __name__ == "__main__":
    main()

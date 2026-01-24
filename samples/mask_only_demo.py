#!/usr/bin/env python3
"""
Demonstration of mask-based PII detection without labels.

This example shows how PIIShield now masks PII with '*' characters
instead of entity type labels like <PERSON>, <EMAIL>, etc.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import PIIShield, MaskingStrategy


def demo_mask_only():
    """Demonstrate masking without labels."""
    print("=" * 80)
    print("MASK-ONLY PII MASKING DEMONSTRATION")
    print("=" * 80)
    print("\nPII is now masked with '*' characters only (no entity type labels)")
    print()
    
    shield = PIIShield()
    
    # English examples
    print("-" * 80)
    print("English Examples:")
    print("-" * 80)
    
    en_examples = [
        "Contact John Doe at john.doe@example.com or call 555-123-4567.",
        "My credit card number is 4111-1111-1111-1111.",
        "Visit https://example.com for more information.",
    ]
    
    for text in en_examples:
        result = shield.protect(text, language="en", strategy=MaskingStrategy.MASK)
        print(f"\nOriginal: {text}")
        print(f"Masked:   {result.masked_text}")
        print(f"Entities: {', '.join(f'{k}={v}' for k, v in result.entity_count.items())}")
    
    # Korean examples
    print("\n" + "-" * 80)
    print("Korean Examples:")
    print("-" * 80)
    
    ko_examples = [
        "안녕하세요, 김철수입니다. 연락처는 010-1234-5678입니다.",
        "홍길동님의 이메일은 hong@example.com입니다.",
        "세종대왕님 주민등록번호 800520-1234567 등록 완료.",
    ]
    
    for text in ko_examples:
        result = shield.protect(text, language="ko", strategy=MaskingStrategy.MASK)
        print(f"\nOriginal: {text}")
        print(f"Masked:   {result.masked_text}")
        print(f"Entities: {', '.join(f'{k}={v}' for k, v in result.entity_count.items())}")
    
    print("\n" + "=" * 80)


def compare_strategies():
    """Compare different masking strategies."""
    print("\n" + "=" * 80)
    print("MASKING STRATEGY COMPARISON")
    print("=" * 80)
    
    shield = PIIShield()
    text = "Contact John Doe at john.doe@example.com or call 555-123-4567."
    
    print(f"\nOriginal text:")
    print(f"  {text}")
    
    strategies = [
        (MaskingStrategy.MASK, "MASK (asterisks only)"),
        (MaskingStrategy.REPLACE, "REPLACE (with labels)"),
        (MaskingStrategy.REDACT, "REDACT (remove completely)"),
    ]
    
    for strategy, description in strategies:
        result = shield.protect(text, language="en", strategy=strategy)
        print(f"\n{description}:")
        print(f"  {result.masked_text}")
    
    print("\n" + "=" * 80)


def main():
    """Run all demonstrations."""
    demo_mask_only()
    compare_strategies()
    
    print("\n✅ Demonstration complete!")
    print("\nKey Changes:")
    print("  • MASK strategy now uses '*' only (no entity type labels)")
    print("  • Validation is based on masked text comparison")
    print("  • Detection accuracy remains the same")
    print("  • All entity information is still available in result.entity_count")
    print()


if __name__ == "__main__":
    main()

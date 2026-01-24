#!/usr/bin/env python3
"""
Demonstration of strict merge rule in dual detection mode.

This example shows how PIIShield merges results from Azure and Presidio
when both detectors find overlapping entities. The strict rule ensures
maximum PII coverage by selecting the wider entity.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import PIIShield, MaskingStrategy


def demo_korean_partial_detection():
    """Demonstrate Korean name detection with partial vs full coverage."""
    print("=" * 80)
    print("Example 1: Korean Name - Partial vs Full Detection")
    print("=" * 80)
    
    text = "세종대왕은 조선의 위대한 왕입니다."
    print(f"\nOriginal text:\n  {text}")
    print("\nScenario:")
    print("  - Azure might detect: '세종' (partial)")
    print("  - Presidio might detect: '세종대왕' (full name)")
    print("  - Strict merge rule: Choose the wider one → '세종대왕'")
    
    shield = PIIShield()
    result = shield.protect(
        text=text,
        strategy=MaskingStrategy.REDACT,
    )
    
    print(f"\nMasked text:\n  {result.masked_text}")
    print(f"\nDetected entities: {len(result.detected_entities)}")
    for entity in result.detected_entities:
        original = text[entity.start:entity.end]
        print(f"  - {entity.entity_type} at {entity.start}-{entity.end}: '{original}'")
    print()


def demo_email_with_name():
    """Demonstrate email detection where name is part of email."""
    print("=" * 80)
    print("Example 2: Email with Name - Different Coverage")
    print("=" * 80)
    
    text = "Please contact john@example.com for more information."
    print(f"\nOriginal text:\n  {text}")
    print("\nScenario:")
    print("  - Azure might detect: 'john' as PERSON (partial)")
    print("  - Presidio might detect: 'john@example.com' as EMAIL (full)")
    print("  - Strict merge rule: Choose the wider one → 'john@example.com'")
    
    shield = PIIShield()
    result = shield.protect(
        text=text,
        strategy=MaskingStrategy.REDACT,
    )
    
    print(f"\nMasked text:\n  {result.masked_text}")
    print(f"\nDetected entities: {len(result.detected_entities)}")
    for entity in result.detected_entities:
        original = text[entity.start:entity.end]
        print(f"  - {entity.entity_type} at {entity.start}-{entity.end}: '{original}'")
    print()


def demo_multiple_non_overlapping():
    """Demonstrate multiple non-overlapping entities."""
    print("=" * 80)
    print("Example 3: Multiple Non-Overlapping Entities")
    print("=" * 80)
    
    text = "Contact Alice Johnson at alice.johnson@example.com for details."
    print(f"\nOriginal text:\n  {text}")
    print("\nScenario:")
    print("  - Azure detects: 'Alice' + 'alice.johnson@example.com'")
    print("  - Presidio detects: 'Alice Johnson' + 'alice.johnson@example.com'")
    print("  - Strict merge rule:")
    print("    * 'Alice' vs 'Alice Johnson' → Choose 'Alice Johnson' (wider)")
    print("    * Email is same in both → Keep one")
    
    shield = PIIShield()
    result = shield.protect(
        text=text,
        strategy=MaskingStrategy.MASK,
    )
    
    print(f"\nMasked text:\n  {result.masked_text}")
    print(f"\nDetected entities: {len(result.detected_entities)}")
    for entity in result.detected_entities:
        original = text[entity.start:entity.end]
        print(f"  - {entity.entity_type} at {entity.start}-{entity.end}: '{original}'")
    print()


def demo_comparison_mode():
    """Compare Azure-only, Presidio-only, and dual detection modes."""
    print("=" * 80)
    print("Example 4: Mode Comparison - Azure vs Presidio vs Dual")
    print("=" * 80)
    
    text = "세종대왕은 한글을 창제했습니다. Contact john@example.com for details."
    print(f"\nOriginal text:\n  {text}")
    
    # Azure only mode (if endpoint is configured)
    try:
        shield_azure = PIIShield(azure_only=True)
        result_azure = shield_azure.protect(
            text=text,
            strategy=MaskingStrategy.REDACT,
        )
        print(f"\nAzure-only mode:")
        print(f"  Masked: {result_azure.masked_text}")
        print(f"  Entities: {len(result_azure.detected_entities)}")
        for entity in result_azure.detected_entities:
            original = text[entity.start:entity.end]
            print(f"    - {entity.entity_type}: '{original}'")
    except Exception as e:
        print(f"\nAzure-only mode: Not available ({str(e)[:50]}...)")
    
    # Presidio only mode
    shield_presidio = PIIShield(use_azure=False)
    result_presidio = shield_presidio.protect(
        text=text,
        strategy=MaskingStrategy.REDACT,
    )
    print(f"\nPresidio-only mode:")
    print(f"  Masked: {result_presidio.masked_text}")
    print(f"  Entities: {len(result_presidio.detected_entities)}")
    for entity in result_presidio.detected_entities:
        original = text[entity.start:entity.end]
        print(f"    - {entity.entity_type}: '{original}'")
    
    # Dual detection mode (default)
    shield_dual = PIIShield()
    result_dual = shield_dual.protect(
        text=text,
        strategy=MaskingStrategy.REDACT,
    )
    print(f"\nDual detection mode (default):")
    print(f"  Masked: {result_dual.masked_text}")
    print(f"  Entities: {len(result_dual.detected_entities)}")
    for entity in result_dual.detected_entities:
        original = text[entity.start:entity.end]
        print(f"    - {entity.entity_type}: '{original}'")
    
    print("\nKey takeaway:")
    print("  Dual detection mode provides maximum PII coverage by combining")
    print("  results from both Azure and Presidio, using strict merge rules")
    print("  to select the widest entity when overlaps occur.")
    print()


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 80)
    print("STRICT MERGE RULE DEMONSTRATION")
    print("=" * 80)
    print("\nThis demo shows how PIIShield's strict merge rule works")
    print("when combining results from Azure and Presidio detectors.")
    print("Rule: When entities overlap, always choose the wider coverage.")
    print()
    
    demo_korean_partial_detection()
    demo_email_with_name()
    demo_multiple_non_overlapping()
    demo_comparison_mode()
    
    print("=" * 80)
    print("Demo complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()

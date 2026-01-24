"""
Dual Detection Strategy Example

Demonstrates the new dual detection strategy where both Azure and Presidio
are used simultaneously to maximize PII detection coverage.
"""

import os
from core import PIIShield


def main():
    """
    Demonstrate dual detection strategy.
    """
    print("=" * 70)
    print("Dual Detection Strategy Demo")
    print("=" * 70)
    print()
    
    # Check configuration
    endpoint = os.environ.get("AZURE_FOUNDRY_ENDPOINT")
    if not endpoint:
        print("⚠️  AZURE_FOUNDRY_ENDPOINT not set")
        print("   This demo requires Azure endpoint to show dual detection")
        print("   Set it with:")
        print("   export AZURE_FOUNDRY_ENDPOINT=https://your-resource.cognitiveservices.azure.com/")
        return
    
    print(f"✅ Azure endpoint: {endpoint}")
    print()
    
    # Test texts
    test_cases = [
        ("Email and phone", "Contact me at john@example.com or call 555-123-4567"),
        ("Person name", "Alice Johnson works at Microsoft"),
        ("Credit card", "Card number: 4111-1111-1111-1111"),
        ("Mixed Korean", "김철수님 이메일: chulsoo@example.com"),
    ]
    
    print("Comparing Detection Modes:")
    print("=" * 70)
    print()
    
    for title, text in test_cases:
        print(f"📝 {title}")
        print(f"   Original: {text}")
        print()
        
        # Mode 1: Presidio only
        shield_presidio = PIIShield(use_azure=False)
        result_presidio = shield_presidio.protect(text)
        
        print(f"   Presidio only:")
        print(f"     Masked: {result_presidio.masked_text}")
        print(f"     Entities: {result_presidio.entity_count}")
        print(f"     Total: {len(result_presidio.detected_entities)}")
        
        # Mode 2: Azure only
        shield_azure = PIIShield(azure_only=True)
        result_azure = shield_azure.protect(text)
        
        print(f"   Azure only:")
        print(f"     Masked: {result_azure.masked_text}")
        print(f"     Entities: {result_azure.entity_count}")
        print(f"     Total: {len(result_azure.detected_entities)}")
        
        # Mode 3: Dual (both)
        shield_dual = PIIShield()
        result_dual = shield_dual.protect(text)
        
        print(f"   Dual (Azure + Presidio):")
        print(f"     Masked: {result_dual.masked_text}")
        print(f"     Entities: {result_dual.entity_count}")
        print(f"     Total: {len(result_dual.detected_entities)}")
        
        # Analysis
        presidio_count = len(result_presidio.detected_entities)
        azure_count = len(result_azure.detected_entities)
        dual_count = len(result_dual.detected_entities)
        
        print(f"   Analysis:")
        if dual_count >= max(presidio_count, azure_count):
            print(f"     ✅ Dual mode found most entities ({dual_count})")
        if dual_count > presidio_count:
            print(f"     📈 +{dual_count - presidio_count} more than Presidio alone")
        if dual_count > azure_count:
            print(f"     📈 +{dual_count - azure_count} more than Azure alone")
        
        print()
        print("-" * 70)
        print()


def show_merge_example():
    """
    Show how entities are merged from both detectors.
    """
    print("\n" + "=" * 70)
    print("Entity Merging Example")
    print("=" * 70)
    print()
    
    text = "Email john@example.com to John Smith at 555-1234"
    
    shield = PIIShield()
    result = shield.detect_only(text)
    
    print(f"Text: {text}")
    print(f"\nDetected {len(result)} entities:")
    
    for i, entity in enumerate(result, 1):
        entity_text = text[entity.start:entity.end]
        print(f"  {i}. {entity.entity_type}")
        print(f"     Text: '{entity_text}'")
        print(f"     Position: {entity.start}-{entity.end}")
        print(f"     Confidence: {entity.score:.2f}")
    
    print("\n✨ These entities come from BOTH Azure and Presidio")
    print("   Duplicates are automatically removed based on overlap")


if __name__ == "__main__":
    main()
    
    # Uncomment to see entity merging details
    # show_merge_example()

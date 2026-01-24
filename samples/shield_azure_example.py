"""
PIIShield with Azure Integration Example

Demonstrates how PIIShield automatically uses Azure Language Service
when AZURE_FOUNDRY_ENDPOINT is configured, with Presidio as fallback.
"""

import os
from core import PIIShield, MaskingStrategy


def main():
    """
    Example showing automatic Azure/Presidio integration.
    """
    print("=== PIIShield with Azure Integration ===")
    print()
    
    # Check if Azure is configured
    azure_endpoint = os.environ.get("AZURE_FOUNDRY_ENDPOINT") or os.environ.get("AZURE_LANGUAGE_ENDPOINT")
    
    if azure_endpoint:
        print(f"✅ Azure endpoint configured: {azure_endpoint}")
        print("   PIIShield will use Azure Language Service (cloud)")
        print("   Presidio will be used as fallback if Azure fails")
    else:
        print("ℹ️  No Azure endpoint configured")
        print("   PIIShield will use Presidio (local) only")
    
    print()
    print("-" * 60)
    print()
    
    # Initialize PIIShield (auto-detects Azure availability)
    shield = PIIShield()
    
    # Test texts
    texts = [
        "My email is john.doe@example.com and phone is 555-123-4567.",
        "저는 홍길동이고, 이메일은 hong@example.com입니다.",
        "Credit card: 4111-1111-1111-1111, SSN: 123-45-6789",
    ]
    
    languages = ["en", "ko", "en"]
    
    for i, (text, lang) in enumerate(zip(texts, languages), 1):
        print(f"Example {i} ({lang}):")
        print(f"Original: {text}")
        
        # Protect the text
        result = shield.protect(text, language=lang)
        
        print(f"Masked:   {result.masked_text}")
        print(f"Entities: {result.entity_count}")
        print()
    
    print("-" * 60)
    print()
    
    # Test detect_only (without masking)
    print("Detection Only (no masking):")
    text = "Contact Alice at alice@company.com or call 555-9876"
    entities = shield.detect_only(text, language="en")
    
    print(f"Text: {text}")
    print(f"Found {len(entities)} entities:")
    for entity in entities:
        print(f"  - {entity.entity_type}: position {entity.start}-{entity.end} (score: {entity.score:.2f})")
    
    print()
    print("=== Complete ===")


def test_explicit_modes():
    """
    Test explicit Azure enable/disable.
    """
    print("\n=== Testing Explicit Modes ===\n")
    
    # Force Presidio only (even if Azure is available)
    print("1. Force Presidio only (use_azure=False):")
    shield_local = PIIShield(use_azure=False)
    result = shield_local.protect("Email: test@example.com")
    print(f"   Masked: {result.masked_text}")
    print()
    
    # Auto-detect (default behavior)
    print("2. Auto-detect (use_azure=None, default):")
    shield_auto = PIIShield()
    result = shield_auto.protect("Email: test@example.com")
    print(f"   Masked: {result.masked_text}")
    print()


if __name__ == "__main__":
    main()
    
    # Uncomment to test explicit modes
    # test_explicit_modes()

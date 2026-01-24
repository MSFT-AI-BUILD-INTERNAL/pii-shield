"""
Azure-Only Mode Example

Demonstrates using PIIShield with Azure Language Service only,
without Presidio fallback.
"""

import os
from core import PIIShield


def main():
    """
    Example using Azure-only mode (no Presidio fallback).
    """
    print("=== PIIShield - Azure Only Mode ===")
    print()
    
    # Check Azure configuration
    endpoint = os.environ.get("AZURE_FOUNDRY_ENDPOINT")
    if not endpoint:
        print("❌ AZURE_FOUNDRY_ENDPOINT is not set")
        print("   azure_only mode requires this environment variable")
        print()
        print("   Set it with:")
        print("   export AZURE_FOUNDRY_ENDPOINT=https://your-resource.cognitiveservices.azure.com/")
        return
    
    print(f"✅ Azure endpoint: {endpoint}")
    print()
    
    try:
        # Initialize with azure_only=True
        # This will NOT initialize Presidio detector
        shield = PIIShield(azure_only=True)
        
        print(f"Configuration:")
        print(f"  - Using Azure: {shield.use_azure}")
        print(f"  - Azure Only: {shield.azure_only}")
        print(f"  - Presidio Detector: {shield.detector}")
        print(f"  - Azure Detector: {shield.azure_detector is not None}")
        print()
        
        # Test texts
        texts = [
            ("My email is john@example.com", "en"),
            ("Credit card: 4111-1111-1111-1111", "en"),
            ("저는 홍길동이고 이메일은 hong@example.com입니다", "ko"),
        ]
        
        print("PII Detection Results:")
        print("-" * 60)
        
        for text, lang in texts:
            result = shield.protect(text, language=lang)
            print(f"[{lang}] Original: {text}")
            print(f"     Masked:   {result.masked_text}")
            print(f"     Entities: {result.entity_count}")
            print()
        
        print("=" * 60)
        print("✅ Azure-only mode working successfully!")
        print()
        print("Benefits:")
        print("  - Uses latest cloud AI models")
        print("  - Higher accuracy than local Presidio")
        print("  - No local model dependencies")
        print()
        print("Note:")
        print("  - Requires internet connection")
        print("  - No fallback if Azure fails")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Common issues:")
        print("  1. Azure endpoint not set or invalid")
        print("  2. Azure SDK not installed (pip install pii-shield[azure])")
        print("  3. Not authenticated (run 'az login')")
        print("  4. Missing permissions on Azure resource")


def compare_modes():
    """
    Compare azure_only vs normal mode.
    """
    print("\n=== Mode Comparison ===\n")
    
    text = "Email: test@example.com"
    
    # Normal mode (with fallback)
    print("1. Normal Mode (Azure + Presidio fallback):")
    shield_normal = PIIShield()
    result1 = shield_normal.protect(text)
    print(f"   Masked: {result1.masked_text}")
    print(f"   Has fallback: Yes")
    print()
    
    # Azure only mode (no fallback)
    print("2. Azure-Only Mode (no fallback):")
    shield_azure = PIIShield(azure_only=True)
    result2 = shield_azure.protect(text)
    print(f"   Masked: {result2.masked_text}")
    print(f"   Has fallback: No")
    print()


if __name__ == "__main__":
    main()
    
    # Uncomment to compare modes
    # compare_modes()

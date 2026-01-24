"""
Microsoft Foundry PII Detection Example

Demonstrates how to use Microsoft Foundry Language Service for PII detection
with Microsoft Entra ID authentication (keyless, no API key required).

Prerequisites:
    - Install: pip install pii-shield[azure]
    - Set: AZURE_FOUNDRY_ENDPOINT environment variable
    - Authentication: Azure CLI (az login), Managed Identity, or VS Code Azure extension

Reference:
    https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/sdk-overview
    https://learn.microsoft.com/en-us/azure/ai-services/language-service/personally-identifiable-information/
"""

import os
from core import (
    AzurePIIDetector,
    AzureRedactionPolicy,
    is_azure_sdk_available,
    is_azure_identity_available,
)


def main():
    """
    Example using Microsoft Entra ID authentication (no API key required).
    
    Prerequisites:
        - pip install pii-shield[azure]
        - Azure CLI logged in (az login) OR
        - Running in Azure with Managed Identity OR
        - VS Code with Azure extension signed in
    """
    print("=== Microsoft Foundry PII Detection (Entra ID) ===")
    print()
    
    if not is_azure_sdk_available():
        print("Azure AI Text Analytics SDK is not installed.")
        print("Install it with: pip install pii-shield[azure]")
        return
    
    if not is_azure_identity_available():
        print("Azure Identity SDK is not installed.")
        print("Install it with: pip install azure-identity")
        return
    
    # Check for endpoint
    foundry_endpoint = os.environ.get("AZURE_FOUNDRY_ENDPOINT") or os.environ.get("AZURE_LANGUAGE_ENDPOINT")
    
    if not foundry_endpoint:
        print("Please set AZURE_FOUNDRY_ENDPOINT environment variable")
        print("Example: export AZURE_FOUNDRY_ENDPOINT='https://your-resource.cognitiveservices.azure.com/'")
        return
    
    print(f"Using endpoint: {foundry_endpoint}")
    print("Authentication: Microsoft Entra ID (DefaultAzureCredential)")
    print()
    
    try:
        # Initialize with Entra ID authentication (no API key!)
        with AzurePIIDetector(
            endpoint=foundry_endpoint,
            redaction_policy=AzureRedactionPolicy.CHARACTER_MASK,
        ) as detector:
            
            text = "My email is john@example.com and phone is 555-123-4567."
            result = detector.detect(text, language="en")
            
            # Check for errors
            if result.is_error:
                print(f"❌ Error: {result.error_message}")
                print()
                print("Common issues:")
                print("  1. Wrong endpoint format - Must be Language Service endpoint:")
                print("     ✅ https://<resource-name>.cognitiveservices.azure.com/")
                print("     ❌ https://<resource>.services.ai.azure.com/api/projects/<project>/")
                print()
                print("  2. Missing permissions:")
                print("     - Grant 'Cognitive Services Language Reader' role to your account")
                print()
                print("  3. Wrong token audience:")
                print("     - Ensure using Language Service, not Foundry Project endpoint")
                return
            
            print(f"Original: {result.original_text}")
            print(f"Redacted: {result.redacted_text}")
            print(f"Entities: {result.entity_count}")
            
            if result.entities:
                print()
                print("Detected entities:")
                for entity in result.entities:
                    print(f"  - {entity.category}: '{entity.text}' (confidence: {entity.confidence_score:.2f})")
            
    except Exception as e:
        print(f"Error: {e}")
        print()
        print("Troubleshooting:")
        print("  - Ensure you're logged in with Azure CLI: az login")
        print("  - Or running in Azure with Managed Identity enabled")
        print("  - Ensure your account has 'Cognitive Services Language Reader' role")


def compare_with_presidio():
    """
    Example comparing Azure PII detection with local Presidio detection.
    """
    from core import PIIShield, AzurePIIDetector, is_azure_sdk_available
    
    if not is_azure_sdk_available():
        print("Azure SDK not available for comparison")
        return
    
    text = "Contact John Doe at john.doe@example.com or call 555-987-6543."
    
    print("=== Comparison: Azure vs Presidio ===\n")
    
    # Presidio (local) detection
    print("Presidio (Local):")
    print("-" * 40)
    shield = PIIShield()
    presidio_result = shield.protect(text, language="en")
    print(f"  Masked: {presidio_result.masked_text}")
    print(f"  Entities: {presidio_result.entity_count}")
    
    print()
    
    # Azure (cloud) detection
    print("Azure Language Service (Cloud):")
    print("-" * 40)
    with AzurePIIDetector() as azure_detector:
        azure_result = azure_detector.detect(text, language="en")
        print(f"  Masked: {azure_result.redacted_text}")
        print(f"  Entities: {azure_result.entity_count}")


if __name__ == "__main__":
    main()

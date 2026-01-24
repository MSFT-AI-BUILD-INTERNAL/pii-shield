"""
Environment Variable Configuration Example

Demonstrates how to use .env file for configuration.
"""

import os
from pathlib import Path
from core import (
    config,
    load_environment,
    is_dotenv_available,
    AzurePIIDetector,
    PIIShield,
    EnvConfig,
)


def main():
    print("=== Environment Configuration Example ===")
    print()
    
    # Check if dotenv is available
    if not is_dotenv_available():
        print("⚠️  python-dotenv is not installed.")
        print("   Install with: pip install python-dotenv")
        print("   Falling back to system environment variables")
        print()
    else:
        print("✅ python-dotenv is available")
        
        # Check if .env file exists
        project_root = Path(__file__).parent.parent
        env_file = project_root / ".env"
        
        if env_file.exists():
            print(f"✅ Found .env file at: {env_file}")
            print()
        else:
            print(f"⚠️  No .env file found at: {env_file}")
            print("   Copy .env.sample to .env and configure your settings")
            print()
    
    # Display current configuration
    print("Current Configuration:")
    print("-" * 60)
    print(config)
    print()
    
    # Example 1: Using Config object
    print("Example 1: Using Config object")
    print("-" * 60)
    endpoint = config.AZURE_FOUNDRY_ENDPOINT
    has_key = "Yes" if config.AZURE_FOUNDRY_KEY else "No"
    
    print(f"Endpoint: {endpoint or 'Not configured'}")
    print(f"Has API Key: {has_key}")
    print(f"Default Language: {config.PII_DEFAULT_LANGUAGE}")
    print(f"Confidence Threshold: {config.PII_CONFIDENCE_THRESHOLD}")
    print()
    
    # Example 2: Using environment variables directly
    print("Example 2: Direct environment variable access")
    print("-" * 60)
    print(f"AZURE_FOUNDRY_ENDPOINT: {os.environ.get('AZURE_FOUNDRY_ENDPOINT', 'Not set')}")
    print(f"AZURE_FOUNDRY_KEY: {'***' if os.environ.get('AZURE_FOUNDRY_KEY') else 'Not set'}")
    print()
    
    # Example 3: Initialize Azure detector from config
    print("Example 3: Initialize Azure PII Detector from .env")
    print("-" * 60)
    
    if config.AZURE_FOUNDRY_ENDPOINT:
        try:
            # Option A: Use API Key if available
            if config.AZURE_FOUNDRY_KEY:
                print("Using API Key authentication")
                detector = AzurePIIDetector(
                    api_key=config.AZURE_FOUNDRY_KEY,
                    endpoint=config.AZURE_FOUNDRY_ENDPOINT,
                )
                print("✅ Azure detector initialized successfully (API Key)")
            else:
                # Option B: Use Entra ID if no API key
                print("Using Entra ID authentication")
                detector = AzurePIIDetector(
                    endpoint=config.AZURE_FOUNDRY_ENDPOINT,
                    use_entra_id=True,
                )
                print("✅ Azure detector initialized successfully (Entra ID)")
        except Exception as e:
            print(f"❌ Failed to initialize: {e}")
    else:
        print("⚠️  AZURE_FOUNDRY_ENDPOINT not configured")
    
    print()
    
    # Example 4: Initialize local Presidio shield with config
    print("Example 4: Initialize Local PII Shield with .env")
    print("-" * 60)
    
    try:
        shield = PIIShield(
            default_language=config.PII_DEFAULT_LANGUAGE,
        )
        print(f"✅ Local shield initialized with language: {config.PII_DEFAULT_LANGUAGE}")
        
        # Test detection
        test_text = "My email is john@example.com"
        result = shield.protect(
            test_text,
            score_threshold=config.PII_CONFIDENCE_THRESHOLD
        )
        print(f"   Test: '{test_text}'")
        print(f"   Result: '{result.masked_text}'")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
    
    print()
    
    # Example 5: Reload configuration
    print("Example 5: Reload configuration from different file")
    print("-" * 60)
    
    # You can load from a different .env file
    custom_env = Path(__file__).parent.parent / ".env.production"
    if custom_env.exists():
        load_environment(str(custom_env))
        print(f"✅ Loaded configuration from: {custom_env}")
    else:
        print(f"⚠️  File not found: {custom_env}")
    
    print()


def show_env_setup_guide():
    """Show setup guide for .env file."""
    print("=== Setup Guide ===")
    print()
    print("1. Copy .env.sample to .env:")
    print("   cp .env.sample .env")
    print()
    print("2. Edit .env and configure your settings:")
    print("   - AZURE_FOUNDRY_ENDPOINT (required)")
    print("   - AZURE_FOUNDRY_KEY (optional, for API Key auth)")
    print("   - Or use Entra ID authentication (no key needed)")
    print()
    print("3. Run your application:")
    print("   python samples/env_config_example.py")
    print()
    print("4. For production, use .env.production:")
    print("   cp .env.sample .env.production")
    print("   # Edit with production values")
    print()


if __name__ == "__main__":
    main()
    print()
    print("=" * 60)
    show_env_setup_guide()

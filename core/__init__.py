"""
PII Shield Core Module

Presidio-based PII Detection and Masking functionality.
Supports multiple languages including English and Korean.

Also provides Microsoft Foundry Language Service integration for cloud-based
PII detection with support for both API Key and Entra ID authentication.

Environment Variables:
    Load from .env file or set directly in environment.
    See .env.sample for configuration options.
"""

from core.detector import PIIDetector
from core.masker import PIIMasker, MaskingStrategy
from core.shield import PIIShield, PIIResult
from core.azure_pii import (
    AzurePIIDetector,
    AzurePIIResult,
    AzurePIIEntity,
    AzureRedactionPolicy,
    is_azure_sdk_available,
    is_azure_identity_available,
)
from core.env_config import (
    EnvConfig,
    config,
    load_environment,
    get_env,
    get_env_bool,
    get_env_float,
    is_dotenv_available,
)

__all__ = [
    # Presidio-based (local)
    "PIIDetector",
    "PIIMasker",
    "PIIShield",
    "PIIResult",
    "MaskingStrategy",
    # Azure/Foundry-based (cloud)
    "AzurePIIDetector",
    "AzurePIIResult",
    "AzurePIIEntity",
    "AzureRedactionPolicy",
    "is_azure_sdk_available",
    "is_azure_identity_available",
    # Configuration
    "EnvConfig",
    "config",
    "load_environment",
    "get_env",
    "get_env_bool",
    "get_env_float",
    "is_dotenv_available",
]
__version__ = "0.1.0"

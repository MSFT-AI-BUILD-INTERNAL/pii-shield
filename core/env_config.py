"""
Environment Configuration Module

Loads environment variables from .env file and provides configuration access.
Supports both .env files and system environment variables.
"""

import os
from pathlib import Path
from typing import Optional

# Try to load python-dotenv if available
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    load_dotenv = None


def load_environment(env_file: Optional[str] = None) -> bool:
    """
    Load environment variables from .env file.
    
    Args:
        env_file: Path to .env file. If None, looks for .env in project root.
    
    Returns:
        True if .env file was loaded successfully, False otherwise.
    
    Example:
        >>> from core.config import load_environment
        >>> load_environment()  # Loads .env from project root
        >>> load_environment('.env.production')  # Loads specific file
    """
    if not DOTENV_AVAILABLE:
        return False
    
    if env_file is None:
        # Look for .env in project root
        project_root = Path(__file__).parent.parent
        env_file = project_root / ".env"
    
    if not Path(env_file).exists():
        return False
    
    load_dotenv(env_file, override=False)
    return True


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get environment variable value.
    
    Args:
        key: Environment variable name.
        default: Default value if not found.
    
    Returns:
        Environment variable value or default.
    
    Example:
        >>> from core.config import get_env
        >>> endpoint = get_env('AZURE_FOUNDRY_ENDPOINT')
        >>> api_key = get_env('AZURE_FOUNDRY_KEY', '')
    """
    return os.environ.get(key, default)


def get_env_bool(key: str, default: bool = False) -> bool:
    """
    Get environment variable as boolean.
    
    Args:
        key: Environment variable name.
        default: Default value if not found.
    
    Returns:
        Boolean value (true/false/1/0/yes/no are accepted).
    
    Example:
        >>> use_entra_id = get_env_bool('USE_ENTRA_ID', False)
    """
    value = get_env(key)
    if value is None:
        return default
    
    return value.lower() in ('true', '1', 'yes', 'on')


def get_env_float(key: str, default: float = 0.0) -> float:
    """
    Get environment variable as float.
    
    Args:
        key: Environment variable name.
        default: Default value if not found.
    
    Returns:
        Float value.
    
    Example:
        >>> threshold = get_env_float('PII_CONFIDENCE_THRESHOLD', 0.5)
    """
    value = get_env(key)
    if value is None:
        return default
    
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


class EnvConfig:
    """
    Configuration class for PII Shield.
    
    Provides centralized access to environment variables with fallbacks.
    """
    
    # Microsoft Foundry / Azure Language Service
    AZURE_FOUNDRY_ENDPOINT = property(lambda self: get_env('AZURE_FOUNDRY_ENDPOINT') or get_env('AZURE_LANGUAGE_ENDPOINT'))
    AZURE_FOUNDRY_KEY = property(lambda self: get_env('AZURE_FOUNDRY_KEY') or get_env('AZURE_LANGUAGE_KEY'))
    
    # Service Principal (for Entra ID)
    AZURE_CLIENT_ID = property(lambda self: get_env('AZURE_CLIENT_ID'))
    AZURE_TENANT_ID = property(lambda self: get_env('AZURE_TENANT_ID'))
    AZURE_CLIENT_SECRET = property(lambda self: get_env('AZURE_CLIENT_SECRET'))
    
    # Application settings
    PII_DEFAULT_LANGUAGE = property(lambda self: get_env('PII_DEFAULT_LANGUAGE', 'en'))
    PII_DEFAULT_STRATEGY = property(lambda self: get_env('PII_DEFAULT_STRATEGY', 'replace'))
    PII_CONFIDENCE_THRESHOLD = property(lambda self: get_env_float('PII_CONFIDENCE_THRESHOLD', 0.5))
    
    # Azure-specific settings
    AZURE_REDACTION_POLICY = property(lambda self: get_env('AZURE_REDACTION_POLICY', 'character_mask'))
    AZURE_MASK_CHARACTER = property(lambda self: get_env('AZURE_MASK_CHARACTER', '*'))
    
    @classmethod
    def load(cls, env_file: Optional[str] = None) -> 'EnvConfig':
        """
        Load configuration from .env file.
        
        Args:
            env_file: Path to .env file.
        
        Returns:
            EnvConfig instance.
        
        Example:
            >>> config = EnvConfig.load()
            >>> print(config.AZURE_FOUNDRY_ENDPOINT)
        """
        load_environment(env_file)
        return cls()
    
    def __repr__(self) -> str:
        """String representation of config (hides sensitive data)."""
        endpoint = self.AZURE_FOUNDRY_ENDPOINT or 'Not set'
        has_key = 'Yes' if self.AZURE_FOUNDRY_KEY else 'No'
        return (
            f"EnvConfig(\n"
            f"  endpoint={endpoint},\n"
            f"  has_api_key={has_key},\n"
            f"  default_language={self.PII_DEFAULT_LANGUAGE},\n"
            f"  confidence_threshold={self.PII_CONFIDENCE_THRESHOLD}\n"
            f")"
        )


# Auto-load .env on import
load_environment()

# Create default config instance
config = EnvConfig()


def is_dotenv_available() -> bool:
    """
    Check if python-dotenv is available.
    
    Returns:
        True if dotenv is installed, False otherwise.
    """
    return DOTENV_AVAILABLE

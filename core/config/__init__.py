"""
Configuration files for PII Shield.

Contains YAML configuration files for Presidio Recognizer Registry.
"""

from pathlib import Path

CONFIG_DIR = Path(__file__).parent

RECOGNIZERS_EN_CONFIG = CONFIG_DIR / "recognizers_en.yaml"
RECOGNIZERS_KO_CONFIG = CONFIG_DIR / "recognizers_ko.yaml"

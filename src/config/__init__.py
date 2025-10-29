"""
Configuration management for AK Group application.

This package provides settings and constants used throughout the application.
"""

from src.config.settings import Settings, get_settings
from src.config.constants import (
    DEFAULT_CURRENCY,
    DEFAULT_TAX_RATE,
    DEFAULT_PAGINATION_LIMIT,
)

__all__ = [
    "Settings",
    "get_settings",
    "DEFAULT_CURRENCY",
    "DEFAULT_TAX_RATE",
    "DEFAULT_PAGINATION_LIMIT",
]

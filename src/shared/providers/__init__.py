"""Providers para inyección de dependencias."""
from .time_provider import TimeProvider, FakeTimeProvider, ITimeProvider

__all__ = ["TimeProvider", "FakeTimeProvider", "ITimeProvider"]

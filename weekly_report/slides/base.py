"""
Abstract base classes for Weekly Slide Generators (SOLID - ISP / DIP)
"""
from abc import ABC, abstractmethod
from typing import Any, Dict
import pandas as pd


class SlideGenerator(ABC):
    """Base interface for all slide generators (ISP: each slide has its own contract)"""

    @abstractmethod
    def generate(self, **kwargs) -> Dict[str, Any]:
        """Generate slide data. Returns a dict with slide-specific keys."""
        ...


class InsightMixin:
    """Mixin for slides that call LLM to produce an insight paragraph."""

    @abstractmethod
    def _generate_insight(self, **kwargs) -> str: ...

"""Base agent abstract definition."""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAgent(ABC):
    """Abstract base class for Kaggriculture agents."""

    def __init__(self, name: str = "BaseAgent") -> None:
        self.name = name

    def reset(self) -> None:
        """Reset internal agent memory for a new episode."""
        pass

    def act(self, obs: Dict[str, Any], config: Any = None) -> Dict[str, Any]:
        """Produce per-turn action dictionary.

        Returns:
            dict with keys "farmer": [op, ...], "hands": [[op, ...], ...], "market": [[op, ...], ...]
        """
        raise NotImplementedError

    def __call__(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Convenience caller for kaggle-environments which passes (observation, configuration)."""
        obs = args[0] if args else kwargs.get("obs", {})
        config = args[1] if len(args) > 1 else kwargs.get("config", None)
        return self.act(obs, config)

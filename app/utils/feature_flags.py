from typing import Any

from config import FEATURE_FLAGS as CONFIG_FLAGS

FEATURE_FLAGS: dict[str, Any] = dict(CONFIG_FLAGS)
FEATURE_FLAGS.setdefault("billing_enabled", False)


def get_feature_flag(name: str, default: Any = False) -> Any:
    return FEATURE_FLAGS.get(name, default)


def set_feature_flag(name: str, value: Any) -> None:
    FEATURE_FLAGS[name] = value


__all__ = ["FEATURE_FLAGS", "get_feature_flag", "set_feature_flag"]

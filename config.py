import os


def _env_flag(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).lower() in {"1", "true", "yes"}


def env_value(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)


FEATURE_FLAGS = {
    "multi_tenant_enabled": _env_flag("FEATURE_MULTI_TENANT"),
}

STRIPE_TEST_PUBLISHABLE_KEY = env_value("STRIPE_TEST_PUBLISHABLE_KEY")
STRIPE_TEST_SECRET_KEY = env_value("STRIPE_TEST_SECRET_KEY")
STRIPE_ACTIVE_PRICE_ID = env_value("STRIPE_ACTIVE_PRICE_ID", "price_1SDaPGQpDeiCy5Mxx8VOvW4t")
STRIPE_CHECKOUT_SUCCESS_URL = env_value("STRIPE_CHECKOUT_SUCCESS_URL", "http://localhost:8000/app#billing-success")
STRIPE_CHECKOUT_CANCEL_URL = env_value("STRIPE_CHECKOUT_CANCEL_URL", "http://localhost:8000/app#billing-cancel")
STRIPE_WEBHOOK_SECRET = env_value("STRIPE_WEBHOOK_SECRET")

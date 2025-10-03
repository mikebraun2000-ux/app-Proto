"""Pytest shared fixtures and configuration."""

import os

# Ensure a deterministic secret key is always present during test runs.
os.environ.setdefault("SECRET_KEY", "test-secret-key-change-me")

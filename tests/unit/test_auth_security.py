"""Unit-Tests für Passwort-Hashing und Auth-Sicherheit."""

import hashlib

import pytest

from app.auth import get_password_hash, verify_password, needs_rehash


def test_password_hash_uses_argon2():
    """Neue Passwörter sollen Argon2 verwenden."""
    hashed = get_password_hash("TestPasswort123")
    assert hashed.startswith("$argon2"), "Hash sollte Argon2 verwenden"


def test_password_verification_success():
    """Korrekte Passwörter werden akzeptiert."""
    password = "SicheresPasswort!"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)


def test_password_verification_failure():
    """Falsche Passwörter müssen abgelehnt werden."""
    hashed = get_password_hash("EinAnderesPasswort")
    assert not verify_password("FalschesPasswort", hashed)


def test_same_password_creates_different_hash():
    """Gleiche Passwörter erzeugen unterschiedliche Hashes wegen Salt."""
    password = "RandomPasswort!"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    assert hash1 != hash2, "Salting sollte unterschiedliche Hashes erzeugen"
    assert verify_password(password, hash1)
    assert verify_password(password, hash2)


def test_needs_rehash_for_legacy_sha256():
    """Alte SHA256-Hashes müssen als rehash-bedürftig erkannt werden."""
    legacy_hash = "sha256:" + hashlib.sha256("admin123".encode()).hexdigest()
    assert needs_rehash(legacy_hash), "Legacy-Hash sollte Rehash benötigen"


def test_legacy_sha256_still_verifies():
    """Legacy SHA256-Hashes sollen vorübergehend akzeptiert werden."""
    password = "admin123"
    legacy_hash = "sha256:" + hashlib.sha256(password.encode()).hexdigest()
    assert verify_password(password, legacy_hash)


def test_needs_rehash_false_for_modern_hash():
    """Neue Argon2-Hashes dürfen kein Rehash benötigen."""
    hashed = get_password_hash("ModernPasswort")
    assert not needs_rehash(hashed)


def test_invalid_hash_returns_false():
    """Ungültige Hashes dürfen nicht akzeptiert werden."""
    assert not verify_password("irgendwas", "invalid-hash")



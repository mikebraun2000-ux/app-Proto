"""Authentifizierung und Autorisierung für die Bau-Dokumentations-App."""

import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select

from app.database import get_session
from app.models import User, UserRole
from app.schemas import TokenData

try:
    from dotenv import load_dotenv  # type: ignore
except ImportError:  # pragma: no cover
    load_dotenv = None

if load_dotenv:
    load_dotenv()


def _resolve_secret_key() -> str:
    """Reads the SECRET_KEY from the environment and fails fast when missing."""

    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        raise RuntimeError("SECRET_KEY ist nicht gesetzt. Bitte .env konfigurieren.")
    return secret_key


SECRET_KEY = _resolve_secret_key()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Passwort-Hashing
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
    argon2__memory_cost=65536,
    argon2__time_cost=3,
    argon2__parallelism=4,
)

# HTTP Bearer Token
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Überprüft ein Passwort gegen den Hash."""
    if not hashed_password:
        return False

    try:
        if pwd_context.verify(plain_password, hashed_password):
            return True
    except Exception:
        pass

    # Legacy SHA256
    if hashed_password.startswith("sha256:"):
        import hashlib

        expected_hash = "sha256:" + hashlib.sha256(plain_password.encode()).hexdigest()
        if expected_hash == hashed_password:
            return True

    # Keine weiteren Fallbacks zulassen – Legacy-Passwörter sind deaktiviert.
    return False


def get_password_hash(password: str) -> str:
    """Erstellt einen sicheren Hash für ein Passwort."""
    return pwd_context.hash(password)


def needs_rehash(hashed_password: str) -> bool:
    """Prüft, ob ein Hash aktualisiert werden sollte."""
    try:
        return pwd_context.needs_update(hashed_password)
    except Exception:
        return True


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Erstellt einen JWT-Token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """Überprüft einen JWT-Token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return TokenData(username=username)
    except JWTError:
        return None


def get_user_by_username(session: Session, username: str) -> Optional[User]:
    """Holt einen Benutzer anhand des Benutzernamens."""
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()


def authenticate_user(session: Session, username: str, password: str) -> Optional[User]:
    """Authentifiziert einen Benutzer."""
    user = get_user_by_username(session, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None

    if needs_rehash(user.hashed_password):
        user.hashed_password = get_password_hash(password)
        session.add(user)
        session.commit()

    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """Holt den aktuellen Benutzer aus dem Token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_token(credentials.credentials)
    if token_data is None:
        raise credentials_exception

    user = get_user_by_username(session, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def require_role(required_role: UserRole):
    """Dependency für rollenbasierte Berechtigungen."""

    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user

    return role_checker


def require_admin(current_user: User = Depends(get_current_user)):
    """Dependency für Admin-Berechtigung."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_employee_or_admin(current_user: User = Depends(get_current_user)):
    """Dependency für Mitarbeiter oder Admin."""
    if current_user.role not in [UserRole.MITARBEITER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee or admin access required"
        )
    return current_user


def require_buchhalter_or_admin(current_user: User = Depends(get_current_user)):
    """Dependency für Buchhalter oder Admin."""
    if current_user.role not in [UserRole.BUCHHALTER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Buchhalter or admin access required"
        )
    return current_user

"""API-Router für benutzerspezifische Einstellungen (z. B. Theme)."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.auth import get_current_user
from app.database import get_session
from app.models import User, UserSettings
from app.schemas import UserSettingsResponse, UserSettingsUpdate

router = APIRouter(prefix="/user/settings", tags=["User Settings"])

SUPPORTED_THEMES = {"light", "dark"}


def _get_or_create_user_settings(session: Session, user_id: int) -> UserSettings:
    """Lädt die Einstellungen des Benutzers oder legt sie mit Standardwerten an."""

    settings = session.exec(
        select(UserSettings).where(UserSettings.user_id == user_id)
    ).first()
    if settings:
        return settings

    settings = UserSettings(user_id=user_id)
    session.add(settings)
    session.commit()
    session.refresh(settings)
    return settings


@router.get("", response_model=UserSettingsResponse)
async def read_user_settings(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> UserSettingsResponse:
    """Gibt die gespeicherten Einstellungen des aktuellen Benutzers zurück."""

    settings = _get_or_create_user_settings(session, current_user.id)
    return UserSettingsResponse.model_validate(settings)


@router.put("", response_model=UserSettingsResponse)
async def update_user_settings(
    update: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> UserSettingsResponse:
    """Aktualisiert die benutzerspezifischen Einstellungen (z. B. Theme)."""

    settings = _get_or_create_user_settings(session, current_user.id)

    if update.theme_preference is not None:
        normalized_theme = update.theme_preference.lower()
        if normalized_theme not in SUPPORTED_THEMES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unsupported theme preference."
            )
        settings.theme_preference = normalized_theme

    settings.updated_at = datetime.utcnow()
    session.add(settings)
    session.commit()
    session.refresh(settings)
    return UserSettingsResponse.model_validate(settings)

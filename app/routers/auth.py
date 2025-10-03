"""
Authentifizierungs-Endpoints für die Bau-Dokumentations-App.
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models import User, TenantInvitation, UserRole, TenantSettings
from app.schemas import (
    UserCreate,
    UserLogin,
    UserUpdate,
    Token,
    User as UserSchema,
    TenantSettingsResponse,
    TenantSettingsUpdate
)
from app.auth import (
    get_password_hash, 
    authenticate_user, 
    create_access_token, 
    get_current_user,
    require_admin,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.services.invite_service import InvitationService, TOKEN_TTL_HOURS

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, session: Session = Depends(get_session)):
    """Benutzeranmeldung."""
    user = authenticate_user(session, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    session.add(user)
    session.commit()
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserSchema)
async def register(
    user_data: UserCreate,
    session: Session = Depends(get_session),
    _: User = Depends(require_admin)
):
    """Benutzerregistrierung (nur für Admins)."""
    # Prüfe ob Benutzername bereits existiert
    existing_user = session.exec(
        select(User).where(User.username == user_data.username)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Prüfe ob E-Mail bereits existiert
    existing_email = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Erstelle neuen Benutzer
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role
    )
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    return db_user

@router.get("/users", response_model=list[UserSchema])
async def list_users(_: User = Depends(require_admin), session: Session = Depends(get_session)):
    """Alle Benutzer für die Verwaltung abrufen."""
    users = session.exec(select(User)).all()
    return [
        UserSchema(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            last_login=user.last_login,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        for user in users
    ]

@router.put("/users/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """Bestehenden Benutzer aktualisieren (Admin)."""
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Benutzer nicht gefunden")

    update_data = user_update.model_dump(exclude_unset=True)

    if 'role' in update_data and update_data['role'] == current_user.role and db_user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Eigene Rolle kann hier nicht geändert werden")

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db_user.updated_at = datetime.utcnow()
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return UserSchema(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        full_name=db_user.full_name,
        name=db_user.full_name,
        role=db_user.role,
        is_active=db_user.is_active,
        last_login=db_user.last_login,
        created_at=db_user.created_at,
        updated_at=db_user.updated_at
    )

@router.post("/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    new_password: dict,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """Passwort eines Benutzers zurücksetzen (Admin)."""
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Benutzer nicht gefunden")

    password = new_password.get('password')
    if not password or len(password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwort muss mindestens 8 Zeichen haben")

    db_user.hashed_password = get_password_hash(password)
    db_user.updated_at = datetime.utcnow()
    session.add(db_user)
    session.commit()

    return {"message": "Passwort wurde aktualisiert"}


@router.post("/invite")
async def create_invitation(
    payload: dict,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """Admin lädt einen neuen Benutzer per E-Mail ein."""
    email = payload.get("email")
    role_value = payload.get("role", UserRole.MITARBEITER.value)

    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email erforderlich")

    try:
        role = UserRole(role_value)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ungültige Rolle")

    invitation_service = InvitationService(session)

    invitation, token = invitation_service.create_invitation(
        tenant_id=current_user.tenant_id,
        email=email,
        role=role,
        invited_by=current_user.id,
        ttl_hours=payload.get("ttl_hours", TOKEN_TTL_HOURS),
    )

    return {
        "invitation_id": invitation.id,
        "token": token,
        "expires_at": invitation.expires_at,
    }


@router.post("/invite/accept")
async def accept_invitation(payload: dict, session: Session = Depends(get_session)):
    """Eingeladener Benutzer akzeptiert Einladung, setzt Passwort."""
    token = payload.get("token")
    full_name = payload.get("full_name")
    password = payload.get("password")

    if not token or not full_name or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token, Name und Passwort erforderlich")

    invitation_service = InvitationService(session)
    invitation = invitation_service.get_invitation_by_token(token)
    if not invitation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Einladung ungültig oder abgelaufen")

    existing_user = session.exec(select(User).where(User.email == invitation.email)).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Benutzer existiert bereits")

    hashed_password = get_password_hash(password)

    new_user = invitation_service.create_user_from_invitation(
        invitation=invitation,
        full_name=full_name,
        hashed_password=hashed_password,
    )

    invitation_service.accept_invitation(invitation)
    invitation_service.ensure_employee_for_user(new_user)

    return {
        "message": "Einladung akzeptiert",
        "user_id": new_user.id,
    }


@router.post("/invite/resend")
async def resend_invitation(
    payload: dict,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """Einladung erneut senden (generiert neues Token)."""
    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email erforderlich")

    invitation_service = InvitationService(session)
    existing = invitation_service.find_active_invitation(current_user.tenant_id, email)
    if existing:
        invitation_service.delete_invitation(existing)

    invitation, token = invitation_service.create_invitation(
        tenant_id=current_user.tenant_id,
        email=email,
        role=role,
        invited_by=current_user.id,
    )

    return {
        "invitation_id": invitation.id,
        "token": token,
        "expires_at": invitation.expires_at,
    }

@router.get("/invitations")
async def list_invitations(current_user: User = Depends(require_admin), session: Session = Depends(get_session)):
    statement = select(TenantInvitation).where(TenantInvitation.tenant_id == current_user.tenant_id)
    invitations = session.exec(statement).all()
    result = []
    for invitation in invitations:
        invited_by_name = None
        if invitation.invited_by:
            inviter = session.get(User, invitation.invited_by)
            invited_by_name = inviter.full_name if inviter else None
        result.append({
            'id': invitation.id,
            'tenant_id': invitation.tenant_id,
            'email': invitation.email,
            'role': invitation.role,
            'invited_by': invitation.invited_by,
            'invited_by_name': invited_by_name,
            'accepted_at': invitation.accepted_at,
            'expires_at': invitation.expires_at,
            'created_at': invitation.created_at,
        })
    return result

@router.delete("/invitations/{invitation_id}")
async def delete_invitation(
    invitation_id: int,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    invitation = session.get(TenantInvitation, invitation_id)
    if not invitation or invitation.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Einladung nicht gefunden")
    session.delete(invitation)
    session.commit()
    return {"message": "Einladung gelöscht"}

@router.get("/me")
async def read_users_me(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    settings = session.exec(
        select(TenantSettings).where(TenantSettings.tenant_id == current_user.tenant_id)
    ).first()

    if not settings:
        settings = TenantSettings(tenant_id=current_user.tenant_id)
        session.add(settings)
        session.commit()
        session.refresh(settings)

    tenant_schema = TenantSettingsResponse.model_validate(settings)
    user_schema = UserSchema(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        last_login=current_user.last_login,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )

    return {
        "user": user_schema.model_dump(mode="json"),
        "tenant": tenant_schema.model_dump(mode="json")
    }

@router.get("/tenant/settings", response_model=TenantSettingsResponse)
async def get_tenant_settings(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    settings = session.exec(
        select(TenantSettings).where(TenantSettings.tenant_id == current_user.tenant_id)
    ).first()

    if not settings:
        settings = TenantSettings(tenant_id=current_user.tenant_id)
        session.add(settings)
        session.commit()
        session.refresh(settings)

    return TenantSettingsResponse.model_validate(settings)


@router.put("/tenant/settings", response_model=TenantSettingsResponse)
async def update_tenant_settings(
    payload: TenantSettingsUpdate,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    settings = session.exec(
        select(TenantSettings).where(TenantSettings.tenant_id == current_user.tenant_id)
    ).first()

    if not settings:
        settings = TenantSettings(tenant_id=current_user.tenant_id)

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(settings, field, value)

    settings.updated_at = datetime.utcnow()
    session.add(settings)
    session.commit()
    session.refresh(settings)

    return TenantSettingsResponse.model_validate(settings)


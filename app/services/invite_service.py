"""Dienst zum Verwalten von Einladungstokens."""

from __future__ import annotations

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional

from sqlmodel import Session, select

from app.models import TenantInvitation, UserRole, User, Employee


TOKEN_LENGTH = 48
TOKEN_TTL_HOURS = 168  # 7 Tage


class InvitationService:
    """Zentrale Logik für das Erstellen und Verwalten von Einladungen."""

    def __init__(self, session: Session):
        self.session = session

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def _normalize_email(self, email: str) -> str:
        return email.strip().lower()

    def _generate_username(self, email: str, full_name: Optional[str] = None) -> str:
        base = email.split("@")[0]
        if full_name:
            name_slug = "".join(ch for ch in full_name.lower() if ch.isalnum())
            if name_slug:
                base = name_slug

        candidate = base
        suffix = 1
        while self.session.exec(select(User).where(User.username == candidate)).first():
            candidate = f"{base}{suffix}"
            suffix += 1
        return candidate

    def create_invitation(
        self,
        tenant_id: int,
        email: str,
        role: UserRole,
        invited_by: Optional[int],
        ttl_hours: int = TOKEN_TTL_HOURS,
    ) -> tuple[TenantInvitation, str]:
        plain_token = secrets.token_urlsafe(TOKEN_LENGTH)
        token_hash = self._hash_token(plain_token)

        expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)

        normalized_email = self._normalize_email(email)

        invitation = TenantInvitation(
            tenant_id=tenant_id,
            email=normalized_email,
            token_hash=token_hash,
            role=role,
            invited_by=invited_by,
            expires_at=expires_at,
        )

        self.session.add(invitation)
        self.session.commit()
        self.session.refresh(invitation)

        return invitation, plain_token

    def get_invitation_by_token(self, token: str) -> Optional[TenantInvitation]:
        token_hash = self._hash_token(token)
        statement = select(TenantInvitation).where(TenantInvitation.token_hash == token_hash)
        invitation = self.session.exec(statement).first()
        if invitation and invitation.expires_at < datetime.utcnow():
            return None
        return invitation

    def accept_invitation(self, invitation: TenantInvitation) -> None:
        invitation.accepted_at = datetime.utcnow()
        self.session.add(invitation)
        self.session.commit()

    def delete_invitation(self, invitation: TenantInvitation) -> None:
        self.session.delete(invitation)
        self.session.commit()

    def find_active_invitation(self, tenant_id: int, email: str) -> Optional[TenantInvitation]:
        normalized_email = self._normalize_email(email)
        statement = select(TenantInvitation).where(
            TenantInvitation.tenant_id == tenant_id,
            TenantInvitation.email == normalized_email
        )
        return self.session.exec(statement).first()

    def create_user_from_invitation(
        self,
        invitation: TenantInvitation,
        full_name: str,
        hashed_password: str,
    ) -> User:
        username = self._generate_username(invitation.email, full_name)
        new_user = User(
            username=username,
            email=invitation.email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=invitation.role,
            tenant_id=invitation.tenant_id,
            is_active=True,
        )

        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)
        return new_user

    def ensure_employee_for_user(
        self,
        user: User,
        hourly_rate: Optional[float] = None,
    ) -> Employee:
        statement = select(Employee).where(Employee.user_id == user.id)
        employee = self.session.exec(statement).first()
        if employee:
            return employee

        employee = Employee(
            tenant_id=user.tenant_id,
            user_id=user.id,
            full_name=user.full_name,
            email=user.email,
            hourly_rate=hourly_rate,
            is_active=True,
        )
        self.session.add(employee)
        self.session.commit()
        self.session.refresh(employee)
        return employee



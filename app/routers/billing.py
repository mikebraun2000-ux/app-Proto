"""Billing-Endpoints für Stripe."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.auth import require_admin, get_current_user
from app.database import get_session
from app.models import Tenant, User
from app.services import StripeService
from app.utils import feature_flags

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.post("/checkout")
def create_checkout_session(
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    """Erstellt eine Stripe-Checkout-Session für den aktuellen Tenant."""
    if not feature_flags.get_feature_flag("billing_enabled", False):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Billing deaktiviert")

    tenant = session.get(Tenant, current_user.tenant_id)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant nicht gefunden")

    service = StripeService(session)
    service.upsert_customer(tenant)
    url = service.create_checkout_session(tenant)

    return {"checkout_url": url}


@router.post("/webhook")
async def stripe_webhook(request: Request, session: Session = Depends(get_session)) -> Any:
    """Empfängt Stripe-Webhooks und verarbeitet relevante Events."""
    if not feature_flags.get_feature_flag("billing_enabled", False):
        return JSONResponse(status_code=200, content={"ignored": True})
    payload = await request.json()
    event_type = payload.get("type")

    logger.info("Stripe-Webhook empfangen: %s", event_type)

    service = StripeService(session)

    if event_type == "customer.subscription.updated":
        service.handle_subscription_updated(payload)
    elif event_type == "invoice.payment_failed":
        service.handle_invoice_payment_failed(payload)
    elif event_type == "invoice.payment_succeeded":
        service.handle_invoice_payment_succeeded(payload)
    else:
        logger.debug("Stripe-Event ignoriert: %s", event_type)

    return JSONResponse(status_code=200, content={"received": True})


@router.get("/status")
async def get_billing_status(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Einfache Rückgabe - Multi-Tenant-Modus ist nicht aktiviert
    return {
        "status": "inactive",
        "subscription_status": "inactive",
        "plan_name": "Kein Abonnement",
        "current_period_end": None,
        "last_payment_status": None,
        "plan_price_id": None,
        "seats_limit": None,
        "projects_limit": None,
        "message": "Multi-Tenant-Modus ist derzeit nicht aktiviert. Das Billing-Feature wird in Phase 4 vollständig implementiert."
    }


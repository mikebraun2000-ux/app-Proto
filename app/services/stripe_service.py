"""Stripe-Integration für Subscription-Billing."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    stripe = None

from sqlmodel import Session, select

import config
from app.models import Tenant, TenantStatus

logger = logging.getLogger(__name__)


class StripeNotConfiguredError(RuntimeError):
    """Fehler, wenn Stripe-Schlüssel fehlen."""


class StripeService:
    """Kapselt alle Stripe-Operationen für Billing."""

    def __init__(self, session: Session):
        if not STRIPE_AVAILABLE:
            raise StripeNotConfiguredError("Stripe-Modul nicht installiert. Führe aus: pip install stripe")
        if not config.STRIPE_TEST_SECRET_KEY:
            raise StripeNotConfiguredError("Stripe Secret Key nicht konfiguriert")
        stripe.api_key = config.STRIPE_TEST_SECRET_KEY
        self.session = session

    def create_checkout_session(self, tenant: Tenant) -> str:
        """Erstellt eine Checkout-Session und liefert die URL zurück."""
        if not config.STRIPE_ACTIVE_PRICE_ID:
            raise StripeNotConfiguredError("Stripe Price ID nicht konfiguriert")

        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": config.STRIPE_ACTIVE_PRICE_ID, "quantity": 1}],
            success_url=config.STRIPE_CHECKOUT_SUCCESS_URL,
            cancel_url=config.STRIPE_CHECKOUT_CANCEL_URL,
            customer_creation="always",
            metadata={
                "tenant_id": str(tenant.id),
                "tenant_name": tenant.name,
            },
        )
        return session.url

    def upsert_customer(self, tenant: Tenant) -> str:
        """Erstellt oder aktualisiert einen Stripe-Customer für den Tenant."""
        if tenant.stripe_customer_id:
            customer = stripe.Customer.modify(
                tenant.stripe_customer_id,
                name=tenant.name,
            )
        else:
            customer = stripe.Customer.create(name=tenant.name)
            tenant.stripe_customer_id = customer.id
            self.session.add(tenant)
            self.session.commit()
            self.session.refresh(tenant)
        return customer.id

    def handle_subscription_updated(self, payload: dict) -> None:
        """Verarbeitet `customer.subscription.updated` Webhook."""
        data = payload.get("data", {}).get("object", {})
        customer_id = data.get("customer")
        subscription_id = data.get("id")
        status = data.get("status")
        current_period_end = data.get("current_period_end")
        cancel_at_period_end = data.get("cancel_at_period_end")

        tenant = self._get_tenant_by_customer(customer_id)
        if not tenant:
            logger.warning("Kein Tenant für Stripe-Customer %s gefunden", customer_id)
            return

        tenant.stripe_subscription_id = subscription_id
        tenant.subscription_status = status
        tenant.current_period_end = datetime.utcfromtimestamp(current_period_end) if current_period_end else None
        tenant.plan_price_id = self._extract_price_id(data)
        tenant.suspended_at = None if status in {"active", "trialing"} else tenant.suspended_at
        if cancel_at_period_end:
            tenant.status = TenantStatus.PAST_DUE

        self.session.add(tenant)
        self.session.commit()

    def handle_invoice_payment_failed(self, payload: dict) -> None:
        data = payload.get("data", {}).get("object", {})
        customer_id = data.get("customer")
        tenant = self._get_tenant_by_customer(customer_id)
        if not tenant:
            logger.warning("Kein Tenant für Stripe-Customer %s gefunden", customer_id)
            return

        tenant.last_payment_status = "failed"
        tenant.subscription_status = "past_due"
        tenant.status = TenantStatus.PAST_DUE
        tenant.suspended_at = datetime.utcnow()

        self.session.add(tenant)
        self.session.commit()

    def handle_invoice_payment_succeeded(self, payload: dict) -> None:
        data = payload.get("data", {}).get("object", {})
        customer_id = data.get("customer")
        tenant = self._get_tenant_by_customer(customer_id)
        if not tenant:
            logger.warning("Kein Tenant für Stripe-Customer %s gefunden", customer_id)
            return

        tenant.last_payment_status = "succeeded"
        tenant.subscription_status = "active"
        tenant.status = TenantStatus.ACTIVE
        tenant.suspended_at = None

        self.session.add(tenant)
        self.session.commit()

    def _get_tenant_by_customer(self, stripe_customer_id: Optional[str]) -> Optional[Tenant]:
        if not stripe_customer_id:
            return None
        statement = select(Tenant).where(Tenant.stripe_customer_id == stripe_customer_id)
        return self.session.exec(statement).first()

    @staticmethod
    def _extract_price_id(subscription_data: dict) -> Optional[str]:
        items = subscription_data.get("items", {}).get("data", [])
        if not items:
            return None
        price = items[0].get("price")
        return price.get("id") if price else None


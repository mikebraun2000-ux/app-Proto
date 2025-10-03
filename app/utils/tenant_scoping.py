"""Hilfsfunktionen für mandantenbezogene Datenbankoperationen."""

from __future__ import annotations

from typing import Optional, Type, TypeVar

from fastapi import HTTPException
from sqlmodel import SQLModel
from sqlalchemy.sql import Select

ModelType = TypeVar("ModelType", bound=SQLModel)


def add_tenant_filter(statement: Select, model: Type[ModelType], tenant_id: int) -> Select:
    """Füge einer SQL-Abfrage automatisch den Tenant-Filter hinzu."""
    if hasattr(model, "tenant_id"):
        statement = statement.where(getattr(model, "tenant_id") == tenant_id)
    return statement


def ensure_tenant_access(
    resource: Optional[ModelType],
    tenant_id: int,
    *,
    not_found_detail: str = "Resource not found",
) -> ModelType:
    """Sicherstellen, dass ein Datensatz zum aktuellen Mandanten gehört."""
    if resource is None:
        raise HTTPException(status_code=404, detail=not_found_detail)

    resource_tenant_id = getattr(resource, "tenant_id", None)
    if resource_tenant_id is not None and resource_tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail=not_found_detail)

    return resource


def set_tenant_on_model(instance: ModelType, tenant_id: int) -> ModelType:
    """Setze die Tenant-ID auf einem SQLModel-Objekt, sofern vorhanden."""
    if hasattr(instance, "tenant_id"):
        setattr(instance, "tenant_id", tenant_id)
    return instance

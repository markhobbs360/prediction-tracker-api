from uuid import UUID
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


# --- Feature schemas ---

class FeatureCreate(BaseModel):
    name: str
    category: str | None = None
    status: str = "available"
    quality_notes: str | None = None


class FeatureUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    status: str | None = None
    quality_notes: str | None = None


class FeatureOut(BaseModel):
    id: UUID
    client_id: UUID
    name: str
    category: str | None = None
    status: str
    quality_notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Program schemas ---

class ProgramCreate(BaseModel):
    name: str
    description: str | None = None
    program_type: str | None = None
    giving_range_min: Decimal | None = None
    giving_range_max: Decimal | None = None
    success_definition: str | None = None
    training_data_description: str | None = None
    is_portfolio_based: bool = False


class ProgramUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    program_type: str | None = None
    giving_range_min: Decimal | None = None
    giving_range_max: Decimal | None = None
    success_definition: str | None = None
    training_data_description: str | None = None
    is_portfolio_based: bool | None = None
    is_active: bool | None = None


class ProgramOut(BaseModel):
    id: UUID
    client_id: UUID
    name: str
    description: str | None = None
    program_type: str | None = None
    giving_range_min: Decimal | None = None
    giving_range_max: Decimal | None = None
    success_definition: str | None = None
    training_data_description: str | None = None
    is_portfolio_based: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Client schemas ---

class ClientCreate(BaseModel):
    name: str
    slug: str
    institution_type: str | None = None
    crm_platform: str | None = None
    data_import_status: str | None = None
    platform_capabilities: dict | None = None
    client_preferences: dict | None = None
    historical_context: str | None = None
    notes: str | None = None
    box_folder_url: str | None = None
    flowers_tenant_id: str | None = None


class ClientUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    institution_type: str | None = None
    crm_platform: str | None = None
    data_import_status: str | None = None
    platform_capabilities: dict | None = None
    client_preferences: dict | None = None
    historical_context: str | None = None
    notes: str | None = None
    box_folder_url: str | None = None
    flowers_tenant_id: str | None = None
    is_active: bool | None = None


class ClientOut(BaseModel):
    id: UUID
    name: str
    slug: str
    institution_type: str | None = None
    crm_platform: str | None = None
    data_import_status: str | None = None
    platform_capabilities: dict | None = None
    client_preferences: dict | None = None
    historical_context: str | None = None
    notes: str | None = None
    box_folder_url: str | None = None
    flowers_tenant_id: str | None = None
    is_active: bool
    created_by: UUID | None = None
    created_at: datetime
    updated_at: datetime
    programs: list[ProgramOut] = []
    features: list[FeatureOut] = []

    model_config = {"from_attributes": True}

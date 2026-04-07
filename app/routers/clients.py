from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.client import Client
from app.models.program import Program
from app.models.feature import Feature
from app.models.user import User
from app.schemas.client import (
    ClientCreate,
    ClientOut,
    ClientUpdate,
    FeatureCreate,
    FeatureOut,
    FeatureUpdate,
    ProgramCreate,
    ProgramOut,
    ProgramUpdate,
)

router = APIRouter(prefix="/clients", tags=["clients"])

PAGE_SIZE = 20


# --- Clients ---

@router.get("", response_model=list[ClientOut])
async def list_clients(
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    stmt = select(Client).where(Client.is_active.is_(True))
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            or_(Client.name.ilike(pattern), Client.slug.ilike(pattern))
        )
    stmt = stmt.order_by(Client.name).offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE)
    result = await db.execute(stmt)
    return [ClientOut.model_validate(c) for c in result.scalars().all()]


@router.post("", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
async def create_client(
    body: ClientCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    client = Client(**body.model_dump(), created_by=user.id)
    db.add(client)
    await db.flush()
    await db.refresh(client)
    return ClientOut.model_validate(client)


@router.get("/{client_id}", response_model=ClientOut)
async def get_client(
    client_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return ClientOut.model_validate(client)


@router.put("/{client_id}", response_model=ClientOut)
async def update_client(
    client_id: UUID,
    body: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(client, key, val)
    await db.flush()
    await db.refresh(client)
    return ClientOut.model_validate(client)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    client.is_active = False
    await db.flush()


# --- Programs ---

@router.get("/{client_id}/programs", response_model=list[ProgramOut])
async def list_programs(
    client_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    stmt = select(Program).where(Program.client_id == client_id, Program.is_active.is_(True))
    result = await db.execute(stmt)
    return [ProgramOut.model_validate(p) for p in result.scalars().all()]


@router.post("/{client_id}/programs", response_model=ProgramOut, status_code=status.HTTP_201_CREATED)
async def create_program(
    client_id: UUID,
    body: ProgramCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    program = Program(**body.model_dump(), client_id=client_id)
    db.add(program)
    await db.flush()
    await db.refresh(program)
    return ProgramOut.model_validate(program)


@router.put("/{client_id}/programs/{program_id}", response_model=ProgramOut)
async def update_program(
    client_id: UUID,
    program_id: UUID,
    body: ProgramUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Program).where(Program.id == program_id, Program.client_id == client_id)
    )
    program = result.scalar_one_or_none()
    if program is None:
        raise HTTPException(status_code=404, detail="Program not found")
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(program, key, val)
    await db.flush()
    await db.refresh(program)
    return ProgramOut.model_validate(program)


# --- Features ---

@router.get("/{client_id}/features", response_model=list[FeatureOut])
async def list_features(
    client_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    stmt = select(Feature).where(Feature.client_id == client_id)
    result = await db.execute(stmt)
    return [FeatureOut.model_validate(f) for f in result.scalars().all()]


@router.post("/{client_id}/features", response_model=FeatureOut, status_code=status.HTTP_201_CREATED)
async def create_feature(
    client_id: UUID,
    body: FeatureCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    feature = Feature(**body.model_dump(), client_id=client_id)
    db.add(feature)
    await db.flush()
    await db.refresh(feature)
    return FeatureOut.model_validate(feature)


@router.put("/{client_id}/features/{feature_id}", response_model=FeatureOut)
async def update_feature(
    client_id: UUID,
    feature_id: UUID,
    body: FeatureUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Feature).where(Feature.id == feature_id, Feature.client_id == client_id)
    )
    feature = result.scalar_one_or_none()
    if feature is None:
        raise HTTPException(status_code=404, detail="Feature not found")
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(feature, key, val)
    await db.flush()
    await db.refresh(feature)
    return FeatureOut.model_validate(feature)

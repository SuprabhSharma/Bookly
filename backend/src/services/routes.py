import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.db.models import User, Vendor
from src.errors import InsufficientPermission, ServiceNotFound
from src.products.routes import get_approved_vendor

from .schemas import ServiceCreate, ServiceListOut, ServiceOut, ServiceUpdate
from .service import ServiceOfferingService

service_router = APIRouter()
service = ServiceOfferingService()


@service_router.get("", response_model=ServiceListOut)
async def list_services(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    vendor: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
):
    return await service.get_all(session, page=page, page_size=page_size, vendor_slug=vendor)


@service_router.get("/vendor/me", response_model=ServiceListOut)
async def vendor_list_services(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=100),
    vendor: Vendor = Depends(get_approved_vendor),
    session: AsyncSession = Depends(get_session),
):
    return await service.get_vendor_services(vendor.uid, session, page, page_size)


@service_router.post("/vendor/me", response_model=ServiceOut, status_code=status.HTTP_201_CREATED)
async def vendor_create_service(
    data: ServiceCreate,
    vendor: Vendor = Depends(get_approved_vendor),
    session: AsyncSession = Depends(get_session),
):
    return await service.create(vendor.uid, data, session)


@service_router.patch("/vendor/me/{uid}", response_model=ServiceOut)
async def vendor_update_service(
    uid: uuid.UUID,
    data: ServiceUpdate,
    vendor: Vendor = Depends(get_approved_vendor),
    session: AsyncSession = Depends(get_session),
):
    item = await service.get_by_id(uid, session)
    if not item:
        raise ServiceNotFound()
    if item.vendor_id != vendor.uid:
        raise InsufficientPermission()
    return await service.update(item, data, session)


@service_router.delete("/vendor/me/{uid}", status_code=status.HTTP_204_NO_CONTENT)
async def vendor_delete_service(
    uid: uuid.UUID,
    vendor: Vendor = Depends(get_approved_vendor),
    session: AsyncSession = Depends(get_session),
):
    item = await service.get_by_id(uid, session)
    if not item:
        raise ServiceNotFound()
    if item.vendor_id != vendor.uid:
        raise InsufficientPermission()
    await service.delete(item, session)

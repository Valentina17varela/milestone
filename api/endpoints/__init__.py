from fastapi import APIRouter

from api.endpoints import declaration

router = APIRouter()

router.include_router(
    declaration.router, prefix="/declarations", tags=["Anual Declaration"]
)

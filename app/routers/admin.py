from fastapi import APIRouter, Depends, HTTPException
from app.schemas import AdminCreate, Admin
from app.crud import create_admin
from app.routers.auth import get_current_superadmin
from app.models import Admin as AdminModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

router = APIRouter(tags=["admin"])

# Endpoint para crear un nuevo admin
@router.post("/", response_model=Admin)
async def create_new_admin(
    admin: AdminCreate,
    current_admin: Admin = Depends(get_current_superadmin)  # Dependencia para asegurar que el token es válido
):
    try:
        # Lógica para crear un nuevo admin, solo si el token es válido
        db_admin = await create_admin(admin)  # Llamamos a la función que crea el admin
        return db_admin
    except Exception as e:
        # Si ocurre un error durante la creación del admin, respondemos con un error detallado
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

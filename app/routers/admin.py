from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.schemas import AdminCreate, Admin
from app.crud import create_admin, get_admin_by_username
from app.routers.auth import get_current_superadmin, get_password_hash
from app.database import get_db 

router = APIRouter(tags=["admin"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def crear_nuevo_admin(
    admin: AdminCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_superadmin)
):
    """
    Crea un nuevo administrador (requiere privilegios de superadmin)
    """
    # Verificar si el username ya existe
    existing_admin = await get_admin_by_username(db, admin.username)
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está registrado"
        )

    try:
        hashed_password = get_password_hash(admin.password)
        db_admin_data = {
            "username": admin.username,
            "email": admin.email,
            "hashed_password": hashed_password,
            "is_superadmin": False,
            "is_active": True
        }
        db_admin = await create_admin(db, db_admin_data)
        
        # Convertir el objeto SQLAlchemy a diccionario correctamente
        admin_data = {
            "id": db_admin.id,
            "username": db_admin.username,
            "email": db_admin.email,
            "message": "creado exitosamente"
        }
        
        return admin_data
        
    except IntegrityError as e:
        await db.rollback()
        if "ix_admins_email" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está registrado"
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
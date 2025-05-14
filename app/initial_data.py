from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import create_admin, get_admin_by_username
from app.schemas import AdminCreate
from app.database import AsyncSessionLocal
from app.routers.auth import get_password_hash

async def create_initial_admin():
    async with AsyncSessionLocal() as db:
        try:
            # Verificar si ya existe el admin inicial
            existing_admin = await get_admin_by_username(db, "romez")
            if existing_admin:
                print("✔ El administrador inicial ya existe")
                return False
            
            # Crear el admin inicial
            admin_data = {
                "username": "romez",
                "email": "romez@example.com",
                "hashed_password": get_password_hash("20861681"),
                "is_superadmin": True,
                "is_active": True
            }
            
            await create_admin(db, admin_data)
            await db.commit()
            print("✔ Administrador inicial creado exitosamente")
            return True
        except Exception as e:
            await db.rollback()
            print(f"✖ Error al crear administrador inicial: {str(e)}")
            raise
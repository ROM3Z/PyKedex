# create_tables.py
import asyncio
from sqlalchemy import inspect
from app.database import engine, Base
from app.models import *

async def main():
    """
    Drops and recreates all database tables based on the current SQLAlchemy metadata.
    
    If tables already exist, lists them and prompts the user for confirmation before proceeding, warning that existing data will be deleted. Cancels the operation if not confirmed. Executes all operations asynchronously.
    """
    async with engine.begin() as conn:
        # Verificar tablas existentes
        inspector = inspect(conn)
        existing_tables = await conn.run_sync(
            lambda sync_conn: inspector.get_table_names()
        )
        
        if existing_tables:
            print("Tablas existentes:")
            for table in existing_tables:
                print(f"- {table}")
            
            confirm = input("¿Deseas recrear todas las tablas? (esto borrará los datos) [y/N]: ")
            if confirm.lower() != 'y':
                print("Operación cancelada")
                return

        print("Creando tablas...")
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        print("✔ Tablas recreadas exitosamente!")

if __name__ == "__main__":
    asyncio.run(main())
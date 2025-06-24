# create_tables.py
import asyncio
import inspect
from typing import List, Type
from sqlalchemy import inspect as sql_inspect
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.database import engine, Base
from app import models  # Asegúrate que todos los modelos estén importados aquí

async def get_all_models() -> List[Type[DeclarativeBase]]:
    """
    Detecta automáticamente todos los modelos SQLAlchemy en el módulo models.
    Devuelve una lista de clases de modelo válidas.
    """
    model_classes = []
    
    print("\n🔍 Buscando modelos en:", models.__file__)
    
    for name, obj in inspect.getmembers(models):
        try:
            if (inspect.isclass(obj) and 
                issubclass(obj, Base) and 
                obj != Base and
                hasattr(obj, '__tablename__')):
                print(f"✅ Modelo válido detectado: {name} (tabla: {obj.__tablename__})")
                model_classes.append(obj)
        except TypeError:
            continue
    
    if not model_classes:
        print("⚠️ ¡No se encontraron modelos válidos! Verifica que:")
        print("- Cada modelo herede de Base (de app.database)")
        print("- Cada modelo tenga definido __tablename__")
        print("- Los modelos estén importados en app/models/__init__.py")
    
    return model_classes

async def verify_database_connection(engine: AsyncEngine):
    """Verifica que la conexión a la base de datos funciona"""
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        print("✓ Conexión a la base de datos verificada")
        return True
    except Exception as e:
        print(f"✖ Error de conexión a la base de datos: {str(e)}")
        return False

async def create_all_tables(engine: AsyncEngine):
    """Crea todas las tablas definidas en los modelos"""
    async with engine.begin() as conn:
        print("\n🛠 Creando todas las tablas...")
        await conn.run_sync(Base.metadata.create_all)
        print("✓ Todas las tablas creadas exitosamente")

async def drop_all_tables(engine: AsyncEngine):
    """Elimina todas las tablas (¡CUIDADO! Pérdida de datos)"""
    async with engine.begin() as conn:
        print("\n⚠️ ELIMINANDO TODAS LAS TABLAS...")
        await conn.run_sync(Base.metadata.drop_all)
        print("✓ Todas las tablas eliminadas")

async def show_existing_tables(engine: AsyncEngine):
    """Muestra las tablas existentes en la base de datos"""
    async with engine.connect() as conn:
        inspector = sql_inspect(conn)
        tables = await conn.run_sync(lambda sync_conn: inspector.get_table_names())
        print("\n📊 Tablas existentes en la base de datos:")
        for table in tables:
            print(f" - {table}")
        return tables

async def main():
    print("\n=== 🚀 Script de Creación de Tablas SQLAlchemy ===")
    
    # 1. Verificar conexión a la base de datos
    if not await verify_database_connection(engine):
        return
    
    # 2. Obtener todos los modelos
    all_models = await get_all_models()
    if not all_models:
        return
    
    # 3. Mostrar tablas existentes
    existing_tables = await show_existing_tables(engine)
    
    # 4. Menú de opciones
    print("\n🔧 Opciones disponibles:")
    print("1. Crear tablas faltantes (sin afectar existentes)")
    print("2. Recrear TODAS las tablas (¡elimina datos existentes!)")
    print("3. Solo mostrar información (no hacer cambios)")
    
    choice = input("\nSeleccione una opción (1-3): ").strip()
    
    if choice == "1":
        await create_all_tables(engine)
    elif choice == "2":
        confirm = input("⚠️ ¿ESTÁ SEGURO? Esto eliminará TODAS las tablas y datos. (s/N): ")
        if confirm.lower() == 's':
            await drop_all_tables(engine)
            await create_all_tables(engine)
        else:
            print("Operación cancelada")
    else:
        print("Solo mostrando información (no se hicieron cambios)")
    
    # Mostrar estado final
    await show_existing_tables(engine)
    print("\n✔ Proceso completado")

if __name__ == "__main__":
    asyncio.run(main())
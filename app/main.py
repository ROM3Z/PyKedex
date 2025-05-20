# app/main.py
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncEngine

# Importaciones de tu aplicación
from app.database import engine, Base
from app.routers import pokemon, trainer, battle, auth, admin
from app.initial_data import create_initial_admin
from app.models import *

# --------------------------------------------------
# CONFIGURACIÓN DEL RATE LIMITER
# --------------------------------------------------
limiter = Limiter(key_func=get_remote_address)

# --------------------------------------------------
# CONFIGURACIÓN DE LA APLICACIÓN
# --------------------------------------------------
bearer_scheme = HTTPBearer()

app = FastAPI(
    title="PyKedex API",
    description="API para el sistema de gestión de Pokémon y batallas",
    version="1.0.0",
    contact={
        "name": "Equipo de Desarrollo DruidCode By ROMEZ",
        "email": "isaac.rod33@gmail.com"
    },
    license_info={
        "name": "MIT",
    }
)

# --------------------------------------------------
# FUNCIONES DE INICIALIZACIÓN
# --------------------------------------------------
async def check_tables_exist(engine: AsyncEngine) -> bool:
    """Verifica si las tablas principales existen en la base de datos"""
    async with engine.connect() as conn:
        # Usamos run_sync para ejecutar la inspección de forma síncrona
        existing_tables = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_table_names()
        )
        required_tables = {"admins", "pokemons", "trainers", "trainer_pokemons", "battles"}
        return all(table in existing_tables for table in required_tables)

async def initialize_database():
    """Inicializa la base de datos creando tablas si no existen"""
    try:
        tables_exist = await check_tables_exist(engine)
        if not tables_exist:
            print("⚠ Tablas no encontradas, creando estructura de base de datos...")
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("✔ Base de datos inicializada correctamente")
        else:
            print("✔ Tablas ya existen en la base de datos")
    except Exception as e:
        print(f"✖ Error al inicializar la base de datos: {e}")
        raise

# --------------------------------------------------
# EVENTOS DE LA APLICACIÓN
# --------------------------------------------------
@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación"""
    await initialize_database()
    await create_initial_admin()
    print("✔ Verificado/Creado administrador inicial")

# --------------------------------------------------
# MIDDLEWARES
# --------------------------------------------------
app.add_middleware(SlowAPIMiddleware)
app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# MANEJADORES DE ERRORES
# --------------------------------------------------
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "message": "Ha superado el límite de 10 solicitudes por minuto. Por favor espere.",
            "success": False,
            "error": "RateLimitExceeded"
        },
        headers={
            "Retry-After": str(60)
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.detail,
            "success": False,
            "error": type(exc).__name__
        }
    )

# --------------------------------------------------
# RUTAS PRINCIPALES
# --------------------------------------------------
@app.get("/", tags=["Inicio"])
async def root():
    return {
        "message": "¡Bienvenido a PyKedex!",
        "documentación": "/docs",
        "versión": "1.0.0",
        "rutas_disponibles": {
            "pokemons": "/api/v1/pokemons",
            "entrenadores": "/api/v1/entrenadores",
            "batallas": "/api/v1/batallas"
        }
    }

# --------------------------------------------------
# INCLUSIÓN DE ROUTERS
# --------------------------------------------------
# Configuración de rate limits para cada router
routers_config = [
    (admin.router, "10/minute", "admin", "/api/v1/admin", "admin"),
    (auth.router, "10/minute", "auth", "/api/v1/auth", "auth"),
    (pokemon.router, "10/minute", "pokemon", "/api/v1/pokemons", "Pokémon"),
    (trainer.router, "10/minute", "trainer", "/api/v1/entrenadores", "Entrenadores"),
    (battle.router, "10/minute", "battle", "/api/v1/batallas", "Batallas"),
]

for router, rate_limit, scope, prefix, tags in routers_config:
    router.dependencies = [Depends(limiter.shared_limit(rate_limit, scope=scope))]
    app.include_router(router, prefix=prefix, tags=[tags])

# --------------------------------------------------
# CONFIGURACIÓN OPENAPI
# --------------------------------------------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
from fastapi import FastAPI, Request, Depends
from app.database import engine, Base
from app.routers import pokemon, trainer, battle, auth, admin
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.initial_data import create_initial_admin
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel, SecurityScheme as SecuritySchemeModel
from fastapi.security import OAuth2PasswordBearer

# --------------------------------------------------
# CONFIGURACIÓN DEL RATE LIMITER
# --------------------------------------------------

limiter = Limiter(key_func=get_remote_address)

# --------------------------------------------------
# CONFIGURACIÓN DE LA APLICACIÓN
# --------------------------------------------------

# Crear el esquema OAuth2 para usar Bearer tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

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

# Añade el middleware de rate limiting
app.add_middleware(SlowAPIMiddleware)

# Configura el rate limiter
app.state.limiter = limiter

# Evento de startup para crear admin inicial
@app.on_event("startup")
async def startup_event():
    await create_initial_admin()
    print("✔ Verificado/Creado administrador inicial")

# --------------------------------------------------
# MANEJADOR DE ERRORES PARA RATE LIMIT
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
            "Retry-After": str(60)  # Indica cuántos segundos esperar (60 = 1 minuto)
        }
    )

# --------------------------------------------------
# REGISTRO DE ROUTERS CON RATE LIMITING
# --------------------------------------------------

admin.router.dependencies = [Depends(limiter.shared_limit("10/minute", scope="admin"))]
app.include_router(
    admin.router,
    prefix="/api/v1/admin",
    tags=["admin"]
)

auth.router.dependencies = [Depends(limiter.shared_limit("10/minute", scope="auth"))]
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["auth"]
)

# Router de Pokémon con rate limiting
pokemon.router.dependencies = [Depends(limiter.shared_limit("10/minute", scope="pokemon"))]
app.include_router(
    pokemon.router,
    prefix="/api/v1/pokemons",
    tags=["Pokémon"]
)

# Router de Entrenadores con rate limiting
trainer.router.dependencies = [Depends(limiter.shared_limit("10/minute", scope="trainer"))]
app.include_router(
    trainer.router,
    prefix="/api/v1/entrenadores",
    tags=["Entrenadores"]
)

# Router de Batallas con rate limiting
battle.router.dependencies = [Depends(limiter.shared_limit("10/minute", scope="battle"))]
app.include_router(
    battle.router,
    prefix="/api/v1/batallas",
    tags=["Batallas"]
)

# --------------------------------------------------
# ENDPOINTS BÁSICOS (SIN RATE LIMITING)
# --------------------------------------------------

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Base de datos inicializada correctamente")

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
# CONFIGURACIÓN ADICIONAL
# --------------------------------------------------

# Middleware para CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manejador de excepciones generales
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

# Personalización de OpenAPI para incluir el esquema de seguridad globalmente
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
    # Aplica BearerAuth globalmente a todos los endpoints
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            operation["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Cambiar el OpenAPI de FastAPI para que use Bearer Token por defecto
app.openapi = custom_openapi

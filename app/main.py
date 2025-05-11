from fastapi import FastAPI, Request, Depends
from app.database import engine, Base
from app.routers import pokemon, trainer, battle
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# --------------------------------------------------
# CONFIGURACIÓN DEL RATE LIMITER
# --------------------------------------------------

limiter = Limiter(key_func=get_remote_address)

# --------------------------------------------------
# CONFIGURACIÓN DE LA APLICACIÓN
# --------------------------------------------------

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
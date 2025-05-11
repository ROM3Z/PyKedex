from fastapi import FastAPI
from app.database import engine, Base  # Importa la configuración de la base de datos
from app.routers import pokemon, trainer, battle  # Importa los routers de cada módulo
import asyncio

# --------------------------------------------------
# CONFIGURACIÓN INICIAL DE LA APLICACIÓN
# --------------------------------------------------

# Crea la instancia principal de FastAPI
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
# REGISTRO DE ROUTERS (ENDPOINTS)
# --------------------------------------------------

# Incluye los routers para cada módulo con prefijos y etiquetas específicas
app.include_router(
    pokemon.router,
    prefix="/api/v1/pokemons",  # Cambia el prefijo para los pokémons
    # para evitar conflictos con el prefijo de Entrenadores
    tags=["Pokémon"]
)

app.include_router(
    trainer.router,
    prefix="/api/v1/entrenadores",  # Cambia el prefijo para los entrenadores
    # para evitar conflictos con el prefijo de Pokémon
    tags=["Entrenadores"]
)

app.include_router(
    battle.router,
    prefix="/api/v1/batallas",  # Cambia el prefijo para las batallas
    # para evitar conflictos con el prefijo de Pokémon
    # y para mantener una estructura clara en la API
    tags=["Batallas"]
)

# --------------------------------------------------
# EVENTOS DE LA APLICACIÓN
# --------------------------------------------------

@app.on_event("startup")
async def startup():
    """
    Evento que se ejecuta al iniciar la aplicación.
    Crea todas las tablas en la base de datos si no existen.
    """
    async with engine.begin() as conn:
        # Crea todas las tablas definidas en los modelos SQLAlchemy
        await conn.run_sync(Base.metadata.create_all)
        
        # Mensaje de confirmación en logs
        print("Base de datos inicializada correctamente")
    
    # Aquí podrías añadir más lógica de inicialización si es necesario
    # como cargar datos iniciales, configurar conexiones externas, etc.

# --------------------------------------------------
# ENDPOINT RAIZ
# --------------------------------------------------

@app.get("/", tags=["Inicio"])
async def root():
    """
    Endpoint raíz que provee un mensaje de bienvenida.
    
    Returns:
        dict: Mensaje de bienvenida en formato JSON
    """
    return {
        "message": "¡Bienvenido a PyKedex!",
        "documentación": "/docs",
        "versión": "1.0.0",
        "rutas_disponibles": {
            "pokemons": "/api/v1/pokemons",
            "entrenadores": "/api/v1/trainers",
            "batallas": "/api/v1/battles"
        }
    }

# --------------------------------------------------
# CONFIGURACIÓN ADICIONAL (OPCIONAL)
# --------------------------------------------------

# Ejemplo de middleware para manejar CORS (si se necesita)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ejemplo de manejo de excepciones personalizadas
from fastapi import HTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.detail,
            "success": False,
            "error": type(exc).__name__
        }
    )
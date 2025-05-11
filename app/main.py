from fastapi import FastAPI
from app.database import engine, Base
from app.routers import pokemon, trainer, battle  # Asegúrate que estos routers existan
import asyncio

app = FastAPI()

# Incluye los routers
app.include_router(pokemon.router)
app.include_router(trainer.router)
app.include_router(battle.router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "¡Muy pronto PyKedex!"}
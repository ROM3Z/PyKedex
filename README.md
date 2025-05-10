# PyKedex - API Pokémon con FastAPI

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68.0-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13-blue.svg)

**Autor:** Isaac Rodríguez ROMEZ  
**Desarrollado para:** Curso PyKedex de DruidCode

## Descripción del Proyecto

PyKedex es una API RESTful inspirada en el universo Pokémon, diseñada como proyecto educativo para el curso de DruidCode. Implementa un sistema completo para gestionar entrenadores, pokémons y simular emocionantes batallas.

## Características Técnicas

- **Arquitectura**: API REST con FastAPI
- **Base de Datos**: PostgreSQL con SQLAlchemy ORM
- **Autenticación**: JWT (próximamente)
- **Operaciones CRUD** completas para todos los modelos
- **Sistema de batallas** por turnos con cálculo de daño
- **Documentación automática** con Swagger UI y ReDoc

## Estructura del Código

```
app/
├── crud.py          # Operaciones de base de datos
├── database.py      # Configuración de DB
├── models.py        # Modelos SQLAlchemy
├── schemas.py       # Esquemas Pydantic
├── routers/
│   ├── pokemon.py   # Endpoints de Pokémon
│   ├── trainer.py   # Endpoints de Entrenadores
│   └── battle.py    # Lógica de batallas
└── main.py          # Aplicación principal
```

## Ejemplos de Uso

### Crear un Pokémon
```python
POST /pokemons
{
    "name": "Pikachu",
    "element": "Eléctrico",
    "hp": 35,
    "attack": 55,
    "defense": 40,
    "moves": ["Impactrueno", "Rayo", "Ataque Rápido"]
}
```

### Simular una Batalla
```python
POST /battles
{
    "trainer_id": 1,
    "opponent_id": 2
}

# Respuesta de ejemplo
{
    "winner_name": "Ash",
    "battle_log": [
        "Pikachu ataca a Squirtle y causa 12 de daño",
        "Squirtle ataca a Pikachu y causa 8 de daño",
        "¡Squirtle se debilitó!"
    ]
}
```

## Requisitos e Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Configurar PostgreSQL en `.env`:
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/pykedex
```

3. Ejecutar la aplicación:
```bash
uvicorn app.main:app --reload
```

## Documentación Interactiva

Accede a la documentación completa en:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Notas del Autor

Este proyecto fue desarrollado como parte del curso PyKedex de DruidCode, con el objetivo de aprender:
- Desarrollo de APIs con FastAPI
- Operaciones asíncronas con bases de datos
- Patrones de diseño para aplicaciones web
- Sistemas de batallas por turnos

**¡Atrapa todos los endpoints!**

# PyKedex - API Pokémon con FastAPI 🚀

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens)

API REST inspirada en Pokémon construida con FastAPI, PostgreSQL y autenticación JWT. Desarrollado como proyecto educativo para el curso PyKedex de DruidCode.

## Características ✨

- **Operaciones CRUD completas** para Pokémon, Entrenadores y Batallas
- **Autenticación JWT** con roles de admin/superadmin
- **Sistema de batallas por turnos** con cálculo de daño
- **Operaciones asíncronas** con SQLAlchemy y PostgreSQL
- **Documentación automática** con Swagger UI y ReDoc
- **Preparado para producción** con seguridad y validaciones

## Estructura del Proyecto 📂

```
app/
├── routers/
│   ├── admin.py       # Endpoints de administración
│   ├── auth.py        # Autenticación JWT
│   ├── battle.py      # Lógica de batallas
│   ├── pokemon.py     # Endpoints de Pokémon
│   └── trainer.py     # Endpoints de Entrenadores
├── crud.py            # Operaciones de base de datos
├── database.py        # Configuración de DB
├── initial_data.py    # Cargador de datos iniciales
├── main.py            # Aplicación principal
├── models.py          # Modelos SQLAlchemy
└── schemas.py         # Esquemas Pydantic
```

## Instalación ⚙️

1. Clona el repositorio:
```bash
git clone https://github.com/tuusuario/pykedex-api.git
cd pykedex-api
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Configura las variables de entorno en `.env`:
```ini
DATABASE_URL=postgresql+asyncpg://usuario:contraseña@localhost:5432/pykedex
SECRET_KEY=tu-clave-secreta-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

4. Ejecuta la aplicación:
```bash
uvicorn app.main:app --reload
```

## Documentación de la API 📚

Una vez en funcionamiento, accede a la documentación interactiva:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Ejemplos de Uso 🎮

### Autenticación
```http
POST /token
Content-Type: application/json

{
    "username": "admin",
    "password": "secreto"
}
```

### Crear un Pokémon (requiere autenticación)
```http
POST /pokemons
Authorization: Bearer <tu-token>
Content-Type: application/json

{
    "name": "Pikachu",
    "element": "Eléctrico",
    "hp": 35,
    "attack": 55,
    "defense": 40,
    "moves": ["Impactrueno", "Ataque Rápido"]
}
```

### Simular una Batalla
```http
POST /battles
Authorization: Bearer <tu-token>
Content-Type: application/json

{
    "trainer_id": 1,
    "opponent_id": 2
}
```

## Contribuciones 🤝

¡Las contribuciones son bienvenidas! Abre un issue o envía un pull request.

## Licencia 📜

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

---

**Desarrollado por Isaac Rodríguez ROMEZ**  
**Para el Curso PyKedex de DruidCode**  

"¡Atrápalos ya!" - Pokémon
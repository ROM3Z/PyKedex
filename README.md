# PyKedex - API Pokémon con FastAPI 🚀

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens)

API REST inspirada en Pokémon construida con FastAPI, PostgreSQL y autenticación JWT. Desarrollado como proyecto educativo para el curso PyKedex de DruidCode.

## Características ✨

- **Operaciones CRUD completas** para Pokémon, Entrenadores y Batallas
- **Autenticación JWT** con roles de admin/superadmin
- **Sistema de batallas por turnos avanzado** con:
  - Cálculo de daño 4x/0.25x para múltiples debilidades/resistencias
  - Selección inteligente de Pokémon basada en ventajas de tipo y estadísticas
  - Gestión de Pokémon derrotados (no pueden volver a combatir)
- **Operaciones asíncronas** con SQLAlchemy y PostgreSQL
- **Documentación automática** con Swagger UI y ReDoc
- **Preparado para producción** con seguridad y validaciones

## Mejoras Recientes 🚀

### Sistema de Batallas
- **Daño 4x/0.25x**: Cálculo preciso de múltiples debilidades/resistencias
- **Selección inteligente**: Los entrenadores eligen Pokémon estratégicamente
- **Diálogos mejorados**: Mensajes especiales para combates extremos
- **MVP**: Identificación del Pokémon más valioso en cada batalla

### Base de Datos
- **Gestión asíncrona mejorada**: Creación y verificación de tablas
- **Pool de conexiones optimizado**: Mejor manejo de conexiones concurrentes
- **Sesiones mejoradas**: Limpieza automática de recursos

### Seguridad
- **Middleware reforzado**: Protección adicional para endpoints
- **Manejo de errores**: Respuestas estructuradas para excepciones
- **OpenAPI actualizado**: Documentación de seguridad mejorada

## Estructura del Proyecto 📂

```
app/
├── routers/
│   ├── admin.py       # Endpoints de administración
│   ├── auth.py        # Autenticación JWT
│   ├── battle.py      # Lógica avanzada de batallas
│   ├── pokemon.py     # Endpoints de Pokémon
│   └── trainer.py     # Endpoints de Entrenadores
├── crud.py            # Operaciones de base de datos
├── database.py        # Configuración mejorada de DB
├── create_tables.py   # Script para gestión de tablas
├── initial_data.py    # Cargador de datos iniciales
├── main.py            # Aplicación principal mejorada
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

4. (Opcional) Crea las tablas:
```bash
python app/create_tables.py
```

5. Ejecuta la aplicación:
```bash
uvicorn app.main:app --reload
```

## Documentación de la API 📚

Una vez en funcionamiento, accede a la documentación interactiva:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Ejemplo de Batalla Mejorada ⚔️

```http
POST /battles
Authorization: Bearer <tu-token>
Content-Type: application/json

{
    "trainer_id": 1,
    "opponent_id": 2,
    "smart_selection": true  # Activa selección inteligente de Pokémon
}
```

Respuesta incluye:
- Turnos detallados con efectividad de ataques (x4, x2, x0.5, x0.25)
- MVP de la batalla (Pokémon más valioso)
- Pokémon derrotados que no podrán volver a combatir

## Contribuciones 🤝

¡Las contribuciones son bienvenidas! Abre un issue o envía un pull request.

## Licencia 📜

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

---

**Desarrollado por Isaac Rodríguez ROMEZ**  
**Para el Curso PyKedex de DruidCode**  

"¡Los combates Pokémon ahora son más estratégicos que nunca!"

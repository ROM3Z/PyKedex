from datetime import datetime, timedelta
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Admin
from app.database import get_db

# Configuración (debes mover esto a variables de entorno)
SECRET_KEY = "PykedexSecretKey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(tags=["auth"])

# Modelos
class Token(BaseModel):
    access_token: str
    token_type: str

class LoginForm(BaseModel):
    username: str
    password: str

# Utilidades
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()

# Función para verificar contraseña
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Función para generar hash de contraseña
def get_password_hash(password: str):
    return pwd_context.hash(password)

# Función para crear token de acceso
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Función para autenticar admin
async def authenticate_admin(
    username: str, 
    password: str,
    db: AsyncSession = Depends(get_db)
):
    from app.crud import get_admin_by_username
    admin = await get_admin_by_username(db, username)
    if not admin:
        return False
    if not verify_password(password, admin.hashed_password):
        return False
    return admin

# Endpoint para obtener token
@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: LoginForm,
    db: AsyncSession = Depends(get_db)
):
    admin = await authenticate_admin(form_data.username, form_data.password, db)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Dependencia para obtener el admin actual
async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        from app.crud import get_admin_by_username
        admin = await get_admin_by_username(db, username=username)
        if admin is None:
            raise credentials_exception
        return admin
    except JWTError:
        raise credentials_exception

# Dependencia para obtener admin superusuario
async def get_current_superadmin(
    current_admin: Admin = Depends(get_current_admin)
):
    if not current_admin.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_admin
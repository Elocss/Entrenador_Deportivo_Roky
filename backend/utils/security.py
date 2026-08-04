import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("roky.security")

security_scheme = HTTPBearer()

def crear_token_acceso(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Genera un token JWT con expiración."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verificar_token_acceso(token: str) -> Optional[dict]:
    """Valida un token JWT. Retorna el payload decodificado o None si es inválido/expirado."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("El token JWT ha expirado.")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Token JWT inválido: {e}")
        return None

def obtener_usuario_actual(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> Dict:
    """
    Dependencia de FastAPI para proteger rutas.
    Verifica que la cabecera contenga un token Bearer válido.
    """
    token = credentials.credentials
    payload = verificar_token_acceso(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado. Autenticación requerida.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

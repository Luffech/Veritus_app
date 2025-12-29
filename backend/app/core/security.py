from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# Configura o algoritmo bcrypt para realizar o hashing seguro das senhas.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Gera um token JWT assinado contendo o ID do usuário e o tempo de expiração.
def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# Verifica se a senha em texto plano corresponde ao hash armazenado.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Gera o hash criptografado da senha para ser armazenado no banco de dados.
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
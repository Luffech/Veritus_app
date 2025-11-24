from passlib.context import CryptContext

# Configura o contexto do Passlib para usar bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se uma senha em texto puro corresponde ao hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera um hash seguro a partir de uma senha em texto puro."""
    return pwd_context.hash(password)
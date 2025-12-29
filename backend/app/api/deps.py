from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload 

from app.core.config import settings
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.token import TokenPayload

# Avisa pro FastAPI que o token vem do header Authorization e qual url gera ele.
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login"
)

# A mágica acontece aqui: valida o token e retorna o objeto Usuário para a rota usar.
async def get_current_user(
    token: Annotated[str, Depends(reusable_oauth2)],
    db: AsyncSession = Depends(get_db)
) -> Usuario:
    
    # Deixa o erro de "Não Autorizado" pronto pra disparar se algo der errado.
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Tenta decodificar o JWT usando nossa chave secreta.
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        
        # Extrai o ID do usuário (sub) de dentro do payload.
        user_id_str: Optional[str] = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        
        try:
            user_id = int(user_id_str)
        except ValueError:
             raise credentials_exception
             
        token_data = TokenPayload(sub=user_id)
        
    except JWTError:
        # Se o token estiver expirado ou inválido, cai aqui.
        raise credentials_exception

    # Busca o usuário no banco já carregando o nível de acesso (pra evitar queries extras depois).
    query = select(Usuario).options(selectinload(Usuario.nivel_acesso)).where(Usuario.id == token_data.sub)
    result = await db.execute(query)
    user = result.scalars().first()

    # Checagens finais de segurança: usuário existe? está ativo?
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
    if not user.ativo:
        raise HTTPException(status_code=400, detail="Usuário inativo")
        
    return user
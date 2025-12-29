from datetime import timedelta
from typing import Any
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db 
from app.models.usuario import Usuario
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.schemas.token import Token

# Inicializa o roteador para agrupar os endpoints de login.
router = APIRouter()

# Endpoint POST para autenticar o usuário e retornar o token de acesso JWT.
@router.post("/", response_model=Token, summary="Login e Geração de Token")
async def login_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    
    # Busca o usuário no banco pelo email carregando junto o nível de acesso.
    query = select(Usuario).options(selectinload(Usuario.nivel_acesso)).where(Usuario.email == form_data.username)
    result = await db.execute(query)
    user = result.scalars().first()

    # Valida se o usuário existe, se a senha confere e se a conta está ativa.
    if not user or not verify_password(form_data.password, user.senha_hash):
         raise HTTPException(status_code=401, detail="Email ou senha incorretos")

    if not user.ativo:
         raise HTTPException(status_code=403, detail="Usuário inativo")

    # Define o tempo de expiração e cria o token JWT assinado com os dados do usuário.
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.nivel_acesso.nome, "email": user.email},
        expires_delta=access_token_expires
    )

    # Retorna o token gerado e as informações básicas do usuário autenticado.
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.email,
        "nome": user.nome,          
        "role": user.nivel_acesso.nome
    }
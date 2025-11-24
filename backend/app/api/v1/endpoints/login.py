from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import AsyncSessionLocal
from app.models.usuario import Usuario
from app.core.security import verify_password # <--- IMPORTANTE

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

async def get_db():
    async with AsyncSessionLocal() as db:
        yield db

@router.post("/login", summary="Login Real (DB)")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    # Busca usuário e carrega o nível de acesso junto (selectinload)
    query = select(Usuario).options(selectinload(Usuario.nivel_acesso)).where(Usuario.email == data.username)
    result = await db.execute(query)
    user = result.scalars().first()

    # VERIFICAÇÃO SEGURA COM HASH
    if not user or not verify_password(data.password, user.senha_hash):
         raise HTTPException(status_code=401, detail="Credenciais inválidas")

    if not user.ativo:
         raise HTTPException(status_code=403, detail="Usuário inativo")

    return {
        "access_token": f"fake-jwt-{user.id}", # Num futuro próximo implementaremos JWT real aqui
        "token_type": "bearer",
        "role": user.nivel_acesso.nome,
        "username": user.email
    }
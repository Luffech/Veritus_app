from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError # <--- IMPORTANTE: Adicione este import
from typing import Sequence, Optional
from fastapi import HTTPException

from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.core.security import get_password_hash

class UsuarioService:
    def __init__(self, db: AsyncSession):
        self.repo = UsuarioRepository(db)

    async def get_all_usuarios(self) -> Sequence[Usuario]:
        return await self.repo.get_all_usuarios()

    async def get_usuario_by_id(self, usuario_id: int) -> Optional[Usuario]:
        return await self.repo.get_usuario_by_id(usuario_id)

    async def create_usuario(self, usuario_data: UsuarioCreate) -> Usuario:
        # Pré-verificação (já existia, mas vamos reforçar com try/catch no insert real)
        if await self.repo.get_usuario_by_email(usuario_data.email):
             raise HTTPException(status_code=400, detail="Email já cadastrado.")

        db_usuario = Usuario(
            nome=usuario_data.nome,
            email=usuario_data.email,
            senha_hash=get_password_hash(usuario_data.senha),
            nivel_acesso_id=usuario_data.nivel_acesso_id,
            ativo=usuario_data.ativo
        )
        
        try:
            return await self.repo.create_usuario(db_usuario)
        except IntegrityError as e:
            # Se o erro for violação de unicidade (email duplicado que passou na pré-verificação por alguma razão de concorrência)
            if "ix_usuarios_email" in str(e.orig):
                raise HTTPException(status_code=409, detail="Este email já está em uso por outro utilizador.")
            # Outro erro de integridade qualquer
            raise HTTPException(status_code=400, detail="Erro de integridade na base de dados.")
        except Exception as e:
            # Erro genérico para não vazar detalhes sensíveis, mas logamos no console
            print(f"Erro inesperado ao criar usuário: {e}")
            raise HTTPException(status_code=500, detail="Erro interno ao criar utilizador.")

    async def update_usuario(self, usuario_id: int, usuario_data: UsuarioUpdate) -> Optional[Usuario]:
        update_dict = usuario_data.model_dump(exclude_unset=True)
        if 'senha' in update_dict:
            update_dict['senha_hash'] = get_password_hash(update_dict.pop('senha'))
        
        try:
            return await self.repo.update_usuario(usuario_id, update_dict)
        except IntegrityError as e:
            if "ix_usuarios_email" in str(e.orig):
                 raise HTTPException(status_code=409, detail="Este email já está em uso.")
            raise e

    async def delete_usuario(self, usuario_id: int) -> bool:
        return await self.repo.delete_usuario(usuario_id)
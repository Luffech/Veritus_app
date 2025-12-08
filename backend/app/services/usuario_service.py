from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import Sequence, Optional
from fastapi import HTTPException
from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from app.core.security import get_password_hash

class UsuarioService:
    def __init__(self, db: AsyncSession):
        self.repo = UsuarioRepository(db)

    async def get_all_usuarios(self, ativo: Optional[bool] = None) -> Sequence[UsuarioResponse]:
        db_usuarios = await self.repo.get_all_usuarios(ativo) 
        return [UsuarioResponse.model_validate(u) for u in db_usuarios]
    
    async def get_usuario_by_id(self, usuario_id: int) -> Optional[UsuarioResponse]:
        db_usuarios = await self.repo.get_usuario_by_id(usuario_id)
        if db_usuarios:
            return UsuarioResponse.model_validate(db_usuarios)
        return None

    async def create_usuario(self, usuario_data: UsuarioCreate) -> UsuarioResponse:
        # Validate Uniqueness
        if await self.repo.get_usuario_by_email(usuario_data.email):
             raise HTTPException(status_code=400, detail="Email já cadastrado.")

        if usuario_data.username and await self.repo.get_usuario_by_username(usuario_data.username):
            raise HTTPException(status_code=400, detail=f"O ID de usuário '{usuario_data.username}' já está em uso.")

        db_usuario = Usuario(
            nome=usuario_data.nome,
            username=usuario_data.username,
            email=usuario_data.email,
            senha_hash=get_password_hash(usuario_data.senha),
            nivel_acesso_id=usuario_data.nivel_acesso_id,
            ativo=usuario_data.ativo
        )
        
        try:
            novo_usuario_db = await self.repo.create_usuario(db_usuario)
            return UsuarioResponse.model_validate(novo_usuario_db)
        except IntegrityError as e:
            await self.repo.db.rollback()
            if "username" in str(e):
                raise HTTPException(status_code=409, detail="ID de usuário já existente.")
            if "email" in str(e):
                raise HTTPException(status_code=409, detail="Email já existente.")
            raise HTTPException(status_code=400, detail="Erro de integridade na base de dados.")
        except Exception as e:
            await self.repo.db.rollback()
            raise HTTPException(status_code=500, detail="Erro interno ao criar utilizador.")

    async def update_usuario(self, usuario_id: int, usuario_data: UsuarioUpdate) -> Optional[UsuarioResponse]:
        update_user = usuario_data.model_dump(exclude_unset=True)
        
        if 'senha' in update_user:
            update_user['senha_hash'] = get_password_hash(update_user.pop('senha'))
        else:
            update_user.pop('senha', None)

        if not update_user:
            raise HTTPException(status_code=400, detail="Nenhum dado fornecido para atualização.")

        if 'username' in update_user and update_user['username']:
            existente = await self.repo.get_usuario_by_username(update_user['username'])
            if existente and existente.id != usuario_id:
                raise HTTPException(status_code=400, detail=f"O ID '{update_user['username']}' já pertence a outro utilizador.")

        try:
            usuario_atualizado_db = await self.repo.update_usuario(usuario_id, update_user)
            if usuario_atualizado_db:
                return UsuarioResponse.model_validate(usuario_atualizado_db)
            return None
        except IntegrityError as e:
            await self.repo.db.rollback()
            if "username" in str(e):
                 raise HTTPException(status_code=409, detail="ID de usuário já em uso.")
            if "email" in str(e):
                 raise HTTPException(status_code=409, detail="Este email já está em uso.")
            raise HTTPException(status_code=400, detail="Erro de integridade.")
        except Exception as e:
            await self.repo.db.rollback()
            raise HTTPException(status_code=500, detail="Erro interno ao atualizar.")

    async def delete_usuario(self, usuario_id: int) -> bool:
        usuario_alvo = await self.repo.get_usuario_by_id(usuario_id)        
        if not usuario_alvo:
            return False 
        
        # Protected Rule: Admin users cannot be deleted
        if usuario_alvo.nivel_acesso and usuario_alvo.nivel_acesso.nome == 'admin':
            raise HTTPException(status_code=403, detail="Ação negada: Não é permitido excluir administradores.")

        try:
            return await self.repo.delete_usuario(usuario_id)
        except IntegrityError:
            await self.repo.db.rollback() 
            raise HTTPException(
                status_code=409, 
                detail="Não é possível excluir este utilizador pois ele possui registos vinculados."
            )
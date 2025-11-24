# backend/app/repositories/usuario_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete
from typing import Sequence, Optional

from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate

class UsuarioRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_usuario(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        await self.db.commit()
        await self.db.refresh(usuario)
        return await self.get_usuario_by_id(usuario.id)

    async def get_all_usuarios(self) -> Sequence[Usuario]:
        query = select(Usuario).options(selectinload(Usuario.nivel_acesso))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_usuario_by_id(self, usuario_id: int) -> Optional[Usuario]:
        # Confirme se esta linha tem o .options(selectinload(...))
        query = select(Usuario).options(selectinload(Usuario.nivel_acesso)).where(Usuario.id == usuario_id)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_usuario_by_email(self, email: str) -> Optional[Usuario]:
         # Usamos options(selectinload(...)) para manter consistência, 
         # embora para a verificação de existência não fosse estritamente necessário.
         query = select(Usuario).options(selectinload(Usuario.nivel_acesso)).where(Usuario.email == email)
         result = await self.db.execute(query)
         return result.scalars().first()

    async def update_usuario(self, usuario_id: int, update_data: dict) -> Optional[Usuario]:
        # 1. Executa a atualização no banco
        # Usa 'update_data' que foi recebido como argumento
        query = (
            sqlalchemy_update(Usuario)
            .where(Usuario.id == usuario_id)
            .values(**update_data) 
            .returning(Usuario.id)
        )
        result = await self.db.execute(query)
        await self.db.commit()
        
        # 2. Obtém o ID do registo atualizado
        updated_id = result.scalars().first()
        
        # 3. Se encontrou, recarrega o objeto completo com os relacionamentos
        if updated_id:
             return await self.get_usuario_by_id(updated_id)
             
        return None

    async def delete_usuario(self, usuario_id: int) -> bool:
        query = sqlalchemy_delete(Usuario).where(Usuario.id == usuario_id)
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0
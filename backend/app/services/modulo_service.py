from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from typing import Sequence, Optional
from app.models import Modulo
from app.repositories.modulo_repository import ModuloRepository
from app.schemas import ModuloCreate, ModuloUpdate

class ModuloService:
    def __init__(self, db: AsyncSession):
        self.repo = ModuloRepository(db)

    async def create_modulo(self, modulo_data: ModuloCreate) -> Modulo:
        return await self.repo.create_modulo(modulo_data)

    async def get_all_modulos(self) -> Sequence[Modulo]:
        return await self.repo.get_all_modulos()

    async def get_modulo_by_id(self, modulo_id: int) -> Optional[Modulo]:
        return await self.repo.get_modulo_by_id(modulo_id)
    
    async def update_modulo(self, modulo_id: int, modulo_data: ModuloUpdate) -> Optional[Modulo]:
        return await self.repo.update_modulo(modulo_id, modulo_data)

    async def delete_modulo(self, modulo_id: int) -> bool:
        try:
            return await self.repo.delete_modulo(modulo_id)
        except IntegrityError:
            await self.repo.db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Não é possível excluir este módulo pois ele possui Projetos vinculados."
            )
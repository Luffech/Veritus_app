from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence, Optional

from app.models import Modulo
from app.repositories.modulo_repository import ModuloRepository
from app.schemas import ModuloCreate, ModuloUpdate

class ModuloService:
    def __init__(self, db: AsyncSession):
        self.repo = ModuloRepository(db)

    async def create_modulo(self, modulo_data: ModuloCreate) -> Modulo:
        # Aqui você poderia adicionar validações, como por exemplo:
        # - Verificar se o 'sistema_id' fornecido realmente existe no banco.
        return await self.repo.create_modulo(modulo_data)

    async def get_all_modulos(self) -> Sequence[Modulo]:
        return await self.repo.get_all_modulos()

    async def get_modulo_by_id(self, modulo_id: int) -> Optional[Modulo]:
        return await self.repo.get_modulo_by_id(modulo_id)
    
    async def update_modulo(self, modulo_id: int, modulo_data: ModuloUpdate) -> Optional[Modulo]:
        return await self.repo.update_modulo(modulo_id, modulo_data)

    async def delete_modulo(self, modulo_id: int) -> bool:
        return await self.repo.delete_modulo(modulo_id)
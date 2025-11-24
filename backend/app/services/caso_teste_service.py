from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence, Optional

from app.models import CasoTeste
from app.repositories.caso_teste_repository import CasoTesteRepository
from app.schemas import CasoTesteCreate, CasoTesteUpdate

class CasoTesteService:
    def __init__(self, db: AsyncSession):
        self.repo = CasoTesteRepository(db)

    async def create_caso_teste(self, caso_teste_data: CasoTesteCreate) -> CasoTeste:
        # Aqui você poderia adicionar validações, como por exemplo:
        # - Verificar se o 'sistema_id' fornecido realmente existe no banco.
        return await self.repo.create_caso_teste(caso_teste_data)

    async def get_all_casos_teste(self) -> Sequence[CasoTeste]:
        return await self.repo.get_all_casos_teste()

    async def get_caso_teste_by_id(self, caso_teste_id: int) -> Optional[CasoTeste]:
        return await self.repo.get_caso_teste_by_id(caso_teste_id)
    
    async def update_caso_teste(self, caso_teste_id: int, caso_teste_data: CasoTesteUpdate) -> Optional[CasoTeste]:
        return await self.repo.update_caso_teste(caso_teste_id, caso_teste_data)

    async def delete_caso_teste(self, caso_teste_id: int) -> bool:
        return await self.repo.delete_caso_teste(caso_teste_id)
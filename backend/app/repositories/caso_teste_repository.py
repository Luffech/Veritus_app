from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete
from typing import Sequence, Optional

from app.models.caso_teste import CasoTeste  # Garanta que a importação está correta
from app.schemas.caso_teste import CasoTesteCreate, CasoTesteUpdate # Garanta que a importação está correta

class CasoTesteRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_caso_teste(self, caso_teste_data: CasoTesteCreate) -> CasoTeste:
    
        db_caso_teste = CasoTeste(**caso_teste_data.model_dump())
        self.db.add(db_caso_teste)
        await self.db.commit()
        await self.db.refresh(db_caso_teste)
        return db_caso_teste

    async def get_all_casos_teste(self) -> Sequence[CasoTeste]:
        result = await self.db.execute(select(CasoTeste))
        return result.scalars().all()

    async def get_caso_teste_by_id(self, caso_teste_id: int) -> Optional[CasoTeste]:
        
        query = select(CasoTeste).where(CasoTeste.id == caso_teste_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def update_caso_teste(self, caso_teste_id: int, caso_teste_data: CasoTesteUpdate) -> Optional[CasoTeste]:
        
        update_data = caso_teste_data.model_dump(exclude_unset=True)
        
        if not update_data:
            return await self.get_caso_teste_by_id(caso_teste_id)

        query = (
            sqlalchemy_update(CasoTeste)
            .where(CasoTeste.id == caso_teste_id)
            .values(**update_data)
            .returning(CasoTeste)
        )
        result = await self.db.execute(query)
        await self.db.commit()
        
        return result.scalars().first() 

    async def delete_caso_teste(self, caso_teste_id: int) -> bool:
        query = sqlalchemy_delete(CasoTeste).where(CasoTeste.id == caso_teste_id)
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0
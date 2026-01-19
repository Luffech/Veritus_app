from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.usuario import Usuario
from app.repositories.defeito_repository import DefeitoRepository
from app.schemas.defeito import DefeitoCreate, DefeitoUpdate

class DefeitoService:
    def __init__(self, db: AsyncSession):
        self.repo = DefeitoRepository(db)

    async def registrar_defeito(self, dados: DefeitoCreate):
        return await self.repo.create(dados)

    async def listar_por_execucao(self, execucao_id: int):
        return await self.repo.get_by_execucao(execucao_id)

    # ESTA É A FUNÇÃO QUE ESTÁ DANDO ERRO. ELA PRECISA TER O PARÂMETRO filtro_responsavel_id
    async def listar_todos(self, current_user: Usuario, filtro_responsavel_id: Optional[int] = None):
        return await self.repo.get_all_with_details(responsavel_id=filtro_responsavel_id)

    async def atualizar_defeito(self, id: int, dados: DefeitoUpdate):
        return await self.repo.update(id, dados)

    async def excluir_defeito(self, id: int):
        return await self.repo.delete(id)
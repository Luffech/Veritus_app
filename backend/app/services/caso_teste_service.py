from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, func
from fastapi import HTTPException, status

from app.repositories.caso_teste_repository import CasoTesteRepository
from app.repositories.ciclo_teste_repository import CicloTesteRepository
from app.schemas.caso_teste import CasoTesteCreate, CasoTesteUpdate, CasoTesteResponse
from app.models.testing import StatusCicloEnum, CasoTeste
from app.core.errors import tratar_erro_integridade

class CasoTesteService:
    def __init__(self, db: AsyncSession):
        self.repo = CasoTesteRepository(db)
        self.ciclo_repo = CicloTesteRepository(db)
        self.db = db

    async def _verificar_iniciar_ciclo(self, ciclo_id: Optional[int]):
        """
        Se o caso for vinculado a um ciclo:
        1. Se estiver 'planejado', vira 'em_execucao'.
        2. Se estiver 'concluido' (foi reativado), vira 'em_execucao'.
        """
        if not ciclo_id:
            return

        ciclo = await self.ciclo_repo.get_by_id(ciclo_id)
        if ciclo and (ciclo.status == StatusCicloEnum.planejado or ciclo.status == StatusCicloEnum.concluido):
            await self.ciclo_repo.update(ciclo_id, {"status": StatusCicloEnum.em_execucao})

    async def _verificar_concluir_ciclo_vazio(self, ciclo_id: Optional[int]):
        if not ciclo_id:
            return
        query = select(func.count()).select_from(CasoTeste).where(CasoTeste.ciclo_id == ciclo_id)
        result = await self.db.execute(query)
        count = result.scalar()
        if count == 0:
            ciclo = await self.ciclo_repo.get_by_id(ciclo_id)
            if ciclo and ciclo.status != StatusCicloEnum.concluido:
                await self.ciclo_repo.update(ciclo_id, {"status": StatusCicloEnum.concluido})

    async def listar_todos(self) -> List[CasoTesteResponse]:
        casos = await self.repo.get_all()
        return [CasoTesteResponse.model_validate(c) for c in casos]

    async def listar_casos_teste(self, projeto_id: int) -> List[CasoTesteResponse]:
        casos = await self.repo.get_by_projeto(projeto_id)
        return [CasoTesteResponse.model_validate(c) for c in casos]

    async def obter_caso_teste(self, caso_id: int) -> Optional[CasoTesteResponse]:
        caso = await self.repo.get_by_id(caso_id)
        if caso:
            return CasoTesteResponse.model_validate(caso)
        return None

    async def criar_caso_teste(self, projeto_id: int, dados: CasoTesteCreate) -> CasoTesteResponse:
        existente = await self.repo.get_by_nome_projeto(dados.nome, projeto_id)
        if existente:
             raise HTTPException(status_code=400, detail="Já existe um Caso de Teste com este nome neste projeto.")

        try:
            novo_caso = await self.repo.create(projeto_id, dados)
            if dados.ciclo_id:
                await self._verificar_iniciar_ciclo(dados.ciclo_id)

            return CasoTesteResponse.model_validate(novo_caso)
        except IntegrityError as e:
            await self.db.rollback()
            tratar_erro_integridade(e)

    async def atualizar_caso_teste(self, caso_id: int, dados: CasoTesteUpdate) -> Optional[CasoTesteResponse]:
        caso_atual = await self.repo.get_by_id(caso_id)
        if not caso_atual:
            return None
        
        ciclo_antigo_id = caso_atual.ciclo_id
        update_data = dados.model_dump(exclude_unset=True)
        
        try:
            caso_atualizado = await self.repo.update(caso_id, dados)
            
            if caso_atualizado:
                novo_ciclo_id = update_data.get('ciclo_id')
                if 'ciclo_id' in update_data and novo_ciclo_id != ciclo_antigo_id:
                    if novo_ciclo_id:
                        await self._verificar_iniciar_ciclo(novo_ciclo_id)
                    if ciclo_antigo_id:
                        await self._verificar_concluir_ciclo_vazio(ciclo_antigo_id)

                return CasoTesteResponse.model_validate(caso_atualizado)
            return None
        except IntegrityError as e:
            await self.db.rollback()
            tratar_erro_integridade(e)

    async def deletar_caso_teste(self, caso_id: int) -> bool:
        caso_alvo = await self.repo.get_by_id(caso_id)
        ciclo_id_afetado = caso_alvo.ciclo_id if caso_alvo else None

        try:
            sucesso = await self.repo.delete(caso_id)
            if sucesso and ciclo_id_afetado:
                await self._verificar_concluir_ciclo_vazio(ciclo_id_afetado)
                
            return sucesso
        except IntegrityError as e:
            await self.db.rollback()
            tratar_erro_integridade(e, {
                "foreign key": "Não é possível excluir este caso de teste pois ele está em uso."
            })
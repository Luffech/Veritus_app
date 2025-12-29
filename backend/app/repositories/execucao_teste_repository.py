from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Sequence, Optional

from app.models.testing import (
    ExecucaoTeste, ExecucaoPasso, PassoCasoTeste, 
    CasoTeste, StatusExecucaoEnum
)
from app.models.usuario import Usuario
from app.schemas.execucao_teste import ExecucaoPassoUpdate

class ExecucaoTesteRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Verifica se tem teste pendente pra impedir o fechamento acidental do ciclo.
    async def verificar_pendencias_ciclo(self, ciclo_id: int) -> bool:
        query = select(ExecucaoTeste).where(
            ExecucaoTeste.ciclo_teste_id == ciclo_id,
            ExecucaoTeste.status_geral.in_([StatusExecucaoEnum.pendente, StatusExecucaoEnum.em_progresso])
        )
        result = await self.db.execute(query)
        return result.scalars().first() is not None

    # O coração da execução: Cria o registro e COPIA os passos do template (CasoTeste) para a execução.
    async def criar_planejamento(self, ciclo_id: int, caso_id: int, responsavel_id: int) -> ExecucaoTeste:
        # 1. Cria o registro pai da execução
        nova_exec = ExecucaoTeste(
            ciclo_teste_id=ciclo_id, 
            caso_teste_id=caso_id, 
            responsavel_id=responsavel_id, 
            status_geral=StatusExecucaoEnum.pendente
        )
        self.db.add(nova_exec)
        await self.db.flush() # Precisa do ID aqui pra vincular os passos abaixo

        # 2. Busca a "receita" (passos originais)
        query_passos = select(PassoCasoTeste.id).where(PassoCasoTeste.caso_teste_id == caso_id)
        passos_ids = (await self.db.execute(query_passos)).scalars().all()
        
        # 3. Snapshot: Cria cópias dos passos para essa execução específica
        if passos_ids:
            novos_passos_execucao = [
                ExecucaoPasso(
                    execucao_teste_id=nova_exec.id, 
                    passo_caso_teste_id=pid, # Mantém link com o original pra saber de onde veio
                    status="pendente", 
                    resultado_obtido=""
                ) 
                for pid in passos_ids
            ]
            self.db.add_all(novos_passos_execucao)
        
        await self.db.commit()
        return await self.get_by_id(nova_exec.id)

    # Busca detalhada carregando toda a hierarquia (Caso, Passos, Responsável).
    async def get_by_id(self, exec_id: int) -> Optional[ExecucaoTeste]:
        query = (
            select(ExecucaoTeste)
            .options(
                selectinload(ExecucaoTeste.caso_teste).selectinload(CasoTeste.passos),
                selectinload(ExecucaoTeste.responsavel).selectinload(Usuario.nivel_acesso),
                # Crucial: carrega o passo executado E o template dele pra mostrar "Resultado Esperado" na tela
                selectinload(ExecucaoTeste.passos_executados).selectinload(ExecucaoPasso.passo_template) 
            )
            .where(ExecucaoTeste.id == exec_id)
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    # Filtra as tarefas do QA logado ("Meus Testes").
    async def get_minhas_execucoes(
        self, 
        usuario_id: int, 
        status: Optional[StatusExecucaoEnum] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Sequence[ExecucaoTeste]:
        
        query = (
            select(ExecucaoTeste)
            .options(
                selectinload(ExecucaoTeste.caso_teste).selectinload(CasoTeste.passos),
                selectinload(ExecucaoTeste.passos_executados).selectinload(ExecucaoPasso.passo_template),
                selectinload(ExecucaoTeste.responsavel).selectinload(Usuario.nivel_acesso)
            )
            .where(ExecucaoTeste.responsavel_id == usuario_id)
        )

        if status:
            query = query.where(ExecucaoTeste.status_geral == status)

        query = query.order_by(ExecucaoTeste.updated_at.desc()).offset(skip).limit(limit)
            
        result = await self.db.execute(query)
        return result.scalars().all()

    # Busca simples de um passo único.
    async def get_execucao_passo(self, passo_id: int) -> Optional[ExecucaoPasso]:
        return await self.db.get(ExecucaoPasso, passo_id)

    # Atualiza o resultado de um passo (aprovado/reprovado e evidência).
    async def update_passo(self, passo_id: int, data: ExecucaoPassoUpdate) -> Optional[ExecucaoPasso]:
        passo = await self.db.get(ExecucaoPasso, passo_id)
        
        if passo:
            update_data = data.model_dump(exclude_unset=True)
            for k, v in update_data.items():
                setattr(passo, k, v)
            
            await self.db.commit()
            
            # Retorna com o template carregado pro front atualizar a tela bonito
            query = (
                select(ExecucaoPasso)
                .options(selectinload(ExecucaoPasso.passo_template))
                .where(ExecucaoPasso.id == passo_id)
            )
            result = await self.db.execute(query)
            return result.scalars().first()
            
        return None

    # Finaliza a execução mudando o status geral (Passou/Falhou).
    async def update_status_geral(self, exec_id: int, status: StatusExecucaoEnum) -> Optional[ExecucaoTeste]:
        execucao = await self.db.get(ExecucaoTeste, exec_id)
        if execucao:
            execucao.status_geral = status
            await self.db.commit()
            await self.db.refresh(execucao)
        return execucao
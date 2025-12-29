from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, desc

from app.models.projeto import Projeto, StatusProjetoEnum
from app.models.testing import (
    CicloTeste, StatusCicloEnum, 
    CasoTeste, 
    Defeito, StatusDefeitoEnum,
    ExecucaoTeste
)
from app.models.modulo import Modulo

class DashboardRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Roda vários counts separados pra montar os "Big Numbers" (cards) do topo da tela.
    async def get_kpis_gerais(self):
        queries = [
            select(func.count(Projeto.id)).where(Projeto.status == StatusProjetoEnum.ativo),
            select(func.count(CicloTeste.id)).where(CicloTeste.status == StatusCicloEnum.em_execucao),
            select(func.count(CasoTeste.id)),
            select(func.count(Defeito.id)).where(Defeito.status == StatusDefeitoEnum.aberto)
        ]
        
        results = []
        for q in queries:
            res = await self.db.execute(q)
            results.append(res.scalar() or 0)
            
        return {
            "total_projetos": results[0],
            "total_ciclos_ativos": results[1],
            "total_casos_teste": results[2],
            "total_defeitos_abertos": results[3]
        }

    # Agrupa o status das execuções (passou/falhou) focando só no que tá rodando agora.
    async def get_status_execucao_geral(self):
        query = (
            select(ExecucaoTeste.status_geral, func.count(ExecucaoTeste.id))
            .join(CicloTeste)
            .where(CicloTeste.status == StatusCicloEnum.em_execucao)
            .group_by(ExecucaoTeste.status_geral)
        )
        result = await self.db.execute(query)
        return result.all()

    # Classifica os bugs pendentes por gravidade (Crítico, Alto, Médio).
    async def get_defeitos_por_severidade(self):
        query = (
            select(Defeito.severidade, func.count(Defeito.id))
            .where(Defeito.status != StatusDefeitoEnum.fechado)
            .group_by(Defeito.severidade)
        )
        result = await self.db.execute(query)
        return result.all()

    # Faz o caminho reverso (Defeito -> Projeto -> Módulo) pra achar os módulos mais problemáticos.
    async def get_modulos_com_mais_defeitos(self, limit: int = 5):
        query = (
            select(Modulo.nome, func.count(Defeito.id))
            .select_from(Defeito)
            .join(Defeito.execucao)
            .join(ExecucaoTeste.caso_teste)
            .join(CasoTeste.projeto)
            .join(Projeto.modulo)
            .group_by(Modulo.nome)
            .order_by(desc(func.count(Defeito.id)))
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.all()
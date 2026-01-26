from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.projeto import Projeto
from app.models.testing import CicloTeste, StatusCicloEnum

async def seed_ciclos(session: AsyncSession):
    project = (await session.execute(select(Projeto).where(Projeto.nome == "Inventário Físico"))).scalars().first()

    if project:
        base_date = datetime.now(timezone.utc)

        ciclos_data = [
            {
                "nome": "Preparação da Contagem",
                "desc": "Definição de parâmetros e criação de docs.",
                "inicio": base_date, 
                "fim": base_date + timedelta(days=2) 
            },
            {
                "nome": "Execução da Contagem",
                "desc": "Impressão, contagem física e lançamentos.",
                "inicio": base_date + timedelta(days=3),
                "fim": base_date + timedelta(days=5)
            },
            {
                "nome": "Análise e Ajuste",
                "desc": "Análise de divergências e ajustes financeiros.",
                "inicio": base_date + timedelta(days=13),
                "fim": base_date + timedelta(days=15)
            },
            {
                "nome": "Finalização",
                "desc": "Arquivamento e desbloqueio do estoque.",
                "inicio": base_date + timedelta(days=18),
                "fim": base_date + timedelta(days=22)
            },
        ]

        for data in ciclos_data:
            result_ciclo = await session.execute(
                select(CicloTeste).where(
                    CicloTeste.nome == data["nome"], 
                    CicloTeste.projeto_id == project.id
                )
            )
            if not result_ciclo.scalars().first():
                novo_ciclo = CicloTeste(
                    nome=data["nome"],
                    descricao=data["desc"],
                    projeto_id=project.id,
                    status=StatusCicloEnum.planejado,
                    data_inicio=data["inicio"],
                    data_fim=data["fim"]
                )
                session.add(novo_ciclo)
        
        await session.flush()
        print("Cycles seeded.")
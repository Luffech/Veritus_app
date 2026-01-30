from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.projeto import Projeto
from app.models.testing import CicloTeste, StatusCicloEnum

async def seed_ciclos(session: AsyncSession):
    # === SAP Projects === #
    project_inv = (await session.execute(select(Projeto).where(Projeto.nome == "Inventário Físico"))).scalars().first()

    # === Veritus Projects === #
    project_security = (await session.execute(select(Projeto).where(Projeto.nome == "Security Core"))).scalars().first()
    project_admin = (await session.execute(select(Projeto).where(Projeto.nome == "Admin Panel"))).scalars().first()
    project_qa = (await session.execute(select(Projeto).where(Projeto.nome == "QA Planner"))).scalars().first()
    project_test = (await session.execute(select(Projeto).where(Projeto.nome == "Test Player"))).scalars().first()
    project_analytics = (await session.execute(select(Projeto).where(Projeto.nome == "Analytics"))).scalars().first()

    # === SAP Cycles === #
    if project_inv:
        base_date = datetime.now(timezone.utc)

        ciclos_data_inv = [
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

        for data in ciclos_data_inv:
            result_ciclo_inv = await session.execute(
                select(CicloTeste).where(
                    CicloTeste.nome == data["nome"], 
                    CicloTeste.projeto_id == project_inv.id
                )
            )
            if not result_ciclo_inv.scalars().first():
                novo_ciclo_inv = CicloTeste(
                    nome=data["nome"],
                    descricao=data["desc"],
                    projeto_id=project_inv.id,
                    status=StatusCicloEnum.em_execucao,
                    data_inicio=data["inicio"],
                    data_fim=data["fim"]
                )
                session.add(novo_ciclo_inv)


    # === Veritus Cycles === #
    if project_security:
        base_date = datetime.now(timezone.utc)

        ciclo_data_security = {
            "nome": "Ciclo de Blindagem e Autenticação v1",
            "desc": "Focado exclusivamente em garantir que o porteiro do sistema funciona. Validação de login, tokens expirados, logout forçado e tentativas de acesso sem credenciais.",
            "inicio": base_date, 
            "fim": base_date + timedelta(days=1) 
        }
        
        result_ciclo_security = await session.execute(
            select(CicloTeste).where(
                CicloTeste.nome == ciclo_data_security["nome"], 
                CicloTeste.projeto_id == project_security.id
            )
        )
        
        if not result_ciclo_security.scalars().first():
            novo_ciclo_security = CicloTeste(
                nome=ciclo_data_security["nome"],
                descricao=ciclo_data_security["desc"],
                projeto_id=project_security.id,
                status=StatusCicloEnum.em_execucao,
                data_inicio=ciclo_data_security["inicio"],
                data_fim=ciclo_data_security["fim"]
            )
            session.add(novo_ciclo_security)
    
    if project_admin:
        base_date = datetime.now(timezone.utc)

        ciclo_data_admin = {
            "nome": "Ciclo de Regressão Administrativa",
            "desc": "Validação completa das operações CRUD (Create, Read, Update, Delete) nos cadastros base (Usuários, Sistemas, Projetos). Essencial para garantir a integridade dos dados organizacionais.",
            "inicio": base_date, 
            "fim": base_date + timedelta(days=2) 
        }
        
        result_ciclo_admin = await session.execute(
            select(CicloTeste).where(
                CicloTeste.nome == ciclo_data_admin["nome"], 
                CicloTeste.projeto_id == project_admin.id
            )
        )
        
        if not result_ciclo_admin.scalars().first():
            novo_ciclo_admin = CicloTeste(
                nome=ciclo_data_admin["nome"],
                descricao=ciclo_data_admin["desc"],
                projeto_id=project_admin.id,
                status=StatusCicloEnum.em_execucao,
                data_inicio=ciclo_data_admin["inicio"],
                data_fim=ciclo_data_admin["fim"]
            )
            session.add(novo_ciclo_admin)
    
    if project_qa:
        base_date = datetime.now(timezone.utc)

        ciclo_data_qa = {
            "nome": "Ciclo de Validação do Planejamento",
            "desc": "Testes focados na usabilidade da criação de artefatos de teste. Verifica se é possível criar suites, casos de teste e passos complexos sem erros de interface.",
            "inicio": base_date, 
            "fim": base_date + timedelta(days=1)
        }
        
        result_ciclo_qa = await session.execute(
            select(CicloTeste).where(
                CicloTeste.nome == ciclo_data_qa["nome"], 
                CicloTeste.projeto_id == project_qa.id
            )
        )
        
        if not result_ciclo_qa.scalars().first():
            novo_ciclo_qa = CicloTeste(
                nome=ciclo_data_qa["nome"],
                descricao=ciclo_data_qa["desc"],
                projeto_id=project_qa.id,
                status=StatusCicloEnum.em_execucao,
                data_inicio=ciclo_data_qa["inicio"],
                data_fim=ciclo_data_qa["fim"]
            )
            session.add(novo_ciclo_qa)
    
    if project_test:
        base_date = datetime.now(timezone.utc)

        ciclo_data_test = {
            "nome": "Ciclo Crítico: Execução e Defeitos (Runner)",
            "desc": "O ciclo mais importante. Simula o dia a dia de um QA executando testes. Foco total no player de execução, cronômetro, aprovação de passos e, principalmente, no fluxo de reporte de bugs (modal de defeitos).",
            "inicio": base_date, 
            "fim": base_date + timedelta(days=3) 
        }
        
        result_ciclo_test = await session.execute(
            select(CicloTeste).where(
                CicloTeste.nome == ciclo_data_test["nome"], 
                CicloTeste.projeto_id == project_test.id
            )
        )
        
        if not result_ciclo_test.scalars().first():
            novo_ciclo_test = CicloTeste(
                nome=ciclo_data_test["nome"],
                descricao=ciclo_data_test["desc"],
                projeto_id=project_test.id,
                status=StatusCicloEnum.em_execucao,
                data_inicio=ciclo_data_test["inicio"],
                data_fim=ciclo_data_test["fim"]
            )
            session.add(novo_ciclo_test)
    
    if project_analytics:
        base_date = datetime.now(timezone.utc)

        ciclo_data_analytics = {
            "nome": "Ciclo de Métricas e Relatórios",
            "desc": "Validação visual e de dados dos dashboards. Verifica se os contadores batem com a realidade e se os gráficos de pizza/curva S estão renderizando corretamente.",
            "inicio": base_date + timedelta(days=5), 
            "fim": base_date + timedelta(days=6) 
        }
        
        result_ciclo_analytics = await session.execute(
            select(CicloTeste).where(
                CicloTeste.nome == ciclo_data_analytics["nome"], 
                CicloTeste.projeto_id == project_analytics.id
            )
        )
        
        if not result_ciclo_analytics.scalars().first():
            novo_ciclo_analytics = CicloTeste(
                nome=ciclo_data_analytics["nome"],
                descricao=ciclo_data_analytics["desc"],
                projeto_id=project_analytics.id,
                status=StatusCicloEnum.em_execucao,
                data_inicio=ciclo_data_analytics["inicio"],
                data_fim=ciclo_data_analytics["fim"]
            )
            session.add(novo_ciclo_analytics)
    
    await session.flush()
    print("Cycles seeded.")
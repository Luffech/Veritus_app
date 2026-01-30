from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sistema import Sistema
from app.models.modulo import Modulo
from app.models.usuario import Usuario
from app.models.projeto import Projeto, StatusProjetoEnum

async def seed_projetos(session: AsyncSession):
    sys_sap = (await session.execute(select(Sistema).where(Sistema.nome == 'SAP'))).scalars().first()
    if not sys_sap:
        return
    
    sys_veritus = (await session.execute(select(Sistema).where(Sistema.nome == 'Veritus'))).scalars().first()
    if not sys_veritus:
        return
    
    # === SAP Modules === #
    mod_mm = (await session.execute(
        select(Modulo).where(Modulo.nome == 'Materiais', Modulo.sistema_id == sys_sap.id)
    )).scalars().first()

    # === Veritus Modules === #
    mod_auth = (await session.execute(
        select(Modulo).where(Modulo.nome == 'Autenticação e Acesso', Modulo.sistema_id == sys_veritus.id)
    )).scalars().first()

    mod_adm = (await session.execute(
        select(Modulo).where(Modulo.nome == 'Administração', Modulo.sistema_id == sys_veritus.id)
    )).scalars().first()

    mod_mng = (await session.execute(
        select(Modulo).where(Modulo.nome == 'Gestão de QA', Modulo.sistema_id == sys_veritus.id)
    )).scalars().first()

    mod_run = (await session.execute(
        select(Modulo).where(Modulo.nome == 'Execução', Modulo.sistema_id == sys_veritus.id)
    )).scalars().first()

    mod_dash = (await session.execute(
        select(Modulo).where(Modulo.nome == 'Dashboards', Modulo.sistema_id == sys_veritus.id)
    )).scalars().first()

    # === Admin Users === #
    user_admin = (await session.execute(select(Usuario).where(Usuario.username == 'admin'))).scalars().first()

    # === SAP Projects === #
    if mod_mm and user_admin:
        project_mm = "Inventário Físico"
        result_proj_mm = await session.execute(select(Projeto).where(Projeto.nome == project_mm))
        mm_project = result_proj_mm.scalars().first()

        if not mm_project:
            mm_project = Projeto(
                nome = project_mm,
                descricao = "Projeto de execução anual do dashentário físico de estoque.",
                sistema_id = sys_sap.id,
                modulo_id = mod_mm.id,
                responsavel_id = user_admin.id,
                status=StatusProjetoEnum.ativo
            )
            session.add(mm_project)

    # === Veritus Projects === #
    if mod_auth and user_admin:
        project_auth = "Security Core"
        result_proj_auth = await session.execute(select(Projeto).where(Projeto.nome == project_auth))
        auth_project = result_proj_auth.scalars().first()

        if not auth_project:
            auth_project = Projeto(
                nome = project_auth,
                descricao = "Testes de Login, Logout, Tokens JWT, Refresh Token e Rotas Protegidas",
                sistema_id = sys_veritus.id,
                modulo_id = mod_auth.id,
                responsavel_id = user_admin.id,
                status=StatusProjetoEnum.ativo
            )
            session.add(auth_project)

    if mod_adm and user_admin:
        project_adm = "Admin Panel"
        result_proj_adm = await session.execute(select(Projeto).where(Projeto.nome == project_adm))
        adm_project = result_proj_adm.scalars().first()

        if not adm_project:
            adm_project = Projeto(
                nome = project_adm,
                descricao = "Testes das telas de Cadastro de Usuários, Sistemas, Módulos, Projetos e de Permissões",
                sistema_id = sys_veritus.id,
                modulo_id = mod_adm.id,
                responsavel_id = user_admin.id,
                status=StatusProjetoEnum.ativo
            )
            session.add(adm_project)

    if mod_mng and user_admin:
        project_mng = "QA Planner"
        result_proj_mng = await session.execute(select(Projeto).where(Projeto.nome == project_mng))
        mng_project = result_proj_mng.scalars().first()

        if not mng_project:
            mng_project = Projeto(
                nome = project_mng,
                descricao = "Testes de criação/edição de Casos de Testes, Suites e Planejamentos de Ciclos",
                sistema_id = sys_veritus.id,
                modulo_id = mod_mng.id,
                responsavel_id = user_admin.id,
                status=StatusProjetoEnum.ativo
            )
            session.add(mng_project)

    if mod_run and user_admin:
        project_run = "Test Player"
        result_proj_run = await session.execute(select(Projeto).where(Projeto.nome == project_run))
        run_project = result_proj_run.scalars().first()

        if not run_project:
            run_project = Projeto(
                nome = project_run,
                descricao = "Testes do executor, cronômetro, status de passos e fila de defeitos",
                sistema_id = sys_veritus.id,
                modulo_id = mod_run.id,
                responsavel_id = user_admin.id,
                status=StatusProjetoEnum.ativo
            )
            session.add(run_project)

    if mod_dash and user_admin:
        project_dash = "Analytics"
        result_proj_dash = await session.execute(select(Projeto).where(Projeto.nome == project_dash))
        dash_project = result_proj_dash.scalars().first()

        if not dash_project:
            dash_project = Projeto(
                nome = project_dash,
                descricao = "Testes de carregamento de gráficos, filtros de data e exportação de relatórios",
                sistema_id = sys_veritus.id,
                modulo_id = mod_dash.id,
                responsavel_id = user_admin.id,
                status=StatusProjetoEnum.ativo
            )
            session.add(dash_project)
        
    await session.flush()
    print("Projects seeded.")
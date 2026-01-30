from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sistema import Sistema
from app.models.modulo import Modulo

async def seed_modulos(session: AsyncSession):
    # === RETRIEVE SYSTEM ID ===
    res_sys = await session.execute(select(Sistema).where(Sistema.nome == 'SAP'))
    sap_sys = res_sys.scalars().first()

    res_sys_2 = await session.execute(select(Sistema).where(Sistema.nome == 'Veritus'))
    veritus_sys = res_sys_2.scalars().first()

    if sap_sys:
        materiais_mod = await session.execute(
            select(Modulo).where(
                Modulo.nome == 'Materiais',
                Modulo.sistema_id == sap_sys.id
            )
        )

        # === MODULE ===
        if not materiais_mod.scalars().first():
            mod_materiais = Modulo(
                nome='Materiais',
                descricao='Responsável pela gestão de compras, estoque, avaliação de materiais e verificação de faturas.',
                sistema_id=sap_sys.id
            )
            session.add(mod_materiais)

    if veritus_sys:
        auth_mod = await session.execute(
            select(Modulo).where(
                Modulo.nome == 'Autenticação e Acesso',
                Modulo.sistema_id == veritus_sys.id
            )
        )

        admin_mod = await session.execute(
            select(Modulo).where(
                Modulo.nome == 'Administração',
                Modulo.sistema_id == veritus_sys.id
            )
        )

        mngmnt_mod = await session.execute(
            select(Modulo).where(
                Modulo.nome == 'Gestão de QA',
                Modulo.sistema_id == veritus_sys.id
            )
        )

        runner_mod = await session.execute(
            select(Modulo).where(
                Modulo.nome == 'Execução',
                Modulo.sistema_id == veritus_sys.id
            )
        )

        dashboard_mod = await session.execute(
            select(Modulo).where(
                Modulo.nome == 'Dashboards',
                Modulo.sistema_id == veritus_sys.id
            )
        )

        # === MODULE ===
        if not auth_mod.scalars().first():
            mod_auth = Modulo(
                nome='Autenticação e Acesso',
                descricao='Login e Recuperação de Senha',
                sistema_id=veritus_sys.id
            )
            session.add(mod_auth)

        if not admin_mod.scalars().first():
            mod_admin = Modulo(
                nome='Administração',
                descricao='Gestão de Usuários, Sistemas e Projetos',
                sistema_id=veritus_sys.id
            )
            session.add(mod_admin)

        if not mngmnt_mod.scalars().first():
            mod_mngmnt = Modulo(
                nome='Gestão de QA',
                descricao='Ciclos e Casos de Teste',
                sistema_id=veritus_sys.id
            )
            session.add(mod_mngmnt)

        if not runner_mod.scalars().first():
            mod_runner = Modulo(
                nome='Execução',
                descricao='Player de Testes e Registro de Defeitos',
                sistema_id=veritus_sys.id
            )
            session.add(mod_runner)

        if not dashboard_mod.scalars().first():
            mod_dashboard = Modulo(
                nome='Dashboards',
                descricao='Métricas e Relatórios',
                sistema_id=veritus_sys.id
            )
            session.add(mod_dashboard)

    await session.flush()
    print("Modules seeded.")
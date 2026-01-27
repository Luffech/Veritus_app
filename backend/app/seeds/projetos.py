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
    
    mod_mm = (await session.execute(
        select(Modulo).where(Modulo.nome == 'Materiais', Modulo.sistema_id == sys_sap.id)
    )).scalars().first()

    user_admin = (await session.execute(select(Usuario).where(Usuario.username == 'admin'))).scalars().first()

    if mod_mm and user_admin:
        project_name = "Inventário Físico"
        result_proj = await session.execute(select(Projeto).where(Projeto.nome == project_name))
        project = result_proj.scalars().first()

        if not project:
            project = Projeto(
                nome = project_name,
                descricao = "Projeto de execução anual do inventário físico de estoque.",
                sistema_id = sys_sap.id,
                modulo_id = mod_mm.id,
                responsavel_id = user_admin.id,
                status=StatusProjetoEnum.ativo
            )
            session.add(project)
        await session.flush()

        print("Projects seeded.")
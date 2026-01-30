from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sistema import Sistema

async def seed_sistemas(session: AsyncSession):
    # === SYSTEM ===
    sap_sys = await session.execute(select(Sistema).where(Sistema.nome == 'SAP'))
    if not sap_sys.scalars().first():
        sys_sap = Sistema(
            nome='SAP',
            descricao='Sistema para gestão de dados corporativos',
            ativo=True
        )
        session.add(sys_sap)

    veritus_sys = await session.execute(select(Sistema).where(Sistema.nome == 'Veritus'))
    if not veritus_sys.scalars().first():
        sys_veritus = Sistema(
            nome='Veritus',
            descricao='Plataforma de Gestão e Execução de Testes Manuais',
            ativo=True
        )
        session.add(sys_veritus)
    
    await session.flush()
    print("Systems seeded.")
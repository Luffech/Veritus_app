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
        await session.flush()

    print("Systems seeded.")
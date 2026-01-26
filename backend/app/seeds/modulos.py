from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sistema import Sistema
from app.models.modulo import Modulo

async def seed_modulos(session: AsyncSession):
    # === RETRIEVE SYSTEM ID ===
    res_sys = await session.execute(select(Sistema).where(Sistema.nome == 'SAP'))
    sap_sys = res_sys.scalars().first()

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
            await session.flush()

        print("Modules seeded.")
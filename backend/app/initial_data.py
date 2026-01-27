import asyncio
import sys
from app.core.database import AsyncSessionLocal

from app.seeds.usuarios import seed_usuarios
from app.seeds.sistemas import seed_sistemas
from app.seeds.modulos import seed_modulos
from app.seeds.projetos import seed_projetos
from app.seeds.ciclos import seed_ciclos
from app.seeds.casos import seed_casos
from app.seeds.execucoes import seed_execucoes

async def seed_db():
    async with AsyncSessionLocal() as session:
        try:
            print("--- Starting Database Seed ---")
            
            # Users must come first to assign responsibilities
            await seed_usuarios(session)
            
            # Systems generate IDs for Modules
            await seed_sistemas(session)
            
            # Modules depend on Systems
            await seed_modulos(session)
            
            # 2. Projects (Depend on Modules and Users)
            await seed_projetos(session)
            
            # 3. Cycles (Depend on Projects)
            await seed_ciclos(session)

            # 4. Test Cases (Depend on Cycles, Projects, and Users)
            await seed_casos(session)

            await seed_execucoes(session)

            # Final commit for all changes
            await session.commit()
            print("--- Seed Completed Successfully! ---")

        except Exception as e:
            await session.rollback()
            print(f"Critical Error during Seed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(seed_db())
    except Exception as e:
        print(f"Execution Error: {e}")
        sys.exit(1)
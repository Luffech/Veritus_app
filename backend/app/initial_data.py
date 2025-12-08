import asyncio
import sys

try:
    from sqlalchemy import select
    from app.core.database import AsyncSessionLocal
    from app.models.nivel_acesso import NivelAcesso
    from app.models.usuario import Usuario
    from app.core.security import get_password_hash
except ImportError as e:
    sys.exit(1)

async def seed_db():
    async with AsyncSessionLocal() as session:
        # 1. Access Levels
        result_admin = await session.execute(select(NivelAcesso).where(NivelAcesso.nome == 'admin'))
        niv_admin = result_admin.scalars().first()
        
        if not niv_admin:
            niv_admin = NivelAcesso(nome='admin', descricao='Administrador do Sistema')
            session.add(niv_admin)
            await session.commit()
            await session.refresh(niv_admin)

        result_user = await session.execute(select(NivelAcesso).where(NivelAcesso.nome == 'user'))
        niv_user = result_user.scalars().first()

        if not niv_user:
            niv_user = NivelAcesso(nome='user', descricao='Usuário Padrão')
            session.add(niv_user)
            await session.commit()
            await session.refresh(niv_user)

        # 2. Users (Admin and Default Tester)
        result_u_admin = await session.execute(select(Usuario).where(Usuario.email == 'admin@example.com'))
        user_admin = result_u_admin.scalars().first()
        
        if not user_admin:
            user_admin = Usuario(
                nome='Administrador',
                username='admin', 
                email='admin@example.com',
                senha_hash=get_password_hash('adm123'),
                nivel_acesso_id=niv_admin.id,
                ativo=True
            )
            session.add(user_admin)

        result_u_igor = await session.execute(select(Usuario).where(Usuario.email == 'igor@example.com'))
        user_igor = result_u_igor.scalars().first()
        
        if not user_igor:
            user_igor = Usuario(
                nome='Igor Tester',
                username='igor',
                email='igor@example.com',
                senha_hash=get_password_hash('adm123'),
                nivel_acesso_id=niv_user.id,
                ativo=True
            )
            session.add(user_igor)

        await session.commit()

if __name__ == "__main__":
    try:
        asyncio.run(seed_db())
    except Exception:
        sys.exit(1)
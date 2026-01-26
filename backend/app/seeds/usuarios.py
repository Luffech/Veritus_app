from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.nivel_acesso import NivelAcesso
from app.models.usuario import Usuario
from app.core.security import get_password_hash

async def seed_usuarios(session: AsyncSession):
    # === ACCESS LEVELS ===
    admin_role = await session.execute(select(NivelAcesso).where(NivelAcesso.nome == 'admin'))
    niv_admin = admin_role.scalars().first()
    
    if not niv_admin:
        niv_admin = NivelAcesso(nome='admin', descricao='Administrador', permissoes={})
        session.add(niv_admin)
        await session.flush()

    user_role = await session.execute(select(NivelAcesso).where(NivelAcesso.nome == 'user'))
    niv_user = user_role.scalars().first()

    if not niv_user:
        niv_user = NivelAcesso(nome='user', descricao='Usuário Padrão', permissoes={})
        session.add(niv_user)
        await session.flush()

    # === USERS ===
    admin_user = await session.execute(select(Usuario).where(Usuario.email == 'admin@example.com'))
    if not admin_user.scalars().first():
        user_admin = Usuario(
            nome='Administrador',
            username='admin',
            email='admin@example.com',
            senha_hash=get_password_hash('adm123'),
            nivel_acesso_id=niv_admin.id,
            ativo=True
        )
        session.add(user_admin)

    igor_user = await session.execute(select(Usuario).where(Usuario.email == 'igor@example.com'))
    if not igor_user.scalars().first():
        user_igor = Usuario(
            nome='Igor Tester',
            username='igor',
            email='igor@example.com',
            senha_hash=get_password_hash('adm123'),
            nivel_acesso_id=niv_user.id,
            ativo=True
        )
        session.add(user_igor)

    diego_user = await session.execute(select(Usuario).where(Usuario.email == 'diego@example.com'))
    if not diego_user.scalars().first():
        user_diego = Usuario(
            nome='Diego Tester',
            username='diego',
            email='diego@example.com',
            senha_hash=get_password_hash('adm123'),
            nivel_acesso_id=niv_user.id,
            ativo=True
        )
        session.add(user_diego)

    luiz_user = await session.execute(select(Usuario).where(Usuario.email == 'luiz@example.com'))
    if not luiz_user.scalars().first():
        user_luiz = Usuario(
            nome='Luiz Tester',
            username='luiz',
            email='luiz@example.com',
            senha_hash=get_password_hash('adm123'),
            nivel_acesso_id=niv_user.id,
            ativo=True
        )
        session.add(user_luiz)

    isaque_user = await session.execute(select(Usuario).where(Usuario.email == 'isaque@example.com'))
    if not isaque_user.scalars().first():
        user_isaque = Usuario(
            nome='Isaque Tester',
            username='isaque',
            email='isaque@example.com',
            senha_hash=get_password_hash('adm123'),
            nivel_acesso_id=niv_user.id,
            ativo=True
        )
        session.add(user_isaque)

    kevin_user = await session.execute(select(Usuario).where(Usuario.email == 'kevin@example.com'))
    if not kevin_user.scalars().first():
        user_kevin = Usuario(
            nome='Kevin Tester',
            username='kevin',
            email='kevin@example.com',
            senha_hash=get_password_hash('adm123'),
            nivel_acesso_id=niv_user.id,
            ativo=True
        )
        session.add(user_kevin)
    
    await session.flush()
    
    print("Users seeded.")
import asyncio
import sys

# Tenta importar os modelos e a sessão. 
# Se falhar aqui, o problema é circular imports nos models.
try:
    from sqlalchemy import select
    from app.core.database import AsyncSessionLocal
    from app.models.nivel_acesso import NivelAcesso
    from app.models.usuario import Usuario
    from app.core.security import get_password_hash
except ImportError as e:
    print(f"ERRO CRÍTICO AO IMPORTAR NO SEED: {e}")
    sys.exit(1)

async def seed_db():
    async with AsyncSessionLocal() as session:
        print("--- INICIANDO SEED DE DADOS ---")

        # --- 1. NÍVEIS DE ACESSO ---
        print("Verificando Nível: admin")
        result_admin = await session.execute(select(NivelAcesso).where(NivelAcesso.nome == 'admin'))
        niv_admin = result_admin.scalars().first()
        
        if not niv_admin:
            print("Criando Nível: admin")
            niv_admin = NivelAcesso(nome='admin', descricao='Administrador do Sistema')
            session.add(niv_admin)
            await session.commit()
            await session.refresh(niv_admin)

        print("Verificando Nível: user")
        result_user = await session.execute(select(NivelAcesso).where(NivelAcesso.nome == 'user'))
        niv_user = result_user.scalars().first()

        if not niv_user:
            print("Criando Nível: user")
            niv_user = NivelAcesso(nome='user', descricao='Usuário Padrão')
            session.add(niv_user)
            await session.commit()
            await session.refresh(niv_user)

        # --- 2. USUÁRIOS ---
        # Admin
        print("Verificando Usuário: admin@example.com")
        result_u_admin = await session.execute(select(Usuario).where(Usuario.email == 'admin@example.com'))
        user_admin = result_u_admin.scalars().first()
        
        if not user_admin:
            print("Criando Usuário: admin@example.com")
            user_admin = Usuario(
                nome='Administrador',
                email='admin@example.com',
                senha_hash=get_password_hash('adm123'), # Usa a função de hash
                nivel_acesso_id=niv_admin.id,
                ativo=True
            )
            session.add(user_admin)

        # Testador
        print("Verificando Usuário: igor@example.com")
        result_u_igor = await session.execute(select(Usuario).where(Usuario.email == 'igor@example.com'))
        user_igor = result_u_igor.scalars().first()
        
        if not user_igor:
            print("Criando Usuário: igor@example.com")
            user_igor = Usuario(
                nome='Igor Tester',
                email='igor@example.com',
                senha_hash=get_password_hash('adm123'), # Usa a função de hash
                nivel_acesso_id=niv_user.id,
                ativo=True
            )
            session.add(user_igor)

        await session.commit()
        print("--- SEED CONCLUÍDO COM SUCESSO ---")

if __name__ == "__main__":
    # Garante que o loop roda corretamente
    try:
        asyncio.run(seed_db())
    except Exception as e:
        print(f"ERRO FATAL NO SEED: {e}")
        # Não queremos que o container morra para sempre se o seed falhar, 
        # mas precisamos saber que falhou.
        sys.exit(1)
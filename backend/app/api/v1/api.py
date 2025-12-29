from fastapi import APIRouter
from .endpoints import login, sistemas, modulo, usuarios, metrica, projeto, teste, defeito, dashboard

# Cria o roteador principal que vai agrupar todas as partes da API.
api_router = APIRouter()

# Registra as rotas de cada módulo, definindo o prefixo da URL e a tag para a documentação.
api_router.include_router(sistemas.router, prefix="/sistemas", tags=["Sistemas"])
api_router.include_router(modulo.router, prefix="/modulos", tags=["Módulos"])
api_router.include_router(projeto.router, prefix="/projetos", tags=["Projetos"])
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["Usuários"])
api_router.include_router(metrica.router, prefix="/metricas", tags=["Métricas"])
api_router.include_router(login.router, prefix="/login", tags=["Login"])
api_router.include_router(teste.router, prefix="/testes", tags=["Testes"])
api_router.include_router(defeito.router, prefix="/defeitos", tags=["Defeitos"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
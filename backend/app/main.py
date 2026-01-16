from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import Base, engine
from app.api.v1.api import api_router
import os

# Garante que a pasta de evidências exista ao iniciar.
os.makedirs("evidencias", exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de ciclo de vida para lidar com operações assíncronas 
    durante o startup e shutdown da aplicação.
    """
    async with engine.begin() as conn:
        # Cria as tabelas assincronamente se elas não existirem
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Caso precise fechar conexões ao desligar
    await engine.dispose()

# Inicializa a aplicação FastAPI com título, configurações e o lifespan
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Configura o CORS para permitir requisições de qualquer origem.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monta o diretório de arquivos estáticos e inclui as rotas da API.
app.mount("/evidencias", StaticFiles(directory="evidencias"), name="evidencias")
app.include_router(api_router, prefix=settings.API_V1_STR)

# Endpoints básicos para verificação de saúde e conectividade da API.
@app.get("/", summary="Endpoint raiz da API")
def read_root():
    return {"message": "Backend conectado ao banco de dados gerenciado pelo Docker!"}

@app.get("/health", summary="Verifica a saúde da API")
def health_check():
    return {"status": "healthy"}
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence, Optional
from app.core.database import AsyncSessionLocal
from app.schemas import SistemaCreate, SistemaResponse, SistemaUpdate
from app.services.sistema_service import SistemaService

# Inicializa o roteador para os endpoints de gerenciamento de sistemas.
router = APIRouter()

# Gerencia o ciclo de vida da sessão do banco de dados assíncrona.
async def get_db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# Função auxiliar que injeta o serviço de sistemas pronto para uso.
def get_sistema_service(db: AsyncSession = Depends(get_db_session)) -> SistemaService:
    return SistemaService(db)

# Cadastra um novo sistema no banco de dados e retorna o registro criado.
@router.post("/", response_model=SistemaResponse, status_code=status.HTTP_201_CREATED, summary="Criar um novo sistema")
async def create_sistema(
    sistema: SistemaCreate,
    service: SistemaService = Depends(get_sistema_service)
):
    return await service.create_sistema(sistema)

# Retorna a lista completa de sistemas cadastrados.
@router.get("/", response_model=Sequence[SistemaResponse], summary="Listar todos os sistemas")
async def get_sistemas(
    service: SistemaService = Depends(get_sistema_service)
):
    return await service.get_all_sistemas()

# Busca os detalhes de um sistema específico pelo ID, retornando erro se não existir.
@router.get("/{sistema_id}", response_model=SistemaResponse, summary="Obter um sistema por ID")
async def get_sistema(
    sistema_id: int,
    service: SistemaService = Depends(get_sistema_service)
):
    db_sistema = await service.get_sistema_by_id(sistema_id)
    if db_sistema is None:
        raise HTTPException(status_code=404, detail="Sistema não encontrado")
    return db_sistema

# Atualiza as informações de um sistema existente, validando se ele foi encontrado.
@router.put("/{sistema_id}", response_model=SistemaResponse, summary="Atualizar um sistema")
async def update_sistema(
    sistema_id: int,
    sistema: SistemaUpdate,
    service: SistemaService = Depends(get_sistema_service)
):
    updated_sistema = await service.update_sistema(sistema_id, sistema)
    if not updated_sistema:
        raise HTTPException(status_code=404, detail="Sistema não encontrado")
    return updated_sistema

# Remove permanentemente um sistema do banco de dados.
@router.delete("/{sistema_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Apagar um sistema")
async def delete_sistema(
    sistema_id: int,
    service: SistemaService = Depends(get_sistema_service)
):
    success = await service.delete_sistema(sistema_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sistema não encontrado")
    return
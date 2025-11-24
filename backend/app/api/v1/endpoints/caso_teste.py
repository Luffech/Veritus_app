from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List # É mais comum usar List da typing para response_models

# ATENÇÃO: Verifique se sua dependência de DB está neste caminho
from .sistemas import get_db_session 
from app.schemas import CasoTesteCreate, CasoTesteResponse, CasoTesteUpdate
from app.services.caso_teste_service import CasoTesteService # Verifique este caminho

router = APIRouter()

# Dependência para obter o serviço de CasoTeste
def get_caso_teste_service(db: AsyncSession = Depends(get_db_session)) -> CasoTesteService:
    return CasoTesteService(db)

@router.post("/", response_model=CasoTesteResponse, status_code=status.HTTP_201_CREATED, summary="Criar um novo caso de teste")
async def create_caso_teste(
    caso_teste: CasoTesteCreate,
    service: CasoTesteService = Depends(get_caso_teste_service)
):
    """
    Cria um novo caso de teste no sistema.
    """
    return await service.create_caso_teste(caso_teste)

@router.get("/", response_model=List[CasoTesteResponse], summary="Listar todos os casos de teste")
async def get_casos_teste(
    service: CasoTesteService = Depends(get_caso_teste_service)
):
    """
    Retorna uma lista de todos os casos de teste.
    """
    return await service.get_all_casos_teste()

@router.get("/{caso_teste_id}", response_model=CasoTesteResponse, summary="Obter um caso de teste por ID")
async def get_caso_teste(
    caso_teste_id: int,
    service: CasoTesteService = Depends(get_caso_teste_service)
):
    """
    Retorna um caso de teste específico pelo seu ID.
    """
    db_caso_teste = await service.get_caso_teste_by_id(caso_teste_id)
    if db_caso_teste is None:
        raise HTTPException(status_code=404, detail="Caso de Teste não encontrado")
    return db_caso_teste

@router.put("/{caso_teste_id}", response_model=CasoTesteResponse, summary="Atualizar um caso de teste")
async def update_caso_teste(
    caso_teste_id: int,
    caso_teste: CasoTesteUpdate,
    service: CasoTesteService = Depends(get_caso_teste_service)
):
    """
    Atualiza um caso de teste existente (usando PUT para substituir os dados).
    """
    updated_caso_teste = await service.update_caso_teste(caso_teste_id, caso_teste)
    if not updated_caso_teste:
        raise HTTPException(status_code=404, detail="Caso de Teste não encontrado")
    return updated_caso_teste

@router.delete("/{caso_teste_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Apagar um caso de teste")
async def delete_caso_teste(
    caso_teste_id: int,
    service: CasoTesteService = Depends(get_caso_teste_service)
):
    """
    Remove um caso de teste do sistema pelo seu ID.
    """
    success = await service.delete_caso_teste(caso_teste_id)
    if not success:
        raise HTTPException(status_code=404, detail="Caso de Teste não encontrado")
    return  # Retorna resposta vazia com status 204
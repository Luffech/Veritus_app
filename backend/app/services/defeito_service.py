from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.repositories.defeito_repository import DefeitoRepository
from app.repositories.execucao_teste_repository import ExecucaoTesteRepository
from app.schemas.defeito import DefeitoCreate, DefeitoUpdate, DefeitoResponse
from app.models.testing import StatusDefeitoEnum, StatusExecucaoEnum
from app.models.usuario import Usuario
from app.models.nivel_acesso import NivelAcessoEnum

class DefeitoService:
    def __init__(self, db: AsyncSession):
        self.repo = DefeitoRepository(db)
        self.execucao_repo = ExecucaoTesteRepository(db)

    async def registrar_defeito(self, dados: DefeitoCreate) -> DefeitoResponse:
        novo_defeito = await self.repo.create(dados)
        return DefeitoResponse.model_validate(novo_defeito)

    async def atualizar_defeito(self, id: int, dados: DefeitoUpdate) -> Optional[DefeitoResponse]:
        defeito_atualizado = await self.repo.update(id, dados)
        
        if not defeito_atualizado:
            return None
        if dados.status == StatusDefeitoEnum.corrigido:
            await self.execucao_repo.update_status(
                defeito_atualizado.execucao_teste_id, 
                StatusExecucaoEnum.reteste
            )
        
        return DefeitoResponse.model_validate(defeito_atualizado)

    async def excluir_defeito(self, id: int) -> bool:
        return await self.repo.delete(id)

    # --- MÉTODOS DE LEITURA ---
    
    async def listar_todos(self, current_user: Usuario, filtro_responsavel_id: Optional[int] = None):
        is_admin = False
        if current_user.nivel_acesso:
             is_admin = current_user.nivel_acesso.nome == NivelAcessoEnum.admin or current_user.nivel_acesso.nome == "admin"

        if not is_admin:
            return await self.repo.get_all_with_details(responsavel_id=current_user.id)
        
        return await self.repo.get_all_with_details(responsavel_id=filtro_responsavel_id)

    async def listar_por_execucao(self, execucao_id: int):
        return await self.repo.get_by_execucao(execucao_id)
    async def obter_nome_teste_por_execucao(self, execucao_id: int) -> str:
        try:
            nome = await self.repo.get_nome_teste_por_execucao(execucao_id)
            return nome if nome else "Teste não identificado"
        except Exception as e:
            return "Teste Desconhecido"
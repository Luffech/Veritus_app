from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import DashboardResponse
from app.api.deps import get_current_user

# Inicializa o roteador para os endpoints do dashboard.
router = APIRouter()

# Endpoint GET que retorna os dados consolidados para a tela inicial.
@router.get("/", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Instancia o serviço de dashboard injetando a sessão do banco.
    service = DashboardService(db)
    
    # Executa a lógica de busca e retorna os dados processados.
    return await service.get_dashboard_data()
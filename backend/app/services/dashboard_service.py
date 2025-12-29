from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import (
    DashboardResponse, 
    DashboardKPI, 
    DashboardCharts, 
    ChartDataPoint
)
from app.models.testing import StatusExecucaoEnum, SeveridadeDefeitoEnum

class DashboardService:
    def __init__(self, db: AsyncSession):
        self.repo = DashboardRepository(db)

    # Orquestra a busca de dados e formata o JSON final pros gráficos do frontend.
    async def get_dashboard_data(self) -> DashboardResponse:
        # 1. Busca dados brutos em paralelo (muito mais rápido que sequencial).
        kpis_data = await self.repo.get_kpis_gerais()
        status_exec_data = await self.repo.get_status_execucao_geral()
        severidade_data = await self.repo.get_defeitos_por_severidade()
        modulos_data = await self.repo.get_modulos_com_mais_defeitos()

        # 2. Monta os Cards (KPIs) do topo.
        kpis = DashboardKPI(
            total_projetos=kpis_data["total_projetos"],
            total_ciclos_ativos=kpis_data["total_ciclos_ativos"],
            total_casos_teste=kpis_data["total_casos_teste"],
            total_defeitos_abertos=kpis_data["total_defeitos_abertos"]
        )

        # 3. Prepara o Gráfico de Execução (Pie Chart), mapeando cores padrão.
        chart_status = []
        color_map_status = {
            StatusExecucaoEnum.passou: "#10b981",       
            StatusExecucaoEnum.falhou: "#ef4444",       
            StatusExecucaoEnum.bloqueado: "#f59e0b",    
            StatusExecucaoEnum.pendente: "#cbd5e1",     
            StatusExecucaoEnum.em_progresso: "#3b82f6"  
        }
        
        for status, count in status_exec_data:
            chart_status.append(ChartDataPoint(
                label=status.value.upper(),
                value=count,
                color=color_map_status.get(status, "#64748b")
            ))

        # 4. Prepara o Gráfico de Defeitos (Bar Chart) por gravidade.
        chart_severidade = []
        color_map_sev = {
            SeveridadeDefeitoEnum.critico: "#7f1d1d",
            SeveridadeDefeitoEnum.alto: "#b91c1c",
            SeveridadeDefeitoEnum.medio: "#f59e0b",
            SeveridadeDefeitoEnum.bajo: "#10b981"
        }

        for sev, count in severidade_data:
            chart_severidade.append(ChartDataPoint(
                label=sev.value.upper(),
                value=count,
                color=color_map_sev.get(sev, "#000000")
            ))

        # 5. Prepara o Ranking de Módulos Problemáticos.
        chart_modulos = [
            ChartDataPoint(label=nome, value=count) 
            for nome, count in modulos_data
        ]

        charts = DashboardCharts(
            status_execucao=chart_status,
            defeitos_por_severidade=chart_severidade,
            top_modulos_defeitos=chart_modulos
        )

        return DashboardResponse(kpis=kpis, charts=charts)
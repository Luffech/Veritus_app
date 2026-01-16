from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import (
    DashboardResponse, 
    DashboardKPI, 
    DashboardCharts, 
    ChartDataPoint,
    # Adicionando as novas importações necessárias
    RunnerDashboardResponse,
    RunnerKPI,
    RunnerRankingData,
    RunnerDashboardCharts
)
from app.models.testing import StatusExecucaoEnum, SeveridadeDefeitoEnum

class DashboardService:
    def __init__(self, db: AsyncSession):
        self.repo = DashboardRepository(db)

    async def get_dashboard_data(self) -> DashboardResponse:
        # 1. Busca dados brutos
        kpis_data = await self.repo.get_kpis_gerais()
        status_exec_data = await self.repo.get_status_execucao_geral()
        severidade_data = await self.repo.get_defeitos_por_severidade()
        modulos_data = await self.repo.get_modulos_com_mais_defeitos()

        # 2. Monta os 8 Cards (KPIs)
        kpis = DashboardKPI(
            total_projetos=kpis_data["total_projetos"],
            total_ciclos_ativos=kpis_data["total_ciclos_ativos"],
            total_casos_teste=kpis_data["total_casos_teste"],
            taxa_sucesso_ciclos=kpis_data["taxa_sucesso_ciclos"],
            
            total_defeitos_abertos=kpis_data["total_defeitos_abertos"],
            total_defeitos_criticos=kpis_data["total_defeitos_criticos"],
            total_bloqueados=kpis_data["total_bloqueados"],
            total_aguardando_reteste=kpis_data["total_aguardando_reteste"]
        )

        # 3. Prepara Gráfico de Execução (Pie Chart)
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

        # 4. Prepara Gráfico de Defeitos (Bar Chart)
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

        # 5. Prepara Ranking de Módulos
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
    
    async def get_runner_dashboard_data(self) -> RunnerDashboardResponse:
        # Repare nos 8 espaços (2 tabs) de recuo aqui:
        # 1. Procura os dados brutos no repositório
        kpis_brutos = await self.repo.get_runner_kpis()
        ranking_bruto = await self.repo.get_ranking_runners()

        # 2. Organiza os KPIs (os 4 cards de cima)
        kpis = RunnerKPI(
            total_execucoes_concluidas=kpis_brutos["total_concluidos"],
            total_defeitos_reportados=kpis_brutos["total_defeitos"],
            tempo_medio_execucao_minutos=kpis_brutos["tempo_medio_minutos"],
            testes_em_fila=kpis_brutos["total_fila"]
        )

        # 3. Prepara o Ranking de Produtividade (Gráfico de Barras)
        ranking_data = [
            RunnerRankingData(label=nome, value=total, color="#3b82f6") 
            for nome, total in ranking_bruto
        ]

        charts = RunnerDashboardCharts(
            ranking_produtividade=ranking_data,
            defeitos_por_runner=[] 
        )

        return RunnerDashboardResponse(kpis=kpis, charts=charts)
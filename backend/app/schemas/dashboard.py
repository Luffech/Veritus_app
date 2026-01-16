from pydantic import BaseModel
from typing import List, Optional

class DashboardKPI(BaseModel):
    # KPIs Originais
    total_projetos: int
    total_ciclos_ativos: int
    total_casos_teste: int
    total_defeitos_abertos: int
    
    # Novos KPIs (Focados em Qualidade e Urgência)
    taxa_sucesso_ciclos: float      # % de testes que passaram nos ciclos ativos
    total_bloqueados: int           # Testes que não podem ser executados
    total_defeitos_criticos: int    # Bugs de severidade Crítica
    total_aguardando_reteste: int   # Bugs corrigidos esperando validação do QA

class ChartDataPoint(BaseModel):
    label: str
    value: int
    color: Optional[str] = None

class DashboardCharts(BaseModel):
    status_execucao: List[ChartDataPoint]
    defeitos_por_severidade: List[ChartDataPoint]
    top_modulos_defeitos: List[ChartDataPoint]

class DashboardResponse(BaseModel):
    kpis: DashboardKPI
    charts: DashboardCharts

# Novos Schemas para o Dashboard de Performance dos Testadores 

class RunnerKPI(BaseModel):
    total_execucoes_concluidas: int
    total_defeitos_reportados: int
    tempo_medio_execucao_minutos: float
    testes_em_fila: int

class RunnerRankingData(BaseModel):
    label: str  # Nome do Testador
    value: int  # Quantidade de testes concluídos
    color: Optional[str] = None

class RunnerDashboardCharts(BaseModel):
    ranking_produtividade: List[RunnerRankingData]
    defeitos_por_runner: List[RunnerRankingData]

class RunnerDashboardResponse(BaseModel):
    kpis: RunnerKPI
    charts: RunnerDashboardCharts
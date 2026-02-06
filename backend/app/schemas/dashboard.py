from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

# --- SCHEMAS DO DASHBOARD GERAL ---

class DashboardKPI(BaseModel):
    total_projetos: int
    total_ciclos_ativos: int
    total_casos_teste: int    
    total_testes_finalizados: int   
    total_defeitos_abertos: int
    total_defeitos_criticos: int        
    total_pendentes: int
    total_bloqueados: int
    total_aguardando_reteste: int

class ChartDataPoint(BaseModel):
    label: str
    value: int
    aprovados: Optional[int] = 0  # Adicionado para suportar barras duplas
    color: Optional[str] = None

class DashboardCharts(BaseModel):
    status_execucao: List[ChartDataPoint]
    defeitos_por_severidade: List[ChartDataPoint]
    top_modulos_defeitos: List[ChartDataPoint]

class DashboardResponse(BaseModel):
    kpis: DashboardKPI
    charts: DashboardCharts

# --- SCHEMAS DO DASHBOARD DO EXECUTOR ---

class RunnerKPI(BaseModel):
    total_execucoes_concluidas: int
    total_defeitos_reportados: int
    tempo_medio_execucao_minutos: float
    testes_em_fila: int
    ultima_atividade: Optional[datetime] = None 

class RunnerRankingData(BaseModel):
    label: str  
    value: int  
    color: Optional[str] = None

class StatusDistributionData(BaseModel):
    name: str   
    value: int   
    color: Optional[str] = None

class TimelineItem(BaseModel):
    id: int
    case_name: str
    status: str
    assignee: str
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class RunnerDashboardCharts(BaseModel):
    ranking_produtividade: List[RunnerRankingData] = []
    status_distribuicao: List[StatusDistributionData] = []
    timeline: List[TimelineItem] = []

class RunnerDashboardResponse(BaseModel):
    kpis: RunnerKPI
    charts: RunnerDashboardCharts

# --- SCHEMAS DE ANÁLISE DE PERFORMANCE (O QUE ESTAMOS USANDO) ---

class TeamStats(BaseModel):
    efetividade: float
    risco_ativo: int
    execucoes_por_testador_30d: float
    tempo_medio_registro_horas: float

class TesterStats(BaseModel):
    impacto_relevante: int
    execucoes_30d: int
    severidade_media: float
    tempo_medio_registro_horas: float

class PerformanceResponse(BaseModel):
    stats_equipe: Optional[TeamStats] = None
    stats_testador: Optional[TesterStats] = None
    
    grafico_velocidade: List[ChartDataPoint] = []
    grafico_top_modulos: List[ChartDataPoint] = []
    grafico_severidade: List[ChartDataPoint] = []
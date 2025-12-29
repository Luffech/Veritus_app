from pydantic import BaseModel
from typing import List, Optional

# Os "Big Numbers" que aparecem nos cards do topo.
class DashboardKPI(BaseModel):
    total_projetos: int
    total_ciclos_ativos: int
    total_casos_teste: int
    total_defeitos_abertos: int

# Estrutura pra alimentar gráficos.
class ChartDataPoint(BaseModel):
    label: str
    value: int
    color: Optional[str] = None

# Agrupa todos os datasets dos gráficos.
class DashboardCharts(BaseModel):
    status_execucao: List[ChartDataPoint]
    defeitos_por_severidade: List[ChartDataPoint]
    top_modulos_defeitos: List[ChartDataPoint]

# Resposta completa do endpoint /dashboard.
class DashboardResponse(BaseModel):
    kpis: DashboardKPI
    charts: DashboardCharts
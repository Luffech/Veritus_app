from pydantic import BaseModel
from typing import List, Optional

# Estrutura genérica pra montar aqueles cards coloridos no topo do dashboard.
class MetricaKPI(BaseModel):
    label: str
    valor: int | float
    unidade: Optional[str] = None
    cor: Optional[str] = None # Ex: "red", "green" pra condicionais no front

# Resumo estatístico do projeto, usado pra alimentar gráficos e tabelas de relatório.
class MetricaProjeto(BaseModel):
    projeto_id: int
    total_casos: int
    casos_sucesso: int
    casos_falha: int
    taxa_cobertura: float  # %
    taxa_sucesso: float    # %
    kpis: List[MetricaKPI] # Lista flexível pra injetar métricas extras sem quebrar o contrato
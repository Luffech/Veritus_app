from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, desc, case, or_, and_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from app.models.modulo import Modulo
from app.models.projeto import Projeto, StatusProjetoEnum
from app.models.testing import (
    CicloTeste, StatusCicloEnum, 
    CasoTeste, 
    Defeito, StatusDefeitoEnum, SeveridadeDefeitoEnum,
    ExecucaoTeste, StatusExecucaoEnum
)
from app.models.usuario import Usuario

class DashboardRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_kpis_gerais(self, sistema_id: Optional[int] = None) -> Dict[str, Any]:
        # --- 1. PROJETOS ---
        q_projetos = select(func.count(Projeto.id)).where(Projeto.status == StatusProjetoEnum.ativo)
        if sistema_id:
            q_projetos = q_projetos.where(Projeto.sistema_id == sistema_id)

        # --- 2. CICLOS ---
        q_ciclos = select(func.count(CicloTeste.id)).join(Projeto).where(
            CicloTeste.status.in_([StatusCicloEnum.em_execucao, StatusCicloEnum.planejado])
        )
        if sistema_id:
            q_ciclos = q_ciclos.where(Projeto.sistema_id == sistema_id)

        # --- 3. CASOS DE TESTE ---
        q_casos = select(func.count(CasoTeste.id)).join(Projeto)
        if sistema_id:
            q_casos = q_casos.where(Projeto.sistema_id == sistema_id)

        # --- 4. DEFEITOS ABERTOS ---
        q_defeitos_abertos = (
            select(func.count(Defeito.id))
            .join(Defeito.execucao)
            .join(ExecucaoTeste.caso_teste)
            .join(CasoTeste.projeto)
            .where(Defeito.status.in_([StatusDefeitoEnum.aberto, StatusDefeitoEnum.em_teste]))
        )
        if sistema_id:
            q_defeitos_abertos = q_defeitos_abertos.where(Projeto.sistema_id == sistema_id)

        # --- 5. DEFEITOS CRITICOS/ALTOS ---
        q_criticos = (
            select(func.count(Defeito.id))
            .join(Defeito.execucao)
            .join(ExecucaoTeste.caso_teste)
            .join(CasoTeste.projeto)
            .where(
                Defeito.status != StatusDefeitoEnum.fechado,
                Defeito.severidade.in_([SeveridadeDefeitoEnum.critico, SeveridadeDefeitoEnum.alto])
            )
        )
        if sistema_id:
            q_criticos = q_criticos.where(Projeto.sistema_id == sistema_id)

        # --- 6. AGUARDANDO RETESTE (Defeitos corrigidos) ---
        q_reteste = (
            select(func.count(Defeito.id))
            .join(Defeito.execucao)
            .join(ExecucaoTeste.caso_teste)
            .join(CasoTeste.projeto)
            .where(Defeito.status == StatusDefeitoEnum.corrigido)
        )
        if sistema_id:
            q_reteste = q_reteste.where(Projeto.sistema_id == sistema_id)

        # --- 7. STATUS DE EXECUÇÃO (Para KPIs e Taxas) ---
        #  Passou (fechado), Falhou (falha) e Pendentes separadamente
        q_exec_stats = (
            select(
                func.sum(case((ExecucaoTeste.status_geral == StatusExecucaoEnum.fechado, 1), else_=0)), # Passou
                func.sum(case((ExecucaoTeste.status_geral == StatusExecucaoEnum.falha, 1), else_=0)),   # Falhou
                func.sum(case((ExecucaoTeste.status_geral.in_([StatusExecucaoEnum.pendente, StatusExecucaoEnum.em_progresso]), 1), else_=0)), # Pendente
                func.sum(case((ExecucaoTeste.status_geral == StatusExecucaoEnum.bloqueado, 1), else_=0)) # Bloqueado
            )
            .join(ExecucaoTeste.caso_teste)
            .join(CasoTeste.projeto)
        )
        if sistema_id:
            q_exec_stats = q_exec_stats.where(Projeto.sistema_id == sistema_id)

        # EXECUÇÃO DAS QUERIES
        total_projetos = (await self.db.execute(q_projetos)).scalar() or 0
        total_ciclos = (await self.db.execute(q_ciclos)).scalar() or 0
        total_casos = (await self.db.execute(q_casos)).scalar() or 0
        total_defeitos = (await self.db.execute(q_defeitos_abertos)).scalar() or 0
        total_criticos = (await self.db.execute(q_criticos)).scalar() or 0
        total_reteste_def = (await self.db.execute(q_reteste)).scalar() or 0
        
        exec_stats_result = (await self.db.execute(q_exec_stats)).first()
        
        passed = exec_stats_result[0] or 0
        failed = exec_stats_result[1] or 0
        pending = exec_stats_result[2] or 0
        blocked = exec_stats_result[3] or 0

        
        total_executed_valid = passed + failed
        taxa = round((passed / total_executed_valid * 100), 1) if total_executed_valid > 0 else 0.0

        total_aguardando_reteste = total_reteste_def

        return {
            "total_projetos": total_projetos,
            "total_ciclos_ativos": total_ciclos,
            "total_casos_teste": total_casos,
            "taxa_sucesso_ciclos": taxa,
            "total_defeitos_abertos": total_defeitos,
            "total_defeitos_criticos": total_criticos,
            "total_pendentes": pending,
            "total_bloqueados": blocked,
            "total_aguardando_reteste": total_aguardando_reteste
        }

    async def get_status_execucao_geral(self, sistema_id: Optional[int] = None) -> List[tuple]:
        query = (
            select(ExecucaoTeste.status_geral, func.count(ExecucaoTeste.id))
            .join(ExecucaoTeste.caso_teste)
            .join(CasoTeste.projeto)
            .group_by(ExecucaoTeste.status_geral)
        )
        if sistema_id:
            query = query.where(Projeto.sistema_id == sistema_id)
            
        result = await self.db.execute(query)
        return result.all()

    async def get_defeitos_por_severidade(self, sistema_id: Optional[int] = None) -> List[tuple]:
        query = (
            select(Defeito.severidade, func.count(Defeito.id))
            .join(Defeito.execucao)
            .join(ExecucaoTeste.caso_teste)
            .join(CasoTeste.projeto)
            .where(Defeito.status != StatusDefeitoEnum.fechado)
            .group_by(Defeito.severidade)
        )
        if sistema_id:
            query = query.where(Projeto.sistema_id == sistema_id)
            
        result = await self.db.execute(query)
        return result.all()
    
    async def get_modulos_com_mais_defeitos(self, limit: int = 5, sistema_id: Optional[int] = None) -> List[tuple]:
        query = (
            select(Modulo.nome, func.count(Defeito.id))
            .select_from(Defeito)
            .join(Defeito.execucao)
            .join(ExecucaoTeste.caso_teste)
            .join(CasoTeste.projeto)
            .join(Projeto.modulo)
            .group_by(Modulo.nome)
            .order_by(desc(func.count(Defeito.id)))
            .limit(limit)
        )
        
        if sistema_id:
            query = query.where(Projeto.sistema_id == sistema_id)

        result = await self.db.execute(query)
        return result.all()

    # --- metodos do runner ---
    async def get_runner_kpis(self, runner_id: int) -> Dict[str, Any]:
        q_concluidos = select(func.count(ExecucaoTeste.id)).where(
            ExecucaoTeste.responsavel_id == runner_id,
            ExecucaoTeste.status_geral.in_([StatusExecucaoEnum.fechado, StatusExecucaoEnum.falha, StatusExecucaoEnum.bloqueado])
        )

        q_defeitos = select(func.count(Defeito.id)).join(Defeito.execucao).where(
            ExecucaoTeste.responsavel_id == runner_id
        )

        q_fila = select(func.count(ExecucaoTeste.id)).where(
            ExecucaoTeste.responsavel_id == runner_id,
            ExecucaoTeste.status_geral == StatusExecucaoEnum.pendente
        )

        q_last = select(func.max(ExecucaoTeste.updated_at)).where(
            ExecucaoTeste.responsavel_id == runner_id
        )

        total_concluidos = (await self.db.execute(q_concluidos)).scalar() or 0
        total_defeitos = (await self.db.execute(q_defeitos)).scalar() or 0
        total_fila = (await self.db.execute(q_fila)).scalar() or 0
        ultima_atividade = (await self.db.execute(q_last)).scalar()

        return {
            "total_concluidos": total_concluidos,
            "total_defeitos": total_defeitos,
            "tempo_medio_minutos": 0.0,
            "total_fila": total_fila,
            "ultima_atividade": ultima_atividade
        }

    async def get_status_distribution(self, runner_id: Optional[int] = None) -> List[tuple]:
        query = select(ExecucaoTeste.status_geral, func.count(ExecucaoTeste.id)).group_by(ExecucaoTeste.status_geral)
        if runner_id:
            query = query.where(ExecucaoTeste.responsavel_id == runner_id)
        
        result = await self.db.execute(query)
        return result.all()

    async def get_runner_timeline(self, runner_id: Optional[int] = None, limit: int = 10):
        from sqlalchemy.orm import selectinload
        
        query = (
            select(ExecucaoTeste)
            .options(selectinload(ExecucaoTeste.caso_teste), selectinload(ExecucaoTeste.responsavel))
            .order_by(desc(ExecucaoTeste.updated_at))
            .limit(limit)
        )
        if runner_id:
            query = query.where(ExecucaoTeste.responsavel_id == runner_id)
            
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_ranking_runners(self, limit: int = 5) -> List[tuple]:
        query = (
            select(Usuario.nome, func.count(ExecucaoTeste.id))
            .join(ExecucaoTeste, Usuario.id == ExecucaoTeste.responsavel_id)
            .where(ExecucaoTeste.status_geral.in_([StatusExecucaoEnum.fechado, StatusExecucaoEnum.falha, StatusExecucaoEnum.bloqueado]))
            .group_by(Usuario.nome)
            .order_by(desc(func.count(ExecucaoTeste.id)))
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.all()

    # --- metodos de performance (novos) ---

    async def get_performance_velocity(self, user_id: Optional[int] = None, days: int = 30) -> List[tuple]:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = (
            select(
                func.date(ExecucaoTeste.updated_at).label('date'), 
                func.count(ExecucaoTeste.id)
            )
            .where(ExecucaoTeste.updated_at >= cutoff_date)
            .where(ExecucaoTeste.status_geral.in_([StatusExecucaoEnum.fechado, StatusExecucaoEnum.falha, StatusExecucaoEnum.bloqueado]))
            .group_by(func.date(ExecucaoTeste.updated_at))
            .order_by(func.date(ExecucaoTeste.updated_at))
        )

        if user_id:
            query = query.where(ExecucaoTeste.responsavel_id == user_id)

        result = await self.db.execute(query)
        return result.all()

    async def get_top_modules_by_defects_perf(self, user_id: Optional[int] = None, limit: int = 5, days: int = 30) -> List[tuple]:
        """Top módulos onde o testador (ou equipe) está encontrando mais defeitos.

        Observação: como o modelo Defeito não guarda "criado_por", atribuímos o defeito ao responsável
        da execução (ExecucaoTeste.responsavel_id), que é o que aparece na tela de Gestão de Falhas.
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        query = (
            select(Modulo.nome, func.count(Defeito.id))
            .select_from(Defeito)
            .join(Defeito.execucao)
            .join(ExecucaoTeste.caso_teste)
            .join(CasoTeste.projeto)
            .join(Projeto.modulo)
            .where(Defeito.created_at >= cutoff_date)
            .where(Defeito.status != StatusDefeitoEnum.fechado)
            .group_by(Modulo.nome)
            .order_by(desc(func.count(Defeito.id)))
            .limit(limit)
        )

        if user_id:
            query = query.where(ExecucaoTeste.responsavel_id == user_id)

        result = await self.db.execute(query)
        return result.all()

    async def get_defects_by_severity_perf(self, user_id: Optional[int] = None, days: int = 30) -> List[tuple]:
        """Distribuição de severidade de defeitos (abertos) atribuídos ao testador/equipe."""
        cutoff_date = datetime.now() - timedelta(days=days)
        query = (
            select(Defeito.severidade, func.count(Defeito.id))
            .select_from(Defeito)
            .join(Defeito.execucao)
            .where(Defeito.created_at >= cutoff_date)
            .where(Defeito.status != StatusDefeitoEnum.fechado)
            .group_by(Defeito.severidade)
        )
        if user_id:
            query = query.where(ExecucaoTeste.responsavel_id == user_id)
        result = await self.db.execute(query)
        return result.all()

    async def get_team_performance_stats(self, days: int = 30) -> Dict[str, Any]:
        """4 métricas gerais (equipe) focadas em testadores."""
        cutoff_date = datetime.now() - timedelta(days=days)

        # Execuções concluídas nos últimos N dias
        q_total_exec_30d = (
            select(func.count(ExecucaoTeste.id))
            .where(ExecucaoTeste.updated_at >= cutoff_date)
            .where(ExecucaoTeste.status_geral.in_([StatusExecucaoEnum.fechado, StatusExecucaoEnum.falha, StatusExecucaoEnum.bloqueado]))
        )

        # Testadores ativos no período (quem executou pelo menos 1)
        q_active_testers = (
            select(func.count(func.distinct(ExecucaoTeste.responsavel_id)))
            .where(ExecucaoTeste.updated_at >= cutoff_date)
            .where(ExecucaoTeste.status_geral.in_([StatusExecucaoEnum.fechado, StatusExecucaoEnum.falha, StatusExecucaoEnum.bloqueado]))
        )

        # Defeitos relevantes (ALTO/CRITICO) no período
        q_relevants = (
            select(func.count(Defeito.id))
            .select_from(Defeito)
            .where(Defeito.created_at >= cutoff_date)
            .where(Defeito.status != StatusDefeitoEnum.fechado)
            .where(Defeito.severidade.in_([SeveridadeDefeitoEnum.alto, SeveridadeDefeitoEnum.critico]))
        )

        # Risco ativo (peso por severidade) - defeitos abertos no período (ou ainda abertos, independente da data)
        # Aqui usamos "status != fechado" para refletir risco ainda vivo.
        q_risco = (
            select(
                func.sum(
                    case(
                        (Defeito.severidade == SeveridadeDefeitoEnum.critico, 3),
                        (Defeito.severidade == SeveridadeDefeitoEnum.alto, 2),
                        (Defeito.severidade == SeveridadeDefeitoEnum.medio, 1),
                        else_=0,
                    )
                )
            )
            .select_from(Defeito)
            .where(Defeito.status != StatusDefeitoEnum.fechado)
        )

        # Tempo médio para registrar defeito (horas) - quando dá para calcular
        q_tempo_registro = (
            select(
                func.avg(func.extract('epoch', (Defeito.created_at - ExecucaoTeste.updated_at)) / 3600.0)
            )
            .select_from(Defeito)
            .join(Defeito.execucao)
            .where(Defeito.created_at >= cutoff_date)
            .where(ExecucaoTeste.updated_at.isnot(None))
        )

        total_exec_30d = (await self.db.execute(q_total_exec_30d)).scalar() or 0
        active_testers = (await self.db.execute(q_active_testers)).scalar() or 0
        relevants = (await self.db.execute(q_relevants)).scalar() or 0
        risco = (await self.db.execute(q_risco)).scalar() or 0
        tempo_med = (await self.db.execute(q_tempo_registro)).scalar()

        # efetividade = defeitos relevantes por execução (quanto o time encontra de coisa séria por execução)
        efetividade = round((relevants / total_exec_30d), 2) if total_exec_30d > 0 else 0.0
        exec_por_testador = round((total_exec_30d / active_testers), 1) if active_testers > 0 else float(total_exec_30d)
        tempo_med_horas = round(max(0.0, float(tempo_med or 0.0)), 2)

        return {
            "efetividade": efetividade,
            "risco_ativo": int(risco or 0),
            "execucoes_por_testador_30d": exec_por_testador,
            "tempo_medio_registro_horas": tempo_med_horas,
        }

    async def get_tester_performance_stats(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """4 métricas individuais (testador) focadas em desempenho."""
        cutoff_date = datetime.now() - timedelta(days=days)

        # Execuções concluídas no período
        q_exec_30d = (
            select(func.count(ExecucaoTeste.id))
            .where(ExecucaoTeste.responsavel_id == user_id)
            .where(ExecucaoTeste.updated_at >= cutoff_date)
            .where(ExecucaoTeste.status_geral.in_([StatusExecucaoEnum.fechado, StatusExecucaoEnum.falha, StatusExecucaoEnum.bloqueado]))
        )

        # Defeitos relevantes atribuídos ao testador (pela execução)
        q_impacto = (
            select(func.count(Defeito.id))
            .select_from(Defeito)
            .join(Defeito.execucao)
            .where(ExecucaoTeste.responsavel_id == user_id)
            .where(Defeito.created_at >= cutoff_date)
            .where(Defeito.status != StatusDefeitoEnum.fechado)
            .where(Defeito.severidade.in_([SeveridadeDefeitoEnum.alto, SeveridadeDefeitoEnum.critico]))
        )

        # Severidade média ponderada dos defeitos do período
        q_sev_media = (
            select(
                func.avg(
                    case(
                        (Defeito.severidade == SeveridadeDefeitoEnum.critico, 4),
                        (Defeito.severidade == SeveridadeDefeitoEnum.alto, 3),
                        (Defeito.severidade == SeveridadeDefeitoEnum.medio, 2),
                        (Defeito.severidade == SeveridadeDefeitoEnum.baixo, 1),
                        else_=0,
                    )
                )
            )
            .select_from(Defeito)
            .join(Defeito.execucao)
            .where(ExecucaoTeste.responsavel_id == user_id)
            .where(Defeito.created_at >= cutoff_date)
        )

        # Tempo médio de registro (horas)
        q_tempo_registro = (
            select(
                func.avg(func.extract('epoch', (Defeito.created_at - ExecucaoTeste.updated_at)) / 3600.0)
            )
            .select_from(Defeito)
            .join(Defeito.execucao)
            .where(ExecucaoTeste.responsavel_id == user_id)
            .where(Defeito.created_at >= cutoff_date)
            .where(ExecucaoTeste.updated_at.isnot(None))
        )

        exec_30d = (await self.db.execute(q_exec_30d)).scalar() or 0
        impacto = (await self.db.execute(q_impacto)).scalar() or 0
        sev_media = (await self.db.execute(q_sev_media)).scalar()
        tempo_med = (await self.db.execute(q_tempo_registro)).scalar()

        return {
            "execucoes_30d": int(exec_30d),
            "impacto_relevante": int(impacto),
            "severidade_media": round(float(sev_media or 0.0), 2),
            "tempo_medio_registro_horas": round(max(0.0, float(tempo_med or 0.0)), 2),
        }

    async def get_team_stats_aggregates(self) -> Dict[str, Any]:
        # 1. total de execucoes 
        q_total_exec = select(func.count(ExecucaoTeste.id)).where(
            ExecucaoTeste.status_geral.in_([StatusExecucaoEnum.fechado, StatusExecucaoEnum.falha, StatusExecucaoEnum.bloqueado])
        )
        
        # 2. execucoes aprovadas
        q_passed = select(func.count(ExecucaoTeste.id)).where(ExecucaoTeste.status_geral == StatusExecucaoEnum.fechado)
        
        # 3. total de defeitos
        q_defects = select(func.count(Defeito.id))

        total_exec = (await self.db.execute(q_total_exec)).scalar() or 0
        passed = (await self.db.execute(q_passed)).scalar() or 0
        total_defects = (await self.db.execute(q_defects)).scalar() or 0

        return {
            "total_executions": total_exec,
            "passed_executions": passed,
            "total_defects": total_defects
        }

    async def get_user_stats_aggregates(self, user_id: int) -> Dict[str, Any]:
    
        q_bugs = (
            select(func.count(Defeito.id))
            .select_from(Defeito)
            .join(Defeito.execucao)
            .where(ExecucaoTeste.responsavel_id == user_id)
        )

        q_execs = select(func.count(ExecucaoTeste.id)).where(
            ExecucaoTeste.responsavel_id == user_id,
            ExecucaoTeste.status_geral.in_([StatusExecucaoEnum.fechado, StatusExecucaoEnum.falha, StatusExecucaoEnum.bloqueado])
        )

        q_blocked = select(func.count(ExecucaoTeste.id)).where(
            ExecucaoTeste.responsavel_id == user_id,
            ExecucaoTeste.status_geral == StatusExecucaoEnum.bloqueado
        )

        reported_bugs = (await self.db.execute(q_bugs)).scalar() or 0
        total_execs = (await self.db.execute(q_execs)).scalar() or 0
        blocked_execs = (await self.db.execute(q_blocked)).scalar() or 0

        return {
            "reported_bugs": reported_bugs,
            "total_executions": total_execs,
            "blocked_executions": blocked_execs
        }
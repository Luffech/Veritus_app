from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.testing import CasoTeste, ExecucaoTeste, StatusExecucaoEnum, StatusPassoEnum, ExecucaoPasso

async def seed_execucoes(session: AsyncSession):
    result = await session.execute(
        select(CasoTeste).where(CasoTeste.status == 'ativo').options(selectinload(CasoTeste.passos))
    )
    cases = result.scalars().all()

    if not cases:
        print("Nenhum caso de teste encontrado para gerar execuções.")
        return

    count_exec = 0

    for case in cases:
        result_exec = await session.execute(
            select(ExecucaoTeste).where(
                ExecucaoTeste.caso_teste_id == case.id,
                ExecucaoTeste.ciclo_teste_id == case.ciclo_id
            )
        )
        exec = result_exec.scalars().first()

        if not exec and case.ciclo_id and case.responsavel_id:
            new_exec = ExecucaoTeste(
                ciclo_teste_id=case.ciclo_id,
                caso_teste_id=case.id,
                responsavel_id=case.responsavel_id,
                status_geral=StatusExecucaoEnum.pendente
            )
            session.add(new_exec)
            await session.flush()

            for step_temp in case.passos:
                new_step = ExecucaoPasso(
                    execucao_teste_id=new_exec.id,
                    passo_caso_teste_id=step_temp.id,
                    status=StatusPassoEnum.pendente,
                    resultado_obtido=""
                )
                session.add(new_step)
            
            count_exec += 1

    await session.flush()
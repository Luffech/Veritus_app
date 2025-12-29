from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import delete, update as sqlalchemy_update
from typing import Sequence, Optional

from app.models.testing import CasoTeste, PassoCasoTeste, ExecucaoTeste, StatusExecucaoEnum, ExecucaoPasso, Defeito
from app.models.usuario import Usuario
from app.schemas.caso_teste import CasoTesteCreate

class CasoTesteRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Busca rápida para validações.
    async def get_by_nome_projeto(self, nome: str, projeto_id: int) -> Optional[CasoTeste]:
        query = select(CasoTeste).where(CasoTeste.nome == nome, CasoTeste.projeto_id == projeto_id)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    # Lista para a grid principal, carregando os passos e quem é o responsável.
    async def get_by_projeto(self, projeto_id: int) -> Sequence[CasoTeste]:
        query = (
            select(CasoTeste)
            .options(
                selectinload(CasoTeste.passos),
                selectinload(CasoTeste.responsavel).selectinload(Usuario.nivel_acesso)
            )
            .where(CasoTeste.projeto_id == projeto_id)
            .order_by(CasoTeste.id.desc())
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    # Criação complexa: salva o caso, os passos e já cria a execução se o usuário pediu alocação.
    async def create(self, projeto_id: int, caso_data: CasoTesteCreate) -> CasoTeste:
        # 1. Cria a "Cabeça" do Caso de Teste
        db_caso = CasoTeste(
            projeto_id=projeto_id,
            **caso_data.model_dump(exclude={'passos', 'ciclo_id'}) 
        )
        self.db.add(db_caso)
        await self.db.flush() 

        # 2. Salva os Passos (Instruções do teste)
        passos_objs = []
        if caso_data.passos:
            passos_objs = [
                PassoCasoTeste(caso_teste_id=db_caso.id, **p.model_dump()) 
                for p in caso_data.passos
            ]
            self.db.add_all(passos_objs)
            await self.db.flush() # Flush aqui é vital para ter os IDs dos passos logo abaixo
        
        # 3. Lógica de Auto-Alocação: Se veio ciclo e responsável, já joga na esteira de execução.
        if caso_data.ciclo_id and caso_data.responsavel_id:
            nova_execucao = ExecucaoTeste(
                ciclo_teste_id=caso_data.ciclo_id,
                caso_teste_id=db_caso.id,
                responsavel_id=caso_data.responsavel_id,
                status_geral=StatusExecucaoEnum.pendente
            )
            self.db.add(nova_execucao)
            await self.db.flush() 

            # Replica os passos da receita para a execução (snapshot para preencher resultado depois)
            if passos_objs:
                passos_execucao = [
                    ExecucaoPasso(
                        execucao_teste_id=nova_execucao.id,
                        passo_caso_teste_id=p.id, # Link vital para saber de qual passo veio
                        status="pendente",
                        resultado_obtido=""
                    )
                    for p in passos_objs
                ]
                self.db.add_all(passos_execucao)

        # 4. Efetiva tudo no banco de uma vez
        await self.db.commit()
        
        return await self.get_by_id(db_caso.id)

    # Helper para buscar um caso único com todas as relações necessárias.
    async def get_by_id(self, caso_id: int) -> Optional[CasoTeste]:
        query = (
            select(CasoTeste)
            .options(
                selectinload(CasoTeste.passos),
                selectinload(CasoTeste.responsavel).selectinload(Usuario.nivel_acesso)
            )
            .where(CasoTeste.id == caso_id)
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    # Atualização inteligente: lida com edição de campos simples e sincronização da lista de passos.
    async def update(self, caso_id: int, dados: dict) -> Optional[CasoTeste]:
        passos_data = dados.pop('passos', None)

        # 1. Update simples (nome, descrição, prioridade)
        if dados:
            await self.db.execute(
                sqlalchemy_update(CasoTeste).where(CasoTeste.id == caso_id).values(**dados)
            )

        # 2. Sincronização de Passos (Diff entre o que veio e o que tá no banco)
        if passos_data is not None:
            # A. IDs que o frontend mandou manter/atualizar
            incoming_ids = [p['id'] for p in passos_data if 'id' in p and p['id']]
            
            # B. Remove passos que existiam no banco mas sumiram da lista do front
            if incoming_ids:
                await self.db.execute(
                    delete(PassoCasoTeste)
                    .where(PassoCasoTeste.caso_teste_id == caso_id)
                    .where(PassoCasoTeste.id.notin_(incoming_ids))
                )
            else:
                # Se a lista não tem IDs, ou são todos novos ou o usuário limpou tudo.
                if not passos_data: 
                     await self.db.execute(delete(PassoCasoTeste).where(PassoCasoTeste.caso_teste_id == caso_id))

            # C. Atualiza existentes ou Insere novos
            for passo in passos_data:
                if 'id' in passo and passo['id']:
                    await self.db.execute(
                        sqlalchemy_update(PassoCasoTeste)
                        .where(PassoCasoTeste.id == passo['id'])
                        .values(acao=passo['acao'], resultado_esperado=passo['resultado_esperado'], ordem=passo['ordem'])
                    )
                else:
                    self.db.add(PassoCasoTeste(
                        caso_teste_id=caso_id,
                        acao=passo['acao'],
                        resultado_esperado=passo['resultado_esperado'],
                        ordem=passo['ordem']
                    ))

        await self.db.commit()
        self.db.expire_all() # Força o reload dos dados atualizados
        return await self.get_by_id(caso_id)

    # Exclusão profunda: limpa execuções, passos e defeitos vinculados antes de matar o caso.
    async def delete(self, caso_id: int) -> bool:
        execs = await self.db.execute(select(ExecucaoTeste.id).where(ExecucaoTeste.caso_teste_id == caso_id))
        execs_ids = execs.scalars().all()

        if execs_ids:
            # Limpeza em cascata manual (pra garantir que o SQLAlchemy não reclame de FK)
            await self.db.execute(delete(ExecucaoPasso).where(ExecucaoPasso.execucao_teste_id.in_(execs_ids)))
            await self.db.execute(delete(Defeito).where(Defeito.execucao_teste_id.in_(execs_ids)))
            await self.db.execute(delete(ExecucaoTeste).where(ExecucaoTeste.id.in_(execs_ids)))

        await self.db.execute(delete(PassoCasoTeste).where(PassoCasoTeste.caso_teste_id == caso_id))
        result = await self.db.execute(delete(CasoTeste).where(CasoTeste.id == caso_id))
        await self.db.commit()
        return result.rowcount > 0
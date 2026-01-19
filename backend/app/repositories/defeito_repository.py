from typing import Sequence, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, aliased
from sqlalchemy import desc

from app.models.testing import Defeito, ExecucaoTeste, CasoTeste, ExecucaoPasso
from app.models.projeto import Projeto
from app.models.usuario import Usuario
from app.schemas.defeito import DefeitoCreate, DefeitoUpdate

class DefeitoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Helper para carregar relacionamentos complexos (usado no create/update/get_one)
    def _get_load_options(self):
        return [
            # Traz a árvore: Defeito -> Execução -> Caso -> [Passos, Projeto, Ciclo]
            selectinload(Defeito.execucao).selectinload(ExecucaoTeste.caso_teste).options(
                selectinload(CasoTeste.passos),
                selectinload(CasoTeste.projeto),
                selectinload(CasoTeste.ciclo)
            ),
            # Traz o ciclo da execução
            selectinload(Defeito.execucao).selectinload(ExecucaoTeste.ciclo),
            # Traz quem executou e o cargo
            selectinload(Defeito.execucao).selectinload(ExecucaoTeste.responsavel).selectinload(Usuario.nivel_acesso),
            # Traz o passo onde deu erro
            selectinload(Defeito.execucao).selectinload(ExecucaoTeste.passos_executados).selectinload(ExecucaoPasso.passo_template)
        ]

    async def create(self, dados: DefeitoCreate) -> Defeito:
        # 1. Blindagem: Evita duplicidade se já houver bug aberto nesta execução com mesmo título
        query_existente = (
            select(Defeito)
            .options(*self._get_load_options()) 
            .where(
                Defeito.execucao_teste_id == dados.execucao_teste_id,
                Defeito.titulo == dados.titulo,
                Defeito.status != 'fechado'
            )
        )
        
        result = await self.db.execute(query_existente)
        defeito_existente = result.scalars().first()

        if defeito_existente:
            return defeito_existente

        # 2. Criação
        novo_defeito = Defeito(**dados.dict())
        self.db.add(novo_defeito)
        await self.db.commit()
        
        # 3. Recarrega com relacionamentos para o frontend não quebrar
        query_novo = (
            select(Defeito)
            .options(*self._get_load_options()) 
            .where(Defeito.id == novo_defeito.id)
        )
        result = await self.db.execute(query_novo)
        return result.scalars().first()

    # Este método retorna a lista detalhada para o Dashboard/Tabela
    async def get_all_with_details(self, responsavel_id: Optional[int] = None):
        # Aliases para distinguir quem executou o teste de quem é dono do projeto
        Runner = aliased(Usuario)  
        Manager = aliased(Usuario) 

        query = (
            select(
                Defeito.id,
                Defeito.titulo,
                Defeito.descricao,
                Defeito.status,
                Defeito.severidade,
                Defeito.created_at,
                Defeito.evidencias,
                Defeito.logs_erro,
                Defeito.execucao_teste_id,
                
                # Campos Extras (Flattened)
                CasoTeste.nome.label('caso_teste_nome'),
                Projeto.nome.label('projeto_nome'),
                Runner.nome.label('responsavel_teste_nome'),   # Nome do Runner
                Manager.nome.label('responsavel_projeto_nome') # Nome do Gerente
            )
            .join(ExecucaoTeste, Defeito.execucao_teste_id == ExecucaoTeste.id)
            .join(CasoTeste, ExecucaoTeste.caso_teste_id == CasoTeste.id)
            .join(Projeto, CasoTeste.projeto_id == Projeto.id)
            
            # Join para achar o Runner (ligado à Execução)
            .outerjoin(Runner, ExecucaoTeste.responsavel_id == Runner.id)
            
            # Join para achar o Manager (ligado ao Projeto)
            .outerjoin(Manager, Projeto.responsavel_id == Manager.id)
            
            .order_by(desc(Defeito.id))
        )

        # Filtro opcional (se o Runner quiser ver só os dele)
        if responsavel_id:
            query = query.where(ExecucaoTeste.responsavel_id == responsavel_id)

        result = await self.db.execute(query)
        
        # Converte Row objects em Dicionários compatíveis com JSON
        return result.mappings().all()

    async def get_by_id(self, id: int) -> Optional[Defeito]:
        query = (
            select(Defeito)
            .options(*self._get_load_options())
            .where(Defeito.id == id)
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def update(self, id: int, dados: DefeitoUpdate) -> Optional[Defeito]:
        defeito = await self.get_by_id(id)
        if not defeito:
            return None
            
        update_data = dados.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(defeito, key, value)
            
        await self.db.commit()
        
        # Recarrega para garantir que os dados atualizados voltem completos
        return await self.get_by_id(id)

    async def delete(self, id: int) -> bool:
        defeito = await self.db.get(Defeito, id)
        if defeito:
            await self.db.delete(defeito)
            await self.db.commit()
            return True
        return False
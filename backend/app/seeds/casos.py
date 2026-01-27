from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.projeto import Projeto
from app.models.usuario import Usuario
from app.models.testing import CicloTeste, CasoTeste, PassoCasoTeste, PrioridadeEnum, StatusCasoTesteEnum

async def seed_casos(session: AsyncSession):
    # Projeto
    project = (await session.execute(select(Projeto).where(Projeto.nome == "Inventário Físico"))).scalars().first()
    
    # Buscar todos os utilizadores (testers) criados no seed de usuários
    usernames_testers = ['igor', 'diego', 'luiz', 'isaque', 'kevin']
    result_users = await session.execute(select(Usuario).where(Usuario.username.in_(usernames_testers)))
    testers = result_users.scalars().all()

    if not project or not testers:
        return

    # Definição dos Dados dos Casos
    dados_casos = [
        {
            "ciclo": "Preparação da Contagem",
            "casos": [
                {
                    "nome": "Definir parâmetros de contagem",
                    "prioridade": PrioridadeEnum.alta,
                    "passos": [
                        ("Acessar transação de configuração", "Tela de parâmetros aberta"),
                        ("Selecionar planta e depósito", "Depósito selecionado"),
                        ("Salvar parâmetros", "Mensagem de sucesso")
                    ]
                },
                {
                    "nome": "Definir o intervalo de contagem",
                    "prioridade": PrioridadeEnum.media,
                    "passos": [("Inserir datas de bloqueio", "Datas aceitas pelo sistema")]
                },
                {
                    "nome": "Criar o processo de inventário físico",
                    "prioridade": PrioridadeEnum.alta,
                    "passos": [("Executar transação MI01", "Documento de inventário criado")]
                }
            ]
        },
        # Ciclo 2
        {
            "ciclo": "Execução da Contagem",
            "casos": [
                {
                    "nome": "Gerar e imprimir as fichas de contagem",
                    "prioridade": PrioridadeEnum.media,
                    "passos": [("Acessar MI21 e imprimir", "PDF gerado corretamente")]
                },
                {
                    "nome": "Bloquear o estoque para movimentação",
                    "prioridade": PrioridadeEnum.alta,
                    "passos": [("Ativar Posting Block", "Flag ativada"), ("Tentar MIGO de saída", "Erro de bloqueio exibido")]
                },
                {
                    "nome": "Lançar dados da primeira contagem",
                    "prioridade": PrioridadeEnum.alta,
                    "passos": [("Lançar contagem MI04", "Contagem registrada")]
                },
                {
                     "nome": "Lançar dados da segunda contagem",
                     "prioridade": PrioridadeEnum.media,
                     "passos": [("Criar documento de recontagem MI11", "Documento gerado"), ("Lançar nova contagem", "Valor atualizado")]
                }
            ]
        },
        # Ciclo 3
        {
            "ciclo": "Análise e Ajuste",
            "casos": [
                {
                    "nome": "Gerar relatório de itens com divergência",
                    "prioridade": PrioridadeEnum.alta,
                    "passos": [("Executar MI20", "Lista de diferenças exibida")]
                },
                {
                    "nome": "Solicitar aprovação de ajuste",
                    "prioridade": PrioridadeEnum.alta,
                    "passos": [("Enviar lista para financeiro", "Aprovação recebida")]
                },
                {
                    "nome": "Realizar o ajuste de inventário",
                    "prioridade": PrioridadeEnum.alta,
                    "passos": [("Postar diferenças MI07", "Documento de material gerado e estoque atualizado")]
                }
            ]
        },
        # Ciclo 4
        {
            "ciclo": "Finalização",
            "casos": [
                {
                    "nome": "Arquivar o inventário físico",
                    "prioridade": PrioridadeEnum.baixa,
                    "passos": [
                        ("Verificar status do documento", "Status 'Contagem postada'"),
                        ("Executar rotina de arquivamento", "Documento movido para histórico")
                    ]
                },
                {
                    "nome": "Liberar o estoque para movimentação",
                    "prioridade": PrioridadeEnum.alta,
                    "passos": [
                        ("Verificar remoção automática de bloqueio", "Flag de bloqueio inativa"),
                        ("Realizar movimentação de teste (MIGO)", "Movimentação processada com sucesso")
                    ]
                }
            ]
        }
    ]

    tester_idx = 0

    for grupo in dados_casos:
        # Busca o ID do ciclo correspondente no banco
        ciclo_db = (await session.execute(
            select(CicloTeste).where(CicloTeste.nome == grupo["ciclo"], CicloTeste.projeto_id == project.id)
        )).scalars().first()

        if not ciclo_db:
            continue

        for caso_data in grupo["casos"]:
            caso_existente = (await session.execute(
                select(CasoTeste).where(CasoTeste.nome == caso_data["nome"], CasoTeste.projeto_id == project.id)
            )).scalars().first()

            if not caso_existente:
                tester_atual = testers[tester_idx % len(testers)]
                tester_idx += 1

                novo_caso = CasoTeste(
                    nome=caso_data["nome"],
                    descricao=f"Caso de teste para: {caso_data['nome']}",
                    projeto_id=project.id,
                    ciclo_id=ciclo_db.id,
                    responsavel_id=tester_atual.id,
                    prioridade=caso_data["prioridade"],
                    status=StatusCasoTesteEnum.ativo,
                    pre_condicoes="Acesso ao SAP MM liberado.",
                    criterios_aceitacao="Operação realizada sem erros de sistema."
                )
                session.add(novo_caso)
                await session.flush()

                # Adicionar Passos
                for idx, (acao, res) in enumerate(caso_data["passos"], start=1):
                    passo = PassoCasoTeste(
                        caso_teste_id=novo_caso.id,
                        ordem=idx,
                        acao=acao,
                        resultado_esperado=res
                    )
                    session.add(passo)
                
    await session.flush()
    print("Tests seeded.")
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from random import randint
from app.models.projeto import Projeto
from app.models.usuario import Usuario
from app.models.testing import CicloTeste, CasoTeste, PassoCasoTeste, PrioridadeEnum, StatusCasoTesteEnum

async def seed_casos(session: AsyncSession):
    # === SAP Projects === #
    project_inv = (await session.execute(select(Projeto).where(Projeto.nome == "Inventário Físico"))).scalars().first()

    # === Veritus Projects === #
    project_security = (await session.execute(select(Projeto).where(Projeto.nome == "Security Core"))).scalars().first()
    project_admin = (await session.execute(select(Projeto).where(Projeto.nome == "Admin Panel"))).scalars().first()
    project_qa = (await session.execute(select(Projeto).where(Projeto.nome == "QA Planner"))).scalars().first()
    project_test = (await session.execute(select(Projeto).where(Projeto.nome == "Test Player"))).scalars().first()
    project_analytics = (await session.execute(select(Projeto).where(Projeto.nome == "Analytics"))).scalars().first()
    
    # === Testers === #
    usernames_testers = ['igor', 'diego', 'luiz', 'isaque', 'kevin']
    result_users = await session.execute(select(Usuario).where(Usuario.username.in_(usernames_testers)))
    testers = result_users.scalars().all()

    # === SAP Cases === #
    if not project_inv or not testers:
        return

    dados_casos_inv = [
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

    tester_idx_inv = 0

    for grupo in dados_casos_inv:
        # Busca o ID do ciclo correspondente no banco
        ciclo_inv_db = (await session.execute(
            select(CicloTeste).where(CicloTeste.nome == grupo["ciclo"], CicloTeste.projeto_id == project_inv.id)
        )).scalars().first()

        if not ciclo_inv_db:
            continue

        for caso_data in grupo["casos"]:
            caso_existente_inv = (await session.execute(
                select(CasoTeste).where(CasoTeste.nome == caso_data["nome"], CasoTeste.projeto_id == project_inv.id)
            )).scalars().first()

            if not caso_existente_inv:
                tester_atual_inv = testers[tester_idx_inv % len(testers)]
                tester_idx_inv += 1

                novo_caso_inv = CasoTeste(
                    nome=caso_data["nome"],
                    descricao=f"Caso de teste para: {caso_data['nome']}",
                    projeto_id=project_inv.id,
                    ciclo_id=ciclo_inv_db.id,
                    responsavel_id=tester_atual_inv.id,
                    prioridade=caso_data["prioridade"],
                    status=StatusCasoTesteEnum.ativo,
                    pre_condicoes="Acesso ao SAP MM liberado.",
                    criterios_aceitacao="Operação realizada sem erros de sistema."
                )
                session.add(novo_caso_inv)
                await session.flush()

                # Adicionar Passos
                for idx, (acao, res) in enumerate(caso_data["passos"], start=1):
                    passo_inv = PassoCasoTeste(
                        caso_teste_id=novo_caso_inv.id,
                        ordem=idx,
                        acao=acao,
                        resultado_esperado=res
                    )
                    session.add(passo_inv)
                
    # === Veritus Cases === #
    # Security Project
    if not project_security or not testers:
        return

    ciclo_security = "Ciclo de Blindagem e Autenticação v1"
    ciclo_security_db = (await session.execute(
        select(CicloTeste).where(CicloTeste.nome == ciclo_security, CicloTeste.projeto_id == project_security.id)
    )).scalars().first()

    if not ciclo_security_db:
        return

    dados_casos_security = [
        {
            "nome": "Login com Sucesso",
            "prioridade": PrioridadeEnum.alta,
            "objetivo": "Validar se um usuário ativo consegue obter um token de sessão válido e acessar a área restrita",
            "requisitos": "Existir um usuário com status Ativo e saber suas credenciais",
            "passos": [
                ("Acessar a rota /login", "Tela de login carregada"),
                ("Inserir email e senha corretos", "Campos preenchidos"),
                ("Clicar em Entrar", "Redirecionamento para /dashboard e mensagem de boas-vindas")
            ]
        },
        {
            "nome": "Bloqueio de Senha Incorreta",
            "prioridade": PrioridadeEnum.media,
            "objetivo": "Garantir que o sistema nega acesso e fornece fedback visual adequado sem expor detalhes de segurança",
            "requisitos": "Estar na tela de login",
            "passos": [
                ("Inserir um email válido cadastrado", "Campo preenchido"),
                ("Inserir uma senha incorreta", "Campo preenchido"),
                ("Clicar em Entrar", "O sistema permanece na tela de login e exibe Snackbar: Credenciais Inválidas"),
            ]
        },
        {
            "nome": "Logout e Segurança de Sessão",
            "prioridade": PrioridadeEnum.alta,
            "objetivo": "Verificar se o token JWT é removido e se o histórico de navegação não permite retorno à área logada",
            "requisitos": "Usuário estar logado no Dashboard",
            "passos": [
                ("Clicar no botão Sair", "Redirecionamento imediato para /login"),
                ("Clicar no botão Voltar do navegador", "O usuário não deve ver o Dashboard, deve ser forçado a ver o Login novamente")
            ]
        },
    ]

    for caso_data in dados_casos_security:
        caso_existente_security = (await session.execute(
            select(CasoTeste).where(CasoTeste.nome == caso_data["nome"], CasoTeste.projeto_id == project_security.id)
        )).scalars().first()

        if not caso_existente_security:
            tester_atual_security = testers[randint(0, len(testers)-1)]

            novo_caso_security = CasoTeste(
                nome=caso_data["nome"],
                descricao=f"Caso de teste para: {caso_data['nome']}",
                projeto_id=project_security.id,
                ciclo_id=ciclo_security_db.id,
                responsavel_id=tester_atual_security.id,
                prioridade=caso_data["prioridade"],
                status=StatusCasoTesteEnum.ativo,
                pre_condicoes=caso_data["requisitos"],
                criterios_aceitacao=caso_data["objetivo"]
            )
            session.add(novo_caso_security)
            await session.flush()

            for idx, (acao, res) in enumerate(caso_data["passos"], start=1):
                passo_security = PassoCasoTeste(
                    caso_teste_id=novo_caso_security.id,
                    ordem=idx,
                    acao=acao,
                    resultado_esperado=res
                )
                session.add(passo_security)
    
    # Admin Project
    if not project_admin or not testers:
        return

    ciclo_admin = "Ciclo de Regressão Administrativa"
    ciclo_admin_db = (await session.execute(
        select(CicloTeste).where(CicloTeste.nome == ciclo_admin, CicloTeste.projeto_id == project_admin.id)
    )).scalars().first()

    if not ciclo_admin_db:
        return

    dados_casos_admin = [
        {
            "nome": "Cadastro de Novo Usuário Tester",
            "prioridade": PrioridadeEnum.alta,
            "objetivo": "Validar o formulário de criação de usuários e a persistência no banco de dados",
            "requisitos": "Estar logado com perfil de Admin",
            "passos": [
                ("Acessar menu Acessos e clicar em Novo Usuário", "Modal de cadastro aberto"),
                ("Preencher campos do formulário, com nivel de acesso Tester", "Formulário validado (botão Salvar habilitado)"),
                ("Clicar em Salvar", "Modal fecha, notificação de sucesso aparece e o novo usuário é listado na tabela")
            ]
        },
        {
            "nome": "Vinculo Hierárquico de Projetos",
            "prioridade": PrioridadeEnum.media,
            "objetivo": "Garantir a integridade referencial: Um Projeto só existe dentro de um Módulo, que existe dentro de um Sistema",
            "requisitos": "Ter pelo menos 1 Sistema e 1 Módulo cadastrados",
            "passos": [
                ("Acessar menu Projetos e clicar em Novo Projeto", "Modal de cadastro aberto"),
                ("Selecionar um Sistema no dropdown", "O dropdown de Módulos deve carregar"),
                ("Selecionar um Módulo e preencher o nome do Projeto. Salvar.", "Projeto criado com os vínculos corretos."),
            ]
        }
    ]

    for caso_data in dados_casos_admin:
        caso_existente_admin = (await session.execute(
            select(CasoTeste).where(CasoTeste.nome == caso_data["nome"], CasoTeste.projeto_id == project_admin.id)
        )).scalars().first()

        if not caso_existente_admin:
            tester_atual_admin = testers[randint(0, len(testers)-1)]

            novo_caso_admin = CasoTeste(
                nome=caso_data["nome"],
                descricao=f"Caso de teste para: {caso_data['nome']}",
                projeto_id=project_admin.id,
                ciclo_id=ciclo_admin_db.id,
                responsavel_id=tester_atual_admin.id,
                prioridade=caso_data["prioridade"],
                status=StatusCasoTesteEnum.ativo,
                pre_condicoes=caso_data["requisitos"],
                criterios_aceitacao=caso_data["objetivo"]
            )
            session.add(novo_caso_admin)
            await session.flush()

            for idx, (acao, res) in enumerate(caso_data["passos"], start=1):
                passo_admin = PassoCasoTeste(
                    caso_teste_id=novo_caso_admin.id,
                    ordem=idx,
                    acao=acao,
                    resultado_esperado=res
                )
                session.add(passo_admin)

    # Management Project
    if not project_qa or not testers:
        return

    ciclo_qa = "Ciclo de Validação do Planejamento"
    ciclo_qa_db = (await session.execute(
        select(CicloTeste).where(CicloTeste.nome == ciclo_qa, CicloTeste.projeto_id == project_qa.id)
    )).scalars().first()

    if not ciclo_qa_db:
        return

    dados_casos_qa = [
        {
            "nome": "Criação do Ciclo de Teste",
            "prioridade": PrioridadeEnum.alta,
            "objetivo": "Verificar se o sistema permite criar um Ciclo de Teste com as informações necessárias, preparando o terreno para os testes",
            "requisitos": "Estar no menu Ciclos de Testes",
            "passos": [
                ("Clicar no botão Novo Ciclo", "O modal de cadastro deve abrir"),
                ("Preencher o formulário", "Formulário validado (botão Salvar habilitado)"),
                ("Clicar em Salvar", "Modal fecha, notificação de sucesso aparece e o novo ciclo é listado na tabela")
            ]
        },
        {
            "nome": "Criação de Caso de Teste Detalhado",
            "prioridade": PrioridadeEnum.media,
            "objetivo": "Verificar a capacidade de criar roteiros de teste com múltiplos passos e resultados esperados",
            "requisitos": "Existir um Projeto cadastrado",
            "passos": [
                ("Acessar o menu Casos de Teste e criar novo caso", "O modal de cadastro deve abrir"),
                ("Inserir os dados do Caso e os passos, com Ações e Resultados Esperados", "Caso Salvo")
            ]
        }
    ]

    for caso_data in dados_casos_qa:
        caso_existente_qa = (await session.execute(
            select(CasoTeste).where(CasoTeste.nome == caso_data["nome"], CasoTeste.projeto_id == project_qa.id)
        )).scalars().first()

        if not caso_existente_qa:
            tester_atual_qa = testers[randint(0, len(testers)-1)]

            novo_caso_qa = CasoTeste(
                nome=caso_data["nome"],
                descricao=f"Caso de teste para: {caso_data['nome']}",
                projeto_id=project_qa.id,
                ciclo_id=ciclo_qa_db.id,
                responsavel_id=tester_atual_qa.id,
                prioridade=caso_data["prioridade"],
                status=StatusCasoTesteEnum.ativo,
                pre_condicoes=caso_data["requisitos"],
                criterios_aceitacao=caso_data["objetivo"]
            )
            session.add(novo_caso_qa)
            await session.flush()

            for idx, (acao, res) in enumerate(caso_data["passos"], start=1):
                passo_qa = PassoCasoTeste(
                    caso_teste_id=novo_caso_qa.id,
                    ordem=idx,
                    acao=acao,
                    resultado_esperado=res
                )
                session.add(passo_qa)

    # Runner Project
    if not project_test or not testers:
        return

    ciclo_test = "Ciclo Crítico: Execução e Defeitos (Runner)"
    ciclo_test_db = (await session.execute(
        select(CicloTeste).where(CicloTeste.nome == ciclo_test, CicloTeste.projeto_id == project_test.id)
    )).scalars().first()

    if not ciclo_test_db:
        return

    dados_casos_test = [
        {
            "nome": "Execução",
            "prioridade": PrioridadeEnum.alta,
            "objetivo": "Verificar se o ambiente de execução ExecutionPlayer carrega os dados corretamente",
            "requisitos": "Existir um ciclo atribuído ao usuário",
            "passos": [
                ("Ir em Minhas Tarefas e executar o teste pendente", "O modal principal é liberado"),
                ("Aprovar o primeiro passo", "Status do passo muda visualmente")
            ]
        },
        {
            "nome": "Fluxo de Reprovação e Abertura de Defeito",
            "prioridade": PrioridadeEnum.media,
            "objetivo": "Validar a regra de negócio que obriga a abertura de um defeito ao reprovar um passo",
            "requisitos": "Estar com um teste em andamento",
            "passos": [
                ("Clicar no botão de reprovar um passo", "O modal de Defeito abre automaticamente"),
                ("Tentar fechar o modal ou clicar fora dele sem salvar", "O sistema bloqueia ou rever a reprovação"),
                ("Preencher Título e Descrição do erro simulado", "Campos aceitam input"),
            ]
        },
        {
            "nome": "Upload de Evidência (Imagem)",
            "prioridade": PrioridadeEnum.alta,
            "objetivo": "Testar a integração com o sistema de arquivos para anexos de evidências",
            "requisitos": "Modal de defeito aberto",
            "passos": [
                ("Clicar na área de upload do mod", "Seletor de arquivos do S.O. abre"),
                ("Selecionar uma imagem", "Preview da imagem aparece no modal"),
                ("Clicar em Salvar Defeito", "Defeito salvo, passo marcado como falha, ícone de anexo visível")
            ]
        },
    ]

    for caso_data in dados_casos_test:
        caso_existente_test = (await session.execute(
            select(CasoTeste).where(CasoTeste.nome == caso_data["nome"], CasoTeste.projeto_id == project_test.id)
        )).scalars().first()

        if not caso_existente_test:
            tester_atual_test = testers[randint(0, len(testers)-1)]

            novo_caso_test = CasoTeste(
                nome=caso_data["nome"],
                descricao=f"Caso de teste para: {caso_data['nome']}",
                projeto_id=project_test.id,
                ciclo_id=ciclo_test_db.id,
                responsavel_id=tester_atual_test.id,
                prioridade=caso_data["prioridade"],
                status=StatusCasoTesteEnum.ativo,
                pre_condicoes=caso_data["requisitos"],
                criterios_aceitacao=caso_data["objetivo"]
            )
            session.add(novo_caso_test)
            await session.flush()

            for idx, (acao, res) in enumerate(caso_data["passos"], start=1):
                passo_test = PassoCasoTeste(
                    caso_teste_id=novo_caso_test.id,
                    ordem=idx,
                    acao=acao,
                    resultado_esperado=res
                )
                session.add(passo_test)

    # Analytics Project
    if not project_analytics or not testers:
        return

    ciclo_analytics = "Ciclo de Métricas e Relatórios"
    ciclo_analytics_db = (await session.execute(
        select(CicloTeste).where(CicloTeste.nome == ciclo_analytics, CicloTeste.projeto_id == project_analytics.id)
    )).scalars().first()

    if not ciclo_analytics_db:
        return

    dados_casos_analytics = [
        {
            "nome": "Consistência dos Contadores",
            "prioridade": PrioridadeEnum.alta,
            "objetivo": "Garantir que a finalização de um teste impacta as métricas globais em tempo real",
            "requisitos": "Ter finalizado o Ciclo de Teste anterior",
            "passos": [
                ("Acessar o Dashboard principal", "Carregamento dos widgets"),
                ("Verificar widget Testes Executados", "Número incrementado em uma unidade"),
                ("Verificar widget Defeitos Abertos", "Número incrementado em uma unidade")
            ]
        },
        {
            "nome": "Rastreabilidade do Defeito",
            "prioridade": PrioridadeEnum.media,
            "objetivo": "Verificar se o defeito criado durante a execução contém os metadados corretos para auditoria",
            "requisitos": "Defeito criado anteriormente",
            "passos": [
                ("Acessar lista de Defeitos", "A tela de listagem exibe a tabela com os defeitos cadastrados"),
                ("Clicar para ver detalhes do defeito criado", "O sistema exibe: título correto, passo de origem correto e evidência carregada corretamente")
            ]
        }
    ]

    for caso_data in dados_casos_analytics:
        caso_existente_analytics = (await session.execute(
            select(CasoTeste).where(CasoTeste.nome == caso_data["nome"], CasoTeste.projeto_id == project_analytics.id)
        )).scalars().first()

        if not caso_existente_analytics:
            tester_atual_analytics = testers[randint(0, len(testers)-1)]

            novo_caso_analytics = CasoTeste(
                nome=caso_data["nome"],
                descricao=f"Caso de teste para: {caso_data['nome']}",
                projeto_id=project_analytics.id,
                ciclo_id=ciclo_analytics_db.id,
                responsavel_id=tester_atual_analytics.id,
                prioridade=caso_data["prioridade"],
                status=StatusCasoTesteEnum.ativo,
                pre_condicoes=caso_data["requisitos"],
                criterios_aceitacao=caso_data["objetivo"]
            )
            session.add(novo_caso_analytics)
            await session.flush()

            for idx, (acao, res) in enumerate(caso_data["passos"], start=1):
                passo_analytics = PassoCasoTeste(
                    caso_teste_id=novo_caso_analytics.id,
                    ordem=idx,
                    acao=acao,
                    resultado_esperado=res
                )
                session.add(passo_analytics)

    await session.flush()
    print("Tests seeded.")
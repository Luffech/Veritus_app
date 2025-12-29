import logging
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

# Inicializa o logger para registrar ocorrências internas.
logger = logging.getLogger(__name__)

# Traduz erros de banco (IntegrityError) para respostas HTTP amigáveis.
def tratar_erro_integridade(e: IntegrityError, mensagens_personalizadas: dict[str, str] = None):
    # Extrai e normaliza a mensagem de erro original do banco.
    error_msg = str(e.orig).lower() if e.orig else str(e).lower()
    
    # Procura por palavras-chave específicas para retornar mensagens de erro personalizadas.
    if mensagens_personalizadas:
        for keyword, message in mensagens_personalizadas.items():
            if keyword.lower() in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=message
                )

    # Loga o erro técnico completo para o desenvolvedor investigar depois.
    logger.error(f"Erro de Integridade não mapeado: {e}")
    
    # Retorna um erro genérico de conflito caso não tenha uma mensagem específica mapeada.
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Operação negada devido a conflito de dados (violação de integridade)."
    )
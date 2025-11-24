# backend/Dockerfile

# 1. Argumento de Build: 'false' por padrão
ARG WITH_SAP=false

FROM python:3.11-slim

# 2. Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    dos2unix \
    libpq-dev \
    gcc \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# 3. Define o diretório de trabalho
WORKDIR /code

# 4. Instala dependências Python (SEM pyrfc)
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt

# 5. Copia todo o código-fonte E arquivos opcionais
COPY . .

# 6. Lógica de Instalação Condicional do SAP
#    Este bloco só é executado se WITH_SAP=true
RUN if [ "$WITH_SAP" = "true" ]; then \
      # Verifica se os arquivos necessários existem
      if [ -f "/code/nwrfcsdk.zip" ] && [ -f "/code/requirements-sap.txt" ]; then \
        echo "--- Instalando dependências SAP (pyrfc) ---"; \
        pip install -r /code/requirements-sap.txt; \
        echo "--- Instalando SAP NWRFC SDK ---"; \
        unzip /code/nwrfcsdk.zip -d /usr/local/sap; \
        rm /code/nwrfcsdk.zip; \
      else \
        echo "--- ATENÇÃO: WITH_SAP=true, mas nwrfcsdk.zip ou requirements-sap.txt não encontrados. Pulando. ---"; \
        # O build continua, mas o app vai falhar no runtime se tentar usar o SAP
      fi \
    else \
      echo "--- WITH_SAP=false. Pulando instalação do SAP. ---"; \
    fi

# 7. Define as ENV VARS (inofensivo se o SDK não estiver lá)
ENV SAPNWRFC_HOME=/usr/local/sap/nwrfcsdk
ENV LD_LIBRARY_PATH=$SAPNWRFC_HOME/lib:$LD_LIBRARY_PATH

# 8. Corrige quebras de linha e permissões do entrypoint
RUN dos2unix /code/entrypoint.sh
RUN chmod +x /code/entrypoint.sh

# 9. Expõe a porta
EXPOSE 8000

# 10. Define o ponto de entrada e o comando padrão
ENTRYPOINT ["/code/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
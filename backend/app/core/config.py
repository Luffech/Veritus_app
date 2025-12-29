from pydantic_settings import BaseSettings, SettingsConfigDict
import re

# Gerencia todas as configurações e variáveis de ambiente da aplicação.
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra='ignore')

    # Variáveis para conexão com o banco de dados e segurança (JWT).
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_HOST: str | None = None
    POSTGRES_PORT: int | None = None
    POSTGRES_DB: str | None = None
    
    DATABASE_URL: str | None = None
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Lógica inteligente para montar a URL de conexão com SSL se necessário.
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        url = self.DATABASE_URL
        
        # Se não houver URL completa, tenta montar a local ou usa SQLite em memória.
        if not url:
            if not self.POSTGRES_HOST:
                return "sqlite+aiosqlite:///:memory:"
            
            return (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )

        # Detecta e ajusta configurações de SSL para bancos hospedados em nuvem.
        needs_ssl = "sslmode=require" in url

        url = re.sub(r'[?&]sslmode=[^&]+', '', url)
        url = re.sub(r'[?&]channel_binding=[^&]+', '', url)

        # Garante o uso do driver asyncpg na string de conexão.
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

        # Reaplica o parâmetro SSL se ele estava presente na URL original.
        if needs_ssl:
            separator = "&" if "?" in url else "?"
            if "ssl=" not in url:
                url += f"{separator}ssl=require"

        return url

    # Definições gerais de nome do projeto e prefixo da API.
    PROJECT_NAME: str = "Projeto GE"
    API_V1_STR: str = "/api/v1"

settings = Settings()
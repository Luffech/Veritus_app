from pydantic_settings import BaseSettings, SettingsConfigDict
import re

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra='ignore')

    # Campos Opcionais (evita erro de validação no Render)
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_HOST: str | None = None
    POSTGRES_PORT: int | None = None
    POSTGRES_DB: str | None = None
    
    # URL principal
    DATABASE_URL: str | None = None
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        url = self.DATABASE_URL
        
        # 1. Fallback para ambiente local se não houver URL
        if not url:
            if not self.POSTGRES_HOST:
                return "sqlite+aiosqlite:///:memory:"
            return (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )

        # 2. LIMPEZA DE PARÂMETROS INCOMPATÍVEIS COM ASYNCPG
        # Remove 'sslmode=...' (qualquer valor)
        url = re.sub(r'[?&]sslmode=[^&]+', '', url)
        
        # Remove 'channel_binding=...' (qualquer valor) - CAUSA DO SEU ERRO ATUAL
        url = re.sub(r'[?&]channel_binding=[^&]+', '', url)

        # 3. GARANTIR DRIVER CORRETO E SSL
        # Garante o prefixo postgresql+asyncpg://
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

        # 4. REINSERIR SSL DA FORMA CORRETA
        # O asyncpg exige 'ssl=require' (ou True), não sslmode.
        # Verifica se já tem query params para adicionar com ? ou &
        separator = "&" if "?" in url else "?"
        
        # Evita duplicar se já existir
        if "ssl=" not in url:
            url += f"{separator}ssl=require"

        return url

    # Configurações gerais
    PROJECT_NAME: str = "Projeto GE"
    API_V1_STR: str = "/api/v1"

settings = Settings()
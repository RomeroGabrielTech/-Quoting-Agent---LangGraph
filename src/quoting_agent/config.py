"""
Configuración centralizada del agente
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class Config:
    """Configuración del agente de cotización"""
    
    # LLM Provider Selection
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini").lower()
    
    # Google Gemini
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    GEMINI_TEMPERATURE: float = float(os.getenv("GEMINI_TEMPERATURE", "0"))
    
    # OpenAI (alternativo)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0"))
    
    # ERP
    ERP_API_URL: str = os.getenv("ERP_API_URL", "http://localhost:8000")
    ERP_API_KEY: str = os.getenv("ERP_API_KEY", "")
    ENABLE_MOCK_DATA: bool = os.getenv("ENABLE_MOCK_DATA", "true").lower() == "true"
    
    # Application
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "5"))
    QUOTE_VALIDITY_DAYS: int = int(os.getenv("QUOTE_VALIDITY_DAYS", "30"))
    
    # API Server
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    @classmethod
    def validate(cls) -> None:
        """Valida que la configuración sea correcta según el proveedor"""
        if cls.LLM_PROVIDER == "gemini":
            if not cls.GOOGLE_API_KEY:
                raise ValueError(
                    "GOOGLE_API_KEY no está configurada. "
                    "Obtén una en: https://aistudio.google.com/app/apikey"
                )
        elif cls.LLM_PROVIDER == "openai":
            if not cls.OPENAI_API_KEY:
                raise ValueError(
                    "OPENAI_API_KEY no está configurada. "
                    "Obtén una en: https://platform.openai.com/api-keys"
                )
        else:
            raise ValueError(
                f"LLM_PROVIDER inválido: {cls.LLM_PROVIDER}. "
                f"Usa 'gemini' o 'openai'"
            )
    
    @classmethod
    def get_llm_config(cls) -> Dict[str, Any]:
        """Retorna la configuración del LLM seleccionado"""
        if cls.LLM_PROVIDER == "gemini":
            return {
                "provider": "gemini",
                "api_key": cls.GOOGLE_API_KEY,
                "model": cls.GEMINI_MODEL,
                "temperature": cls.GEMINI_TEMPERATURE
            }
        elif cls.LLM_PROVIDER == "openai":
            return {
                "provider": "openai",
                "api_key": cls.OPENAI_API_KEY,
                "model": cls.OPENAI_MODEL,
                "temperature": cls.OPENAI_TEMPERATURE
            }
        else:
            raise ValueError(f"Proveedor no soportado: {cls.LLM_PROVIDER}")
    
    @classmethod
    def is_development(cls) -> bool:
        """Verifica si está en modo desarrollo"""
        return cls.ENVIRONMENT == "development"
    
    @classmethod
    def is_production(cls) -> bool:
        """Verifica si está en modo producción"""
        return cls.ENVIRONMENT == "production"


# Instancia global
config = Config()
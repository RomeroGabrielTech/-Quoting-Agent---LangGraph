"""
Factory para crear instancias de LLM según configuración
"""

from typing import Dict, Any
from langchain_core.language_models import BaseChatModel

from .config import config


def create_llm() -> BaseChatModel:
    """
    Crea una instancia del LLM configurado.
    
    Soporta:
    - Google Gemini (langchain_google_genai)
    - OpenAI (langchain_openai)
    
    Returns:
        Instancia del LLM configurado
        
    Raises:
        ValueError: Si el proveedor no está soportado o falta configuración
        ImportError: Si falta instalar el paquete del proveedor
    """
    
    llm_config = config.get_llm_config()
    provider = llm_config["provider"]
    
    if provider == "gemini":
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError:
            raise ImportError(
                "langchain-google-genai no está instalado. "
                "Instálalo con: pip install langchain-google-genai"
            )
        
        if not llm_config["api_key"]:
            raise ValueError(
                "GOOGLE_API_KEY no está configurada. "
                "Obtén una en: https://aistudio.google.com/app/apikey"
            )
        
        return ChatGoogleGenerativeAI(
            model=llm_config["model"],
            google_api_key=llm_config["api_key"],
            temperature=llm_config["temperature"],
            convert_system_message_to_human=True  # Gemini no soporta system messages
        )
    
    elif provider == "openai":
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            raise ImportError(
                "langchain-openai no está instalado. "
                "Instálalo con: pip install langchain-openai"
            )
        
        if not llm_config["api_key"]:
            raise ValueError(
                "OPENAI_API_KEY no está configurada. "
                "Obtén una en: https://platform.openai.com/api-keys"
            )
        
        return ChatOpenAI(
            model=llm_config["model"],
            api_key=llm_config["api_key"],
            temperature=llm_config["temperature"]
        )
    
    else:
        raise ValueError(
            f"Proveedor LLM no soportado: {provider}. "
            f"Usa 'gemini' o 'openai'"
        )


def get_llm_info() -> Dict[str, Any]:
    """
    Obtiene información sobre el LLM configurado.
    
    Returns:
        Diccionario con información del LLM:
        - provider: Nombre del proveedor
        - model: Modelo configurado
        - temperature: Temperatura configurada
        - configured: Si tiene API key configurada
    """
    
    llm_config = config.get_llm_config()
    
    return {
        "provider": llm_config["provider"],
        "model": llm_config["model"],
        "temperature": llm_config["temperature"],
        "configured": bool(llm_config["api_key"])
    }
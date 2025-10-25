"""
Estado del grafo LangGraph
"""

from typing import TypedDict, Optional, List
from langchain_core.messages import BaseMessage

from .models import QuoteRequest, InventoryResult, Quote


class AgentState(TypedDict):
    """
    Estado compartido entre todos los nodos del grafo.
    
    LangGraph usa TypedDict para definir el estado que se pasa
    entre nodos. Cada nodo puede leer y actualizar este estado.
    """
    
    # Mensajes de conversación
    messages: List[BaseMessage]
    
    # Datos del proceso
    quote_request: Optional[QuoteRequest]
    inventory_result: Optional[InventoryResult]
    quote: Optional[Quote]
    
    # Control de flujo
    needs_clarification: bool
    error_message: Optional[str]
    iteration_count: int


def create_initial_state(user_message: str) -> AgentState:
    """
    Crea el estado inicial del agente con el mensaje del usuario.
    
    Args:
        user_message: Mensaje inicial del usuario
        
    Returns:
        Estado inicial del agente
    """
    from langchain_core.messages import HumanMessage
    
    return AgentState(
        messages=[HumanMessage(content=user_message)],
        quote_request=None,
        inventory_result=None,
        quote=None,
        needs_clarification=False,
        error_message=None,
        iteration_count=0
    )
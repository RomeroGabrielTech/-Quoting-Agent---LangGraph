"""
Construcción del grafo LangGraph para el agente de cotización
"""

from langgraph.graph import StateGraph, END

from .state import AgentState, create_initial_state
from .nodes import (
    parse_request_node,
    check_inventory_node,
    handle_insufficient_stock_node,
    generate_quote_node,
    clarification_node
)
from .edges import (
    should_continue_after_parse,
    should_continue_after_inventory,
    should_end_after_quote,
    should_end_after_clarification
)


def create_quoting_agent() -> StateGraph:
    """
    Crea el grafo del agente de cotización.
    
    Flujo:
    1. parse_request: Extrae información del mensaje
    2. check_inventory: Consulta disponibilidad
    3. generate_quote o handle_insufficient: Genera cotización o maneja problemas
    4. clarification: Pide aclaraciones si es necesario
    
    Returns:
        StateGraph compilado listo para ejecutar
    """
    
    # Crear grafo
    workflow = StateGraph(AgentState)
    
    # Agregar nodos
    workflow.add_node("parse_request", parse_request_node)
    workflow.add_node("check_inventory", check_inventory_node)
    workflow.add_node("generate_quote", generate_quote_node)
    workflow.add_node("handle_insufficient", handle_insufficient_stock_node)
    workflow.add_node("clarification", clarification_node)
    
    # Definir punto de entrada
    workflow.set_entry_point("parse_request")
    
    # Agregar edges condicionales
    workflow.add_conditional_edges(
        "parse_request",
        should_continue_after_parse,
        {
            "check_inventory": "check_inventory",
            "clarification": "clarification"
        }
    )
    
    workflow.add_conditional_edges(
        "check_inventory",
        should_continue_after_inventory,
        {
            "generate_quote": "generate_quote",
            "handle_insufficient": "handle_insufficient"
        }
    )
    
    # Edges finales
    workflow.add_edge("generate_quote", END)
    workflow.add_edge("handle_insufficient", "clarification")
    workflow.add_edge("clarification", END)
    
    # Compilar grafo
    return workflow.compile()


def run_agent(user_message: str) -> AgentState:
    """
    Ejecuta el agente con un mensaje del usuario.
    
    Args:
        user_message: Mensaje del usuario (ej: "Necesito 100 unidades de ABC-45")
        
    Returns:
        Estado final del agente con la respuesta
        
    Example:
        >>> result = run_agent("Necesito 100 unidades de ABC-45")
        >>> print(result["messages"][-1].content)
    """
    
    # Crear estado inicial
    initial_state = create_initial_state(user_message)
    
    # Crear y ejecutar agente
    agent = create_quoting_agent()
    final_state = agent.invoke(initial_state)
    
    return final_state
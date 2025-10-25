"""
Lógica condicional para las transiciones entre nodos (edges)
"""

from .state import AgentState


def should_continue_after_parse(state: AgentState) -> str:
    """
    Decide si continuar después de parsear la solicitud.
    
    Returns:
        "check_inventory" si se parseó correctamente
        "clarification" si necesita clarificación
    """
    if state.get("needs_clarification", False):
        return "clarification"
    
    if state.get("quote_request") is None:
        return "clarification"
    
    return "check_inventory"


def should_continue_after_inventory(state: AgentState) -> str:
    """
    Decide si continuar después de consultar inventario.
    
    Returns:
        "generate_quote" si hay stock disponible
        "handle_insufficient" si hay problemas
    """
    inventory = state.get("inventory_result")
    
    if inventory is None:
        return "handle_insufficient"
    
    # Solo generar cotización si está disponible
    if inventory.status == "available":
        return "generate_quote"
    
    # Cualquier otro status requiere manejo especial
    return "handle_insufficient"


def should_end_after_quote(state: AgentState) -> str:
    """
    Decide si terminar después de generar cotización.
    
    Returns:
        "END" siempre (la cotización es el punto final)
    """
    return "END"


def should_end_after_clarification(state: AgentState) -> str:
    """
    Decide si terminar después de pedir clarificación.
    
    Returns:
        "END" siempre (espera nueva entrada del usuario)
    """
    return "END"
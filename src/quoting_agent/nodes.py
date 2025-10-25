"""
Nodos del grafo LangGraph - cada nodo representa una etapa del proceso
"""

import json
from langchain_core.messages import AIMessage, SystemMessage

from .state import AgentState
from .models import QuoteRequest
from .tools import check_inventory_tool, generate_quote_tool
from .llm_factory import create_llm


# ============================================================================
# NODO 1: Parse Request
# ============================================================================

def parse_request_node(state: AgentState) -> dict:
    """
    Extrae información estructurada del mensaje del usuario usando LLM.
    
    Usa el LLM para interpretar lenguaje natural y extraer:
    - Número de parte
    - Cantidad solicitada
    
    Returns:
        Estado actualizado con quote_request o needs_clarification
    """
    llm = create_llm()
    
    system_prompt = """Eres un asistente de ventas experto. 
    
Extrae información de cotización del mensaje del cliente.

DEBES identificar:
- part_number: Número de parte o producto (ej: "ABC-45", "XYZ-100")
- quantity: Cantidad numérica solicitada

IMPORTANTE: Responde SOLO con JSON válido, sin texto adicional.

Formato exacto:
{"part_number": "ABC-45", "quantity": 100}

Ejemplos:
- "Necesito 100 unidades de ABC-45" → {"part_number": "ABC-45", "quantity": 100}
- "Quiero cotizar 50 piezas XYZ-100" → {"part_number": "XYZ-100", "quantity": 50}
- "Me interesan 25 del producto DEF-200" → {"part_number": "DEF-200", "quantity": 25}
"""
    
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    
    try:
        response = llm.invoke(messages)
        
        # Parsear JSON
        # Limpiar respuesta por si tiene markdown
        content = response.content.strip()
        if content.startswith("```json"):
            content = content.split("```json")[1].split("```")[0].strip()
        elif content.startswith("```"):
            content = content.split("```")[1].split("```")[0].strip()
            
        data = json.loads(content)
        
        # Validar con Pydantic
        quote_request = QuoteRequest(**data)
        
        return {
            "quote_request": quote_request,
            "messages": [AIMessage(
                content=f"✓ Entendido: {quote_request.quantity} unidades de **{quote_request.part_number}**. "
                        f"Verificando disponibilidad..."
            )],
            "needs_clarification": False
        }
        
    except json.JSONDecodeError as e:
        return {
            "messages": [AIMessage(
                content=f"❌ No pude interpretar tu solicitud correctamente.\n\n"
                        f"Por favor especifica:\n"
                        f"- **Número de parte** (ej: ABC-45)\n"
                        f"- **Cantidad** (ej: 100 unidades)\n\n"
                        f"Ejemplo: 'Necesito 100 unidades de ABC-45'"
            )],
            "needs_clarification": True,
            "error_message": f"JSON parse error: {str(e)}"
        }
        
    except Exception as e:
        return {
            "messages": [AIMessage(
                content=f"❌ Error al procesar solicitud: {str(e)}\n\n"
                        f"Intenta reformular tu mensaje con el formato:\n"
                        f"'Necesito [cantidad] unidades de [parte]'"
            )],
            "needs_clarification": True,
            "error_message": str(e)
        }


# ============================================================================
# NODO 2: Check Inventory
# ============================================================================

def check_inventory_node(state: AgentState) -> dict:
    """
    Consulta el inventario usando la herramienta check_inventory_tool.
    
    Returns:
        Estado actualizado con inventory_result
    """
    request = state["quote_request"]
    
    if request is None:
        return {
            "error_message": "No hay solicitud de cotización",
            "needs_clarification": True
        }
    
    # Llamar a la herramienta
    inventory_result = check_inventory_tool(
        part_number=request.part_number,
        quantity=request.quantity
    )
    
    return {
        "inventory_result": inventory_result,
        "messages": [AIMessage(
            content=f"📊 Inventario consultado para {request.part_number}..."
        )]
    }


# ============================================================================
# NODO 3: Handle Insufficient Stock
# ============================================================================

def handle_insufficient_stock_node(state: AgentState) -> dict:
    """
    Maneja casos donde no se puede generar cotización directamente:
    - Stock insuficiente
    - Sin precio disponible
    - Parte no disponible
    
    Sugiere alternativas cuando es posible.
    
    Returns:
        Estado con mensaje de clarificación
    """
    inventory = state["inventory_result"]
    request = state["quote_request"]
    
    if inventory is None or request is None:
        return {"error_message": "Estado inválido en handle_insufficient"}
    
    # Construir mensaje según el problema
    if inventory.status == "unavailable":
        msg = f"❌ Lo siento, **{request.part_number}** no está disponible en nuestro catálogo."
        if inventory.suggested_alternatives:
            msg += f"\n\n💡 ¿Te interesan estas alternativas?\n"
            for alt in inventory.suggested_alternatives:
                msg += f"  • {alt}\n"
    
    elif inventory.status == "insufficient":
        msg = (f"⚠️ Tenemos solo **{inventory.available_stock:,}** unidades de {request.part_number}, "
               f"pero solicitas {request.quantity:,}.\n\n")
        msg += f"**Opciones:**\n"
        msg += f"1. Cotizar las {inventory.available_stock:,} unidades disponibles\n"
        msg += f"2. Esperar reabastecimiento (aprox. {inventory.lead_time_days} días)\n"
        
        if inventory.suggested_alternatives:
            msg += f"\n💡 **Alternativas disponibles:**\n"
            for alt in inventory.suggested_alternatives:
                msg += f"  • {alt}\n"
    
    elif inventory.status == "no_price":
        msg = (f"⚠️ El precio de **{request.part_number}** no está disponible en este momento.\n\n"
               f"Por favor contacta al departamento de ventas para una cotización personalizada:\n"
               f"📧 ventas@tuempresa.com\n"
               f"📞 +1 (555) 123-4567")
    
    else:
        msg = f"❌ No se puede procesar la cotización en este momento."
    
    return {
        "messages": [AIMessage(content=msg)],
        "needs_clarification": True
    }


# ============================================================================
# NODO 4: Generate Quote
# ============================================================================

def generate_quote_node(state: AgentState) -> dict:
    """
    Genera la cotización final usando generate_quote_tool.
    
    Returns:
        Estado con cotización completa formateada
    """
    request = state["quote_request"]
    inventory = state["inventory_result"]
    
    if request is None or inventory is None:
        return {"error_message": "Estado inválido en generate_quote"}
    
    try:
        # Generar cotización
        quote = generate_quote_tool(request, inventory)
        
        # Formatear para display
        formatted_msg = quote.format_for_display()
        formatted_msg += "\n¿Deseas proceder con esta orden?"
        
        return {
            "quote": quote,
            "messages": [AIMessage(content=formatted_msg)],
            "needs_clarification": False
        }
        
    except Exception as e:
        return {
            "messages": [AIMessage(
                content=f"❌ Error al generar cotización: {str(e)}"
            )],
            "needs_clarification": True,
            "error_message": str(e)
        }


# ============================================================================
# NODO 5: Clarification (Endpoint)
# ============================================================================

def clarification_node(state: AgentState) -> dict:
    """
    Nodo final cuando se necesita clarificación del usuario.
    Previene loops infinitos.
    
    Returns:
        Estado actualizado con contador de iteraciones
    """
    iteration_count = state.get("iteration_count", 0) + 1
    
    # Límite de seguridad
    if iteration_count > 5:
        return {
            "messages": [AIMessage(
                content="⚠️ He intentado procesar tu solicitud varias veces sin éxito.\n\n"
                        "Por favor contacta directamente a nuestro equipo de ventas:\n"
                        "📧 ventas@tuempresa.com\n"
                        "📞 +1 (555) 123-4567"
            )],
            "iteration_count": iteration_count
        }
    
    return {
        "iteration_count": iteration_count
    }
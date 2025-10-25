"""
Herramientas del agente - Funciones que interactúan con sistemas externos
"""

from datetime import datetime, timedelta
from typing import Dict, Any
import uuid

from .models import QuoteRequest, InventoryResult, Quote
from .config import config


# ============================================================================
# Mock Data - Inventario simulado
# ============================================================================

MOCK_INVENTORY: Dict[str, Dict[str, Any]] = {
    "ABC-45": {
        "stock": 500,
        "unit_price": 25.50,
        "lead_time_days": 0,
        "alternatives": ["ABC-46", "ABC-47"]
    },
    "XYZ-100": {
        "stock": 150,
        "unit_price": 45.00,
        "lead_time_days": 0,
        "alternatives": ["XYZ-101"]
    },
    "DEF-200": {
        "stock": 75,
        "unit_price": 120.00,
        "lead_time_days": 0,
        "alternatives": []
    },
    "GHI-300": {
        "stock": 0,
        "unit_price": 85.00,
        "lead_time_days": 15,
        "alternatives": ["GHI-301", "GHI-302"]
    },
    "JKL-400": {
        "stock": 200,
        "unit_price": None,  # Sin precio disponible
        "lead_time_days": 0,
        "alternatives": []
    }
}


# ============================================================================
# Tool 1: Check Inventory
# ============================================================================

def check_inventory_tool(part_number: str, quantity: int) -> InventoryResult:
    """
    Consulta el inventario para una parte específica.
    
    En producción, esto haría una llamada a la API del ERP.
    En desarrollo, usa datos mock.
    
    Args:
        part_number: Número de parte a consultar
        quantity: Cantidad solicitada
        
    Returns:
        InventoryResult con disponibilidad y precio
    """
    
    # Normalizar número de parte
    part_number = part_number.strip().upper()
    
    # Si está habilitado mock data, usar inventario simulado
    if config.ENABLE_MOCK_DATA:
        return _check_mock_inventory(part_number, quantity)
    
    # TODO: Implementar llamada real a ERP
    # response = requests.get(
    #     f"{config.ERP_API_URL}/inventory/{part_number}",
    #     headers={"Authorization": f"Bearer {config.ERP_API_KEY}"}
    # )
    # return InventoryResult(**response.json())
    
    # Por ahora, fallback a mock
    return _check_mock_inventory(part_number, quantity)


def _check_mock_inventory(part_number: str, quantity: int) -> InventoryResult:
    """Consulta inventario mock"""
    
    # Verificar si existe la parte
    if part_number not in MOCK_INVENTORY:
        return InventoryResult(
            part_number=part_number,
            status="unavailable",
            available_stock=0,
            unit_price=None,
            lead_time_days=None,
            suggested_alternatives=[]
        )
    
    item = MOCK_INVENTORY[part_number]
    available_stock = item["stock"]
    unit_price = item["unit_price"]
    lead_time_days = item["lead_time_days"]
    alternatives = item["alternatives"]
    
    # Determinar status
    if unit_price is None:
        status = "no_price"
    elif available_stock >= quantity:
        status = "available"
    elif available_stock > 0:
        status = "insufficient"
    else:
        status = "unavailable"
    
    return InventoryResult(
        part_number=part_number,
        status=status,
        available_stock=available_stock,
        unit_price=unit_price,
        lead_time_days=lead_time_days,
        suggested_alternatives=alternatives
    )


# ============================================================================
# Tool 2: Generate Quote
# ============================================================================

def generate_quote_tool(request: QuoteRequest, inventory: InventoryResult) -> Quote:
    """
    Genera una cotización basada en la solicitud y disponibilidad.
    
    Args:
        request: Solicitud de cotización
        inventory: Resultado de inventario
        
    Returns:
        Quote con detalles completos
        
    Raises:
        ValueError: Si no se puede generar cotización
    """
    
    if inventory.status != "available":
        raise ValueError(f"No se puede cotizar: status={inventory.status}")
    
    if inventory.unit_price is None:
        raise ValueError("Precio no disponible")
    
    # Calcular montos
    subtotal = request.quantity * inventory.unit_price
    tax = subtotal * 0.19  # IVA 19%
    total = subtotal + tax
    
    # Generar ID único
    quote_id = f"Q-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    
    # Fecha de validez
    valid_until = datetime.now() + timedelta(days=config.QUOTE_VALIDITY_DAYS)
    
    return Quote(
        quote_id=quote_id,
        part_number=request.part_number,
        quantity=request.quantity,
        unit_price=inventory.unit_price,
        subtotal=subtotal,
        tax=tax,
        total=total,
        valid_until=valid_until,
        notes=request.notes
    )


# ============================================================================
# Tool 3: Submit Order (Placeholder)
# ============================================================================

def submit_order_tool(quote: Quote) -> Dict[str, Any]:
    """
    Envía la orden al sistema ERP.
    
    Args:
        quote: Cotización aprobada
        
    Returns:
        Confirmación de orden
    """
    
    # TODO: Implementar integración con ERP
    # response = requests.post(
    #     f"{config.ERP_API_URL}/orders",
    #     json=quote.model_dump(),
    #     headers={"Authorization": f"Bearer {config.ERP_API_KEY}"}
    # )
    # return response.json()
    
    # Mock response
    return {
        "order_id": f"ORD-{uuid.uuid4().hex[:8].upper()}",
        "status": "pending",
        "message": "Orden recibida y en proceso"
    }
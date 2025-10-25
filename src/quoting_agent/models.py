"""
Modelos Pydantic para validación de datos
"""

from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class QuoteRequest(BaseModel):
    """Solicitud de cotización del cliente"""
    
    part_number: str = Field(..., description="Número de parte o SKU")
    quantity: int = Field(..., gt=0, description="Cantidad solicitada")
    customer_id: Optional[str] = Field(None, description="ID del cliente")
    notes: Optional[str] = Field(None, description="Notas adicionales")
    
    @field_validator('part_number')
    @classmethod
    def normalize_part_number(cls, v: str) -> str:
        """Normaliza el número de parte a mayúsculas"""
        return v.strip().upper()
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        """Valida que la cantidad sea positiva"""
        if v <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        return v


class InventoryResult(BaseModel):
    """Resultado de consulta de inventario"""
    
    part_number: str
    status: str = Field(..., description="available | insufficient | unavailable | no_price")
    available_stock: int = Field(0, ge=0)
    unit_price: Optional[float] = Field(None, ge=0)
    lead_time_days: Optional[int] = Field(None, ge=0)
    suggested_alternatives: List[str] = Field(default_factory=list)
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Valida que el status sea uno de los permitidos"""
        valid_statuses = {"available", "insufficient", "unavailable", "no_price"}
        if v not in valid_statuses:
            raise ValueError(f"Status debe ser uno de: {valid_statuses}")
        return v


class Quote(BaseModel):
    """Cotización generada"""
    
    quote_id: str
    part_number: str
    quantity: int
    unit_price: float
    subtotal: float
    tax: float
    total: float
    valid_until: datetime
    notes: Optional[str] = None
    
    @field_validator('unit_price', 'subtotal', 'tax', 'total')
    @classmethod
    def validate_positive(cls, v: float) -> float:
        """Valida que los montos sean positivos"""
        if v < 0:
            raise ValueError("Los montos deben ser positivos")
        return v
    
    def format_for_display(self) -> str:
        """Formatea la cotización para mostrar al usuario"""
        return f"""
╔══════════════════════════════════════════════════════════╗
║                    COTIZACIÓN                            ║
╚══════════════════════════════════════════════════════════╝

📋 ID Cotización: {self.quote_id}
📦 Producto: {self.part_number}
🔢 Cantidad: {self.quantity:,} unidades

💰 DESGLOSE:
   Precio unitario:  ${self.unit_price:,.2f}
   Subtotal:         ${self.subtotal:,.2f}
   IVA (19%):        ${self.tax:,.2f}
   ─────────────────────────────────
   TOTAL:            ${self.total:,.2f}

📅 Válida hasta: {self.valid_until.strftime('%d/%m/%Y')}
{f'📝 Notas: {self.notes}' if self.notes else ''}
"""
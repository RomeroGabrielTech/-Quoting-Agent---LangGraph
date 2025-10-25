"""
Tests para el agente de cotización
"""

import pytest
from datetime import datetime

from quoting_agent.models import QuoteRequest, InventoryResult, Quote
from quoting_agent.tools import check_inventory_tool, generate_quote_tool
from quoting_agent.config import config


# ============================================================================
# Tests de Modelos (no requieren API key)
# ============================================================================

class TestModels:
    """Tests de validación de modelos Pydantic"""
    
    def test_quote_request_validation(self):
        """Test de validación básica de QuoteRequest"""
        request = QuoteRequest(part_number="abc-45", quantity=100)
        assert request.part_number == "ABC-45"  # Debe normalizarse a mayúsculas
        assert request.quantity == 100
    
    def test_quote_request_normalization(self):
        """Test de normalización de part_number"""
        request = QuoteRequest(part_number="  xyz-100  ", quantity=50)
        assert request.part_number == "XYZ-100"
    
    def test_quote_request_invalid_quantity(self):
        """Test de validación de cantidad negativa"""
        with pytest.raises(ValueError):
            QuoteRequest(part_number="ABC-45", quantity=-10)
    
    def test_quote_request_zero_quantity(self):
        """Test de validación de cantidad cero"""
        with pytest.raises(ValueError):
            QuoteRequest(part_number="ABC-45", quantity=0)
    
    def test_inventory_result_creation(self):
        """Test de creación de InventoryResult"""
        result = InventoryResult(
            part_number="ABC-45",
            status="available",
            available_stock=500,
            unit_price=25.50
        )
        assert result.part_number == "ABC-45"
        assert result.status == "available"
        assert result.available_stock == 500
        assert result.unit_price == 25.50
    
    def test_inventory_result_invalid_status(self):
        """Test de validación de status inválido"""
        with pytest.raises(ValueError):
            InventoryResult(
                part_number="ABC-45",
                status="invalid_status",
                available_stock=100
            )
    
    def test_quote_creation(self):
        """Test de creación de Quote"""
        quote = Quote(
            quote_id="Q-20240101-ABC123",
            part_number="ABC-45",
            quantity=100,
            unit_price=25.50,
            subtotal=2550.00,
            tax=484.50,
            total=3034.50,
            valid_until=datetime.now()
        )
        assert quote.quote_id == "Q-20240101-ABC123"
        assert quote.total == 3034.50
    
    def test_quote_format_display(self):
        """Test de formateo de cotización"""
        quote = Quote(
            quote_id="Q-TEST-001",
            part_number="ABC-45",
            quantity=100,
            unit_price=25.50,
            subtotal=2550.00,
            tax=484.50,
            total=3034.50,
            valid_until=datetime.now()
        )
        formatted = quote.format_for_display()
        assert "Q-TEST-001" in formatted
        assert "ABC-45" in formatted
        assert "100" in formatted


# ============================================================================
# Tests de Herramientas (no requieren API key)
# ============================================================================

class TestTools:
    """Tests de herramientas con datos mock"""
    
    def test_check_inventory_available(self):
        """Test de inventario disponible"""
        result = check_inventory_tool("ABC-45", 100)
        assert result.status == "available"
        assert result.available_stock >= 100
        assert result.unit_price is not None
    
    def test_check_inventory_insufficient(self):
        """Test de inventario insuficiente"""
        result = check_inventory_tool("DEF-200", 1000)
        assert result.status == "insufficient"
        assert result.available_stock < 1000
    
    def test_check_inventory_unavailable(self):
        """Test de parte no disponible"""
        result = check_inventory_tool("NONEXISTENT-999", 10)
        assert result.status == "unavailable"
        assert result.available_stock == 0
    
    def test_check_inventory_no_price(self):
        """Test de parte sin precio"""
        result = check_inventory_tool("JKL-400", 50)
        assert result.status == "no_price"
        assert result.unit_price is None
    
    def test_generate_quote_success(self):
        """Test de generación de cotización exitosa"""
        request = QuoteRequest(part_number="ABC-45", quantity=100)
        inventory = InventoryResult(
            part_number="ABC-45",
            status="available",
            available_stock=500,
            unit_price=25.50
        )
        
        quote = generate_quote_tool(request, inventory)
        
        assert quote.part_number == "ABC-45"
        assert quote.quantity == 100
        assert quote.unit_price == 25.50
        assert quote.subtotal == 2550.00
        assert quote.tax == pytest.approx(484.50, rel=0.01)
        assert quote.total == pytest.approx(3034.50, rel=0.01)
    
    def test_generate_quote_invalid_status(self):
        """Test de generación de cotización con status inválido"""
        request = QuoteRequest(part_number="ABC-45", quantity=100)
        inventory = InventoryResult(
            part_number="ABC-45",
            status="unavailable",
            available_stock=0
        )
        
        with pytest.raises(ValueError):
            generate_quote_tool(request, inventory)


# ============================================================================
# Tests del Agente (requieren API key)
# ============================================================================

class TestAgent:
    """Tests del agente completo (requieren API key configurada)"""
    
    @pytest.mark.skipif(
        not config.GOOGLE_API_KEY and not config.OPENAI_API_KEY,
        reason="No hay API key configurada"
    )
    def test_agent_simple_request(self):
        """Test de solicitud simple al agente"""
        from quoting_agent import run_agent
        
        result = run_agent("Necesito 100 unidades de ABC-45")
        
        # Verificar que se generó una respuesta
        assert len(result["messages"]) > 0
        
        # Verificar que se parseó la solicitud
        assert result["quote_request"] is not None
        assert result["quote_request"].part_number == "ABC-45"
        assert result["quote_request"].quantity == 100
    
    @pytest.mark.skipif(
        not config.GOOGLE_API_KEY and not config.OPENAI_API_KEY,
        reason="No hay API key configurada"
    )
    def test_agent_generates_quote(self):
        """Test de generación de cotización completa"""
        from quoting_agent import run_agent
        
        result = run_agent("Quiero cotizar 50 unidades de XYZ-100")
        
        # Verificar que se generó cotización
        if result.get("quote"):
            quote = result["quote"]
            assert quote.part_number == "XYZ-100"
            assert quote.quantity == 50
            assert quote.total > 0


# ============================================================================
# Configuración de pytest
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
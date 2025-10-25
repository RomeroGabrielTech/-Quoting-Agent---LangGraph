# 🤖 Quoting Agent - LangGraph

Creé este PoC inmediatamente después de la entrevista para validar mi skillset con su stack exacto

> Sistema inteligente de cotización automatizado usando LangGraph, validación Pydantic e integración con ERP.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🎯 Características

- **Procesamiento de Lenguaje Natural**: Entiende solicitudes de clientes en texto libre
- **Validación Robusta**: Usa Pydantic para validar datos estructurados
- **Flujo Condicional**: Maneja múltiples escenarios (stock insuficiente, sin precio, alternativas)
- **Integración ERP**: Se conecta a sistemas de inventario existentes
- **Cotizaciones Automáticas**: Genera documentos profesionales con ID único
- **Manejo de Excepciones**: Ciclos de retroalimentación inteligentes

## 🏗️ Arquitectura

```
Usuario → Parse Request → Check Inventory → Generate Quote
              ↓                    ↓
         Clarification ←─── Handle Issues
```

El agente usa **LangGraph** para orquestar:
1. **Nodos**: Procesamiento de datos (parse, check, generate)
2. **Tools**: Consultas a sistemas externos (ERP, base de datos)
3. **Conditional Edges**: Lógica de decisión basada en el estado
4. **State Management**: Seguimiento de conversación y datos

## 🚀 Inicio Rápido

### Prerequisitos

- Python 3.11+
- OpenAI API key (o modelo compatible)
- Sistema ERP (opcional, incluye mock)

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/quoting-agent-langgraph.git
cd quoting-agent-langgraph

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales
```

### Uso Básico

```python
from quoting_agent import create_quoting_agent
from langchain_core.messages import HumanMessage

# Crear agente
agent = create_quoting_agent()

# Estado inicial
state = {
    "messages": [HumanMessage(content="Necesito 100 unidades de ABC-45")],
    "quote_request": None,
    "inventory_result": None,
    "quote": None,
    "needs_clarification": False,
    "iteration_count": 0
}

# Ejecutar
result = agent.invoke(state)

# Obtener cotización
if result["quote"]:
    print(f"Cotización: {result['quote'].quote_id}")
    print(f"Total: ${result['quote'].total_price}")
```

### CLI

```bash
# Ejecutar agente por línea de comandos
python scripts/run_agent.py "Necesito 50 unidades de XYZ-100"

# Con archivo de configuración
python scripts/run_agent.py --config config.yaml --input "ABC-45, 100 units"
```

### API REST

```bash
# Iniciar servidor FastAPI
uvicorn api.main:app --reload

# Hacer request
curl -X POST http://localhost:8000/api/v1/quote \
  -H "Content-Type: application/json" \
  -d '{"message": "Necesito 100 unidades de ABC-45"}'
```

## 📚 Casos de Uso

### ✅ Caso Exitoso
```
Input: "Necesito 100 unidades de la parte ABC-45"
Output: Cotización generada con precio, lead time y ID
```

### ⚠️ Stock Insuficiente
```
Input: "Necesito 100 unidades de XYZ-100" (solo hay 50)
Output: Ofrece cantidad disponible + alternativas sugeridas
```

### ❌ Sin Precio Disponible
```
Input: "Necesito 500 unidades de GHI-300"
Output: Solicita contactar departamento de ventas
```

### 🔄 Parte No Disponible
```
Input: "Necesito 10 unidades de DEF-200" (stock = 0)
Output: Sugiere alternativas (DEF-201, DEF-199)
```

## 🔧 Configuración

### Variables de Entorno (.env)

```bash
# LLM Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0

# ERP Integration
ERP_API_URL=https://tu-erp.com/api
ERP_API_KEY=your-api-key
ERP_TIMEOUT=30

# Application
LOG_LEVEL=INFO
MAX_ITERATIONS=5
QUOTE_VALIDITY_DAYS=30
```

### Integración con ERP Real

Edita `integrations/erp_client.py`:

```python
class ERPClient:
    async def check_inventory(self, part_number: str) -> dict:
        # Tu lógica de integración aquí
        response = await self.http_client.get(f"/inventory/{part_number}")
        return response.json()
```

## 🧪 Testing

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=src/quoting_agent --cov-report=html

# Tests específicos
pytest tests/test_agent.py -v

# Tests de integración
pytest tests/ -m integration
```

## 📊 Estructura de Datos

### QuoteRequest (Input)
```python
{
    "part_number": "ABC-45",
    "quantity": 100,
    "customer_id": "CUST-001"
}
```

### Quote (Output)
```python
{
    "quote_id": "Q-A1B2C3D4",
    "part_number": "ABC-45",
    "quantity": 100,
    "unit_price": 15.50,
    "total_price": 1550.00,
    "lead_time_days": 5,
    "notes": "Cotización válida por 30 días..."
}
```

## 🚢 Deployment

### Docker

```bash
# Build
docker build -t quoting-agent .

# Run
docker run -p 8000:8000 --env-file .env quoting-agent

# Con docker-compose
docker-compose up -d
```

### Cloud (Render, Railway, Fly.io)

Ver `docs/deployment.md` para instrucciones específicas.

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver [LICENSE](LICENSE) para detalles.

## 🙏 Agradecimientos

- [LangGraph](https://github.com/langchain-ai/langgraph) - Framework de agentes
- [Pydantic](https://github.com/pydantic/pydantic) - Validación de datos
- [FastAPI](https://github.com/tiangolo/fastapi) - API framework

## 📞 Contacto

- Issues: [GitHub Issues](https://github.com/tu-usuario/quoting-agent-langgraph/issues)
- Documentación: [Wiki](https://github.com/tu-usuario/quoting-agent-langgraph/wiki)

---

Hecho con ❤️ usando LangGraph y Python

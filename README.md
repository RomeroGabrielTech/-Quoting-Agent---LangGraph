# 🤖 Quoting Agent - LangGraph

I created this PoC immediately after the interview to validate my skillset with your exact stack.

> Intelligent automated quoting system using LangGraph, Pydantic validation, and ERP integration.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


## 🎯 Features

- **Natural Language Processing**: Understands customer requests in free text
- **Robust Validation**: Uses Pydantic for structured data validation
- **Conditional Flow**: Handles multiple scenarios (insufficient stock, no price, alternatives)
- **ERP Integration**: Connects to existing inventory systems
- **Automatic Quotes**: Generates professional documents with unique IDs
- **Exception Handling**: Intelligent feedback loops

## 🏗️ Architecture

```
User → Parse Request → Check Inventory → Generate Quote
           ↓                    ↓
      Clarification ←─── Handle Issues
```

The agent uses **LangGraph** to orchestrate:
1. **Nodes**: Data processing (parse, check, generate)
2. **Tools**: Queries to external systems (ERP, database)
3. **Conditional Edges**: State-based decision logic
4. **State Management**: Conversation and data tracking

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key (or compatible model)
- ERP system (optional, includes mock)

### Installation

```bash
# Clone repository
git clone https://github.com/your-username/quoting-agent-langgraph.git
cd quoting-agent-langgraph

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your credentials
```

### Basic Usage

```python
from quoting_agent import create_quoting_agent
from langchain_core.messages import HumanMessage

# Create agent
agent = create_quoting_agent()

# Initial state
state = {
    "messages": [HumanMessage(content="I need 100 units of ABC-45")],
    "quote_request": None,
    "inventory_result": None,
    "quote": None,
    "needs_clarification": False,
    "iteration_count": 0
}

# Execute
result = agent.invoke(state)

# Get quote
if result["quote"]:
    print(f"Quote: {result['quote'].quote_id}")
    print(f"Total: ${result['quote'].total_price}")
```

### CLI

```bash
# Run agent from command line
python scripts/run_agent.py "I need 50 units of XYZ-100"

# With parameters
python scripts/run_agent.py "ABC-45, 100 units"
```

### REST API

```bash
# Start FastAPI server
uvicorn api.main:app --reload

# Make request
curl -X POST http://localhost:8000/api/v1/quote \
  -H "Content-Type: application/json" \
  -d '{"message": "I need 100 units of ABC-45"}'
```

## 📚 Use Cases

### ✅ Successful Case
```
Input: "I need 100 units of part ABC-45"
Output: Quote generated with price, lead time, and ID
```

### ⚠️ Insufficient Stock
```
Input: "I need 100 units of XYZ-100" (only 50 available)
Output: Offers available quantity + suggested alternatives
```

### ❌ Price Not Available
```
Input: "I need 500 units of GHI-300"
Output: Requests to contact sales department
```

### 🔄 Part Not Available
```
Input: "I need 10 units of DEF-200" (stock = 0)
Output: Suggests alternatives (DEF-201, DEF-199)
```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# LLM Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0

# ERP Integration
ERP_API_URL=https://your-erp.com/api
ERP_API_KEY=your-api-key
ERP_TIMEOUT=30

# Application
LOG_LEVEL=INFO
MAX_ITERATIONS=5
QUOTE_VALIDITY_DAYS=30
```

### Real ERP Integration

Edit `integrations/erp_client.py`:

```python
class ERPClient:
    async def check_inventory(self, part_number: str) -> dict:
        # Your integration logic here
        response = await self.http_client.get(f"/inventory/{part_number}")
        return response.json()
```

## 🧪 Testing

```bash
# All tests
pytest

# With coverage
pytest --cov=src/quoting_agent --cov-report=html

# Specific tests
pytest tests/test_agent.py -v

# Integration tests
pytest tests/ -m integration
```

## 📊 Data Structure

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
    "notes": "Quote valid for 30 days..."
}
```

## 🚢 Deployment

### Docker

```bash
# Build
docker build -t quoting-agent .

# Run
docker run -p 8000:8000 --env-file .env quoting-agent

# With docker-compose
docker-compose up -d
```

### Cloud (Render, Railway, Fly.io)

See `docs/deployment.md` for specific instructions.

## 📁 Project Structure

```
quoting-agent-langgraph/
├── src/quoting_agent/      # Main code
│   ├── agent.py            # Graph construction
│   ├── models.py           # Pydantic models
│   ├── nodes.py            # Graph nodes
│   ├── edges.py            # Conditional logic
│   ├── tools.py            # Tools (ERP)
│   └── config.py           # Configuration
├── tests/                  # Tests
├── scripts/                # CLI scripts
├── api/                    # REST API (FastAPI)
├── integrations/           # External integrations
└── docs/                   # Documentation
```

## 🤝 Contributing

1. Fork the repository
2. Create a branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent framework
- [Pydantic](https://github.com/pydantic/pydantic) - Data validation
- [FastAPI](https://github.com/tiangolo/fastapi) - API framework

## 📞 Contact

- Issues: [GitHub Issues](https://github.com/your-username/quoting-agent-langgraph/issues)
- Documentation: [Wiki](https://github.com/your-username/quoting-agent-langgraph/wiki)

---

Made with ❤️ using LangGraph and Python

---

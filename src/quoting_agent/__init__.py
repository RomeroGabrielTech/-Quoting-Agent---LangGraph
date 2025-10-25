"""
Quoting Agent - Sistema de cotización inteligente con LangGraph
"""

__version__ = "0.1.0"
__author__ = "Tu Nombre"

from .agent import create_quoting_agent, run_agent
from .models import QuoteRequest, InventoryResult, Quote
from .state import AgentState, create_initial_state
from .tools import check_inventory_tool, generate_quote_tool
from .llm_factory import create_llm, get_llm_info

__all__ = [
    # Main functions
    "create_quoting_agent",
    "run_agent",
    
    # Models
    "QuoteRequest",
    "InventoryResult",
    "Quote",
    
    # State
    "AgentState",
    "create_initial_state",
    
    # Tools
    "check_inventory_tool",
    "generate_quote_tool",
    
    # LLM
    "create_llm",
    "get_llm_info",
    
    # Metadata
    "__version__",
]
#!/usr/bin/env python3
"""
Script principal para ejecutar el agente de cotización
"""

import sys
import os

# Agregar src al path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quoting_agent import run_agent
from quoting_agent.config import config


def main():
    """Ejecuta el agente con el mensaje del usuario"""
    
    # Verificar argumentos
    if len(sys.argv) < 2:
        print("=" * 60)
        print("🤖 AGENTE DE COTIZACIÓN")
        print("=" * 60)
        print()
        print("Uso:")
        print('  python scripts/run_agent.py "Tu mensaje aquí"')
        print()
        print("Ejemplos:")
        print('  python scripts/run_agent.py "Necesito 100 unidades de ABC-45"')
        print('  python scripts/run_agent.py "Quiero cotizar 50 piezas XYZ-100"')
        print('  python scripts/run_agent.py "Me interesan 25 del producto DEF-200"')
        print()
        return 1
    
    # Obtener mensaje del usuario
    user_message = " ".join(sys.argv[1:])
    
    print("=" * 60)
    print("🤖 AGENTE DE COTIZACIÓN")
    print("=" * 60)
    print()
    
    # Validar configuración
    try:
        config.validate()
    except ValueError as e:
        print("❌ Error de configuración:")
        print(f"   {e}")
        print()
        print("💡 Solución:")
        if "GOOGLE_API_KEY" in str(e):
            print("   1. Ve a: https://aistudio.google.com/app/apikey")
            print("   2. Crea una API key")
            print("   3. Agrégala a tu archivo .env:")
            print("      GOOGLE_API_KEY=AIza...")
        elif "OPENAI_API_KEY" in str(e):
            print("   1. Ve a: https://platform.openai.com/api-keys")
            print("   2. Crea una API key")
            print("   3. Agrégala a tu archivo .env:")
            print("      OPENAI_API_KEY=sk-...")
        print()
        return 1
    
    # Mostrar configuración
    from quoting_agent.llm_factory import get_llm_info
    llm_info = get_llm_info()
    print(f"📋 Configuración:")
    print(f"   Proveedor: {llm_info['provider'].upper()}")
    print(f"   Modelo: {llm_info['model']}")
    print()
    
    # Mostrar mensaje del usuario
    print(f"👤 Usuario:")
    print(f"   {user_message}")
    print()
    
    # Ejecutar agente
    print("🔄 Procesando...")
    print("-" * 60)
    
    try:
        result = run_agent(user_message)
        
        # Mostrar respuesta
        print()
        print("🤖 Respuesta:")
        print("-" * 60)
        
        # Obtener último mensaje (respuesta del agente)
        if result["messages"]:
            last_message = result["messages"][-1]
            print(last_message.content)
        else:
            print("No se generó respuesta")
        
        print()
        print("=" * 60)
        
        # Mostrar información adicional si hay cotización
        if result.get("quote"):
            quote = result["quote"]
            print()
            print("✅ Cotización generada exitosamente")
            print(f"   ID: {quote.quote_id}")
            print(f"   Total: ${quote.total:,.2f}")
        
        return 0
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERROR")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        
        # Mostrar stack trace en modo desarrollo
        if config.is_development():
            import traceback
            print("Stack trace:")
            traceback.print_exc()
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
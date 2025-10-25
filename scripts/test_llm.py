#!/usr/bin/env python3
"""
Script para probar la conexión con el LLM configurado
"""

import sys
import os
from dotenv import load_dotenv

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Cargar variables de entorno
load_dotenv()

from quoting_agent.llm_factory import create_llm, get_llm_info
from quoting_agent.config import config
from langchain_core.messages import HumanMessage


def main():
    """Prueba la configuración del LLM"""
    
    print("=" * 60)
    print("🧪 PRUEBA DE CONEXIÓN LLM")
    print("=" * 60)
    print()
    
    # Mostrar configuración
    print("📋 Configuración detectada:")
    print("-" * 60)
    llm_info = get_llm_info()
    print(f"  Proveedor: {llm_info['provider'].upper()}")
    print(f"  Modelo: {llm_info['model']}")
    print(f"  Temperature: {llm_info['temperature']}")
    print(f"  API Key configurada: {'✓ Sí' if llm_info['configured'] else '✗ No'}")
    print()
    
    if not llm_info['configured']:
        print("❌ Error: API key no configurada")
        print()
        if llm_info['provider'] == 'gemini':
            print("Para configurar Gemini:")
            print("1. Ve a: https://aistudio.google.com/app/apikey")
            print("2. Crea una API key")
            print("3. Agrégala a tu archivo .env:")
            print("   GOOGLE_API_KEY=AIza...")
        else:
            print("Para configurar OpenAI:")
            print("1. Ve a: https://platform.openai.com/api-keys")
            print("2. Crea una API key")
            print("3. Agrégala a tu archivo .env:")
            print("   OPENAI_API_KEY=sk-...")
        return 1
    
    # Intentar crear LLM
    print("🔄 Creando instancia del LLM...")
    try:
        llm = create_llm()
        print("✓ LLM creado exitosamente")
        print()
    except Exception as e:
        print(f"❌ Error creando LLM: {e}")
        return 1
    
    # Hacer prueba simple
    print("🧪 Haciendo prueba de inferencia...")
    print("-" * 60)
    test_message = "Di 'hola' en una palabra"
    print(f"Pregunta: {test_message}")
    print()
    
    try:
        response = llm.invoke([HumanMessage(content=test_message)])
        print(f"Respuesta: {response.content}")
        print()
        print("=" * 60)
        print("✅ ¡PRUEBA EXITOSA!")
        print("=" * 60)
        print()
        print(f"Tu {llm_info['provider'].upper()} está configurado correctamente.")
        print("Puedes ejecutar el agente con:")
        print('  python scripts/run_agent.py "Necesito 100 unidades de ABC-45"')
        print()
        return 0
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERROR EN LA PRUEBA")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        
        if "API key" in str(e) or "authentication" in str(e).lower():
            print("Parece un problema con tu API key.")
            print("Verifica que:")
            print("  1. La API key sea correcta")
            print("  2. Esté en el archivo .env")
            print("  3. No tenga espacios extra")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""
Script para descargar las credenciales OAuth de Google Cloud
y configurar credentials.json automáticamente
"""

import json
import os
import sys
from pathlib import Path

def create_credentials_json():
    """
    Crea el archivo credentials.json basado en las variables de entorno
    o valores de entrada del usuario
    """
    
    print("🔐 Asistente de Configuración - DukeGBP Bot\n")
    
    client_id = input("Ingresa tu CLIENT_ID de Google: ").strip()
    client_secret = input("Ingresa tu CLIENT_SECRET de Google: ").strip()
    
    if not client_id or not client_secret:
        print("❌ Error: Ambos valores son requeridos")
        return False
    
    # Estructura de credenciales para Desktop Client
    credentials = {
        "installed": {
            "client_id": client_id,
            "project_id": "protean-bazaar-355019",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": client_secret,
            "redirect_uris": [
                "http://localhost:8080/callback",
                "urn:ietf:wg:oauth:2.0:oob"
            ]
        }
    }
    
    # Guardar archivo
    creds_path = Path("credentials.json")
    
    with open(creds_path, 'w') as f:
        json.dump(credentials, f, indent=2)
    
    print(f"\n✅ credentials.json creado exitosamente")
    print(f"📁 Ubicación: {creds_path.absolute()}")
    
    return True


def setup_env():
    """Ayuda a crear el archivo .env"""
    
    print("\n🔧 Configuración de Variables de Entorno\n")
    
    env_vars = {
        'TELEGRAM_BOT_TOKEN': '8382371987:AAFsMip0y38jSRdzHBSHdvEv68gw0V8SDj0',
        'GOOGLE_CLIENT_ID': '977275438548-tn4qhi6pqhcle2sntib9g5tl2k59pahd.apps.googleusercontent.com',
        'GOOGLE_CLIENT_SECRET': None,
        'CLAUDE_API_KEY': None,
        'ENVIRONMENT': 'development'
    }
    
    # Obtener valores faltantes
    for key, default in env_vars.items():
        if default is None:
            value = input(f"Ingresa {key}: ").strip()
            env_vars[key] = value
        else:
            print(f"{key}: ✅ (ya configurado)")
    
    # Crear archivo .env
    env_path = Path(".env")
    
    with open(env_path, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    print(f"\n✅ .env creado exitosamente")
    print(f"📁 Ubicación: {env_path.absolute()}")
    
    return True


if __name__ == "__main__":
    print("=" * 50)
    print("DukeGBP Bot - Setup Asistido")
    print("=" * 50 + "\n")
    
    # Crear credentials.json
    if create_credentials_json():
        # Crear .env
        setup_env()
        
        print("\n" + "=" * 50)
        print("✅ Setup completo!")
        print("=" * 50)
        print("\nPróximos pasos:")
        print("1. pip install -r requirements.txt")
        print("2. python main.py")
        print("\nO con Docker:")
        print("docker-compose up\n")
    else:
        sys.exit(1)

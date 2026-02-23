#!/usr/bin/env python3
"""
Script de prueba para validar configuración del DukeGBP Bot
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

print("🔍 Verificando configuración del DukeGBP Bot...\n")

# Cargar .env
load_dotenv()

# Verificar credenciales
checks = [
    ("TELEGRAM_BOT_TOKEN", "Token de Telegram"),
    ("GOOGLE_CLIENT_ID", "Google Client ID"),
    ("GOOGLE_CLIENT_SECRET", "Google Client Secret"),
    ("CLAUDE_API_KEY", "Claude API Key"),
]

all_good = True

for env_var, description in checks:
    value = os.getenv(env_var)
    if value:
        # Mostrar solo primeros caracteres por seguridad
        preview = value[:20] + "..." if len(value) > 20 else value
        print(f"✅ {description}: {preview}")
    else:
        print(f"❌ {description}: NO CONFIGURADO")
        all_good = False

# Verificar archivos
print("\n📁 Verificando archivos...\n")

files_to_check = [
    "credentials.json",
    ".env",
    "main.py",
    "gmb_client.py",
    "claude_analyzer.py",
]

for file in files_to_check:
    path = Path(file)
    if path.exists():
        print(f"✅ {file}: Existe")
    else:
        print(f"❌ {file}: NO ENCONTRADO")
        all_good = False

# Verificar imports
print("\n🐍 Verificando imports Python...\n")

try:
    import telegram
    print("✅ python-telegram-bot: OK")
except ImportError:
    print("❌ python-telegram-bot: NO INSTALADO")
    all_good = False

try:
    import google.auth
    print("✅ google-auth: OK")
except ImportError:
    print("❌ google-auth: NO INSTALADO")
    all_good = False

try:
    from anthropic import Anthropic
    print("✅ anthropic: OK")
except ImportError:
    print("❌ anthropic: NO INSTALADO")
    all_good = False

try:
    import dotenv
    print("✅ python-dotenv: OK")
except ImportError:
    print("❌ python-dotenv: NO INSTALADO")
    all_good = False

# Resumen
print("\n" + "="*50)
if all_good:
    print("✅ TODO LISTO - El bot está configurado correctamente")
    print("="*50)
    print("\nPróximos pasos:")
    print("1. python main.py")
    print("2. Abre Telegram y escribe /start al bot")
    print("\nO para producción:")
    print("docker-compose up")
    sys.exit(0)
else:
    print("❌ FALTAN CONFIGURACIONES - Por favor verifica lo marcado arriba")
    print("="*50)
    sys.exit(1)

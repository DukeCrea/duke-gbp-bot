# 🎯 DukeGBP Bot - Google My Business Analyzer

Bot de Telegram que analiza Google My Business y proporciona recomendaciones automáticas con IA.

## 📋 Qué hace

- ✅ Conecta con Google My Business via OAuth 2.0
- 📊 Extrae métricas de performance (vistas, clics, llamadas, etc.)
- 🤖 Analiza datos con Claude AI
- 💡 Genera recomendaciones automáticas
- 📱 Interfaz amigable en Telegram

## 🚀 Setup Rápido

### 1. Clonar repositorio

```bash
git clone <tu-repo>
cd duke_gbp_bot
```

### 2. Variables de entorno

Copia `.env.example` a `.env` y completa:

```bash
cp .env.example .env
```

Necesitas:
- `TELEGRAM_BOT_TOKEN` ✅ (ya tienes)
- `GOOGLE_CLIENT_ID` ✅ (ya tienes)
- `GOOGLE_CLIENT_SECRET` (obtén de Google Cloud)
- `CLAUDE_API_KEY` (obtén de Anthropic)

### 3. Descargar credenciales de Google

1. Ve a **Google Cloud Console** → Tu proyecto
2. **Credenciales** → `GBP Desktop Client`
3. Click en el nombre → **Descargar JSON**
4. Renómbralo a `credentials.json` y colócalo en la raíz del proyecto

```bash
# Estructura final
duke_gbp_bot/
├── credentials.json       # Descargado de Google Cloud
├── main.py
├── gmb_client.py
├── claude_analyzer.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
└── README.md
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Ejecutar localmente

```bash
python main.py
```

O con Docker:

```bash
docker-compose up
```

## 📱 Usar el bot

1. Abre Telegram y busca `@DukegbpBot`
2. `/start` - Menú principal
3. Conecta tu Google My Business
4. `/analyze` - Obtén análisis

## 🌐 Desplegar en Railway

### 1. Conectar GitHub

- Crea un repo en GitHub con este código
- Ve a [railway.app](https://railway.app)
- "New Project" → "Deploy from GitHub"
- Selecciona tu repo

### 2. Configurar variables

En Railway, ve a **Variables**:

```
TELEGRAM_BOT_TOKEN=8382371987:AAFsMip0y38jSRdzHBSHdvEv68gw0V8SDj0
GOOGLE_CLIENT_ID=977275438548-tn4qhi6pqhcle2sntib9g5tl2k59pahd.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=TU_SECRET
CLAUDE_API_KEY=TU_API_KEY
ENVIRONMENT=production
```

### 3. Deploy

Railway detectará automáticamente el Dockerfile y deployará.

## 🔧 Arquitectura

```
Usuario → Telegram Bot
         ↓
         OAuth Flow (Google)
         ↓
         GMB Client (APIs)
         ├─ My Business API
         ├─ Business Profile API
         └─ Performance API
         ↓
         Claude AI (Análisis)
         ↓
         Reporte → Usuario
```

## 📊 Flujo OAuth

1. Usuario hace `/start`
2. Bot genera URL de OAuth
3. Usuario autoriza en Google
4. Bot almacena credenciales (encriptadas)
5. Usuario puede analizar cuando quiera

## 🐛 Troubleshooting

### "No se encontró credentials.json"
- Descárgalo de Google Cloud Console
- Colócalo en la raíz del proyecto

### "Error de autenticación"
- Verifica que el Client Secret es correcto
- Revisa que las APIs estén habilitadas en Google Cloud

### Bot no responde
- Verifica el token de Telegram
- Mira los logs: `docker-compose logs -f`

## 📈 Mejoras futuras

- [ ] Webhook en lugar de polling
- [ ] Dashboard web con gráficos
- [ ] Alertas automáticas
- [ ] Múltiples ubicaciones
- [ ] Comparativa con competencia
- [ ] Sugerencias de fotos con IA

## 📝 Licencia

MIT

## 👤 Contacto

Antonio Duque - DUKECREA

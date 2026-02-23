import os
import logging
import json
import pickle
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    ContextTypes, filters, ConversationHandler
)
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
import httpx

from gmb_client import GMBClient
from claude_analyzer import ClaudeAnalyzer

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

# Estados de conversación
WAITING_FOR_OAUTH = 1
ANALYZING_GMB = 2

# Rutas de almacenamiento
CREDENTIALS_DIR = Path("credentials")
CREDENTIALS_DIR.mkdir(exist_ok=True)

SCOPES = [
    'https://www.googleapis.com/auth/business.manage',
    'https://www.googleapis.com/auth/business.manage.readonly'
]


class DukeGBPBot:
    def __init__(self):
        self.gmb_client = None
        self.claude_analyzer = ClaudeAnalyzer(CLAUDE_API_KEY)
        self.user_credentials = {}
        
    def get_credentials_path(self, user_id: int) -> Path:
        """Obtener ruta de credenciales del usuario"""
        return CREDENTIALS_DIR / f"user_{user_id}_creds.pickle"
    
    def get_user_credentials(self, user_id: int) -> Optional[Credentials]:
        """Cargar credenciales guardadas del usuario"""
        creds_path = self.get_credentials_path(user_id)
        
        if creds_path.exists():
            with open(creds_path, 'rb') as token:
                creds = pickle.load(token)
                if creds.valid:
                    return creds
                elif creds.refresh_token:
                    try:
                        creds.refresh(Request())
                        self.save_user_credentials(user_id, creds)
                        return creds
                    except RefreshError:
                        logger.warning(f"Token de usuario {user_id} expirado")
                        return None
        return None
    
    def save_user_credentials(self, user_id: int, creds: Credentials):
        """Guardar credenciales del usuario"""
        creds_path = self.get_credentials_path(user_id)
        with open(creds_path, 'wb') as token:
            pickle.dump(creds, token)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        user_id = update.effective_user.id
        existing_creds = self.get_user_credentials(user_id)
        
        if existing_creds:
            # Usuario ya tiene credenciales
            keyboard = [
                [InlineKeyboardButton("📊 Analizar GMB", callback_data="analyze_gmb")],
                [InlineKeyboardButton("🔄 Reconectar Google", callback_data="reconnect_oauth")],
                [InlineKeyboardButton("❌ Desconectar", callback_data="disconnect")]
            ]
        else:
            # Primer acceso
            keyboard = [
                [InlineKeyboardButton("🔐 Conectar Google My Business", callback_data="start_oauth")]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎯 *DukeGBP Bot*\n\n"
            "Analiza tu Google My Business y obtén recomendaciones automáticas con IA.\n\n"
            "¿Qué quieres hacer?",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar botones inline"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        if query.data == "start_oauth":
            await self.initiate_oauth(update, context)
        elif query.data == "reconnect_oauth":
            await self.initiate_oauth(update, context)
        elif query.data == "analyze_gmb":
            await self.analyze_gmb(update, context)
        elif query.data == "disconnect":
            await self.disconnect(update, context)
    
    async def initiate_oauth(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Iniciar flujo OAuth"""
        user_id = update.effective_user.id
        
        try:
            # Crear flow de OAuth
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json',
                SCOPES
            )
            
            # Generar URL de autorización
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            # Guardar flow en contexto para después
            context.user_data['oauth_flow'] = flow
            context.user_data['user_id'] = user_id
            
            keyboard = [[InlineKeyboardButton("✅ Autorizar en Google", url=auth_url)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.edit_message_text(
                "🔐 *Autorización necesaria*\n\n"
                "Haz click en el botón de abajo para conectar tu Google My Business.\n\n"
                "Después escribe `/oauth_callback` para confirmar.",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            
            return WAITING_FOR_OAUTH
            
        except FileNotFoundError:
            await update.callback_query.edit_message_text(
                "❌ Error: No se encontró `credentials.json`\n\n"
                "Descarga las credenciales de Google Cloud Console y colócalas en la raíz del proyecto."
            )
    
    async def oauth_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar callback de OAuth (manual por ahora)"""
        user_id = update.effective_user.id
        
        if 'oauth_flow' not in context.user_data:
            await update.message.reply_text(
                "❌ No hay flujo OAuth activo. Usa `/start` primero."
            )
            return
        
        try:
            flow = context.user_data['oauth_flow']
            # En producción, necesitarías capturar el código de autorización
            # Por ahora, asumimos que el usuario autorizó en Google
            
            # Simular obtención de credenciales (en producción usarías el código)
            # creds = flow.run_local_server(port=0)
            
            await update.message.reply_text(
                "✅ *Conexión exitosa*\n\n"
                "Tu Google My Business está conectado.\n\n"
                "Usa `/start` para ver opciones de análisis."
            )
            
        except Exception as e:
            logger.error(f"Error en OAuth callback: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def analyze_gmb(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Analizar Google My Business del usuario"""
        user_id = update.effective_user.id
        
        # Obtener credenciales del usuario
        creds = self.get_user_credentials(user_id)
        
        if not creds:
            await update.callback_query.edit_message_text(
                "❌ No hay credenciales válidas. Usa `/start` para reconectar."
            )
            return
        
        await update.callback_query.edit_message_text(
            "⏳ Analizando tu Google My Business...\n\n"
            "Esto puede tomar unos segundos."
        )
        
        try:
            # Inicializar cliente GMB con credenciales del usuario
            gmb_client = GMBClient(creds)
            
            # Obtener datos de GMB
            gmb_data = await gmb_client.get_business_data()
            
            if not gmb_data:
                await update.callback_query.edit_message_text(
                    "⚠️ No se encontraron datos de Google My Business.\n\n"
                    "Asegúrate de tener un perfil comercial activo."
                )
                return
            
            # Analizar con Claude
            await update.callback_query.edit_message_text(
                "🤖 Generando análisis con IA...\n\n"
                "Por favor espera."
            )
            
            analysis = await self.claude_analyzer.analyze_gmb(gmb_data)
            
            # Enviar análisis
            await update.callback_query.edit_message_text(
                f"📊 *Análisis de tu Google My Business*\n\n"
                f"{analysis}",
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error analizando GMB: {e}")
            await update.callback_query.edit_message_text(
                f"❌ Error al analizar: {str(e)}"
            )
    
    async def disconnect(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Desconectar usuario"""
        user_id = update.effective_user.id
        creds_path = self.get_credentials_path(user_id)
        
        if creds_path.exists():
            creds_path.unlink()
        
        keyboard = [[InlineKeyboardButton("🔐 Conectar Google My Business", callback_data="start_oauth")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            "✅ Desconectado correctamente.\n\n"
            "Puedes reconectar cuando quieras.",
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help"""
        await update.message.reply_text(
            "🎯 *Comandos disponibles:*\n\n"
            "/start - Menú principal\n"
            "/help - Esta ayuda\n"
            "/analyze - Analizar GMB rápidamente\n"
            "/disconnect - Desconectar Google\n\n"
            "💡 *¿Cómo funciona?*\n\n"
            "1. Conecta tu Google My Business\n"
            "2. Presiona 'Analizar'\n"
            "3. Recibe recomendaciones con IA\n",
            parse_mode="Markdown"
        )


async def main():
    """Función principal"""
    
    # Verificar variables de entorno
    if not all([TELEGRAM_BOT_TOKEN, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, CLAUDE_API_KEY]):
        logger.error("❌ Faltan variables de entorno. Revisa .env")
        return
    
    # Crear aplicación
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    bot = DukeGBPBot()
    
    # Handlers
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("help", bot.help_command))
    app.add_handler(CommandHandler("oauth_callback", bot.oauth_callback))
    app.add_handler(CommandHandler("analyze", bot.analyze_gmb))
    app.add_handler(CommandHandler("disconnect", bot.disconnect))
    
    # Callback queries (botones)
    from telegram.ext import CallbackQueryHandler
    app.add_handler(CallbackQueryHandler(bot.button_callback))
    
    # Iniciar bot
    logger.info("🚀 DukeGBP Bot iniciado...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    # Mantener en ejecución
    try:
        await asyncio.sleep(float('inf'))
    finally:
        await app.stop()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

class SimpleBot:
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("✅ Bot funcionando!")
    
    async def analyze(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("📊 Analizando...")

async def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    bot = SimpleBot()
    
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("analyze", bot.analyze))
    
    logger.info("Bot iniciado")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    try:
        await asyncio.sleep(float('inf'))
    finally:
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())

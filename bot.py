import os
import logging
from anthropic import Anthropic
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
KEY = os.environ.get('ANTHROPIC_KEY', '')
PROMPT = 'Tu es ARIA, assistante IA francophone. Reponds en francais, sois concise et bienveillante. Max 200 mots.'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ARIA')
client = Anthropic(api_key=KEY)
histories = {}

def get_hist(uid):
    return histories.get(uid, [])

def add_hist(uid, role, content):
    if uid not in histories:
        histories[uid] = []
    histories[uid].append({'role': role, 'content': content})
    if len(histories[uid]) > 20:
        histories[uid] = histories[uid][-20:]

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Bonjour ! Je suis ARIA, votre assistante IA. Comment puis-je vous aider ?')

async def reset(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    histories[update.effective_user.id] = []
    await update.message.reply_text('Conversation reinitialisee !')

async def msg(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text
    await ctx.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    add_hist(uid, 'user', text)
    try:
        r = client.messages.create(model='claude-sonnet-4-20250514', max_tokens=800, system=PROMPT, messages=get_hist(uid))
        reply = r.content[0].text
        add_hist(uid, 'assistant', reply)
    except Exception as e:
        reply = 'Erreur, reessayez.'
        logger.error(e)
    await update.message.reply_text(reply)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('reset', reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg))
    logger.info('ARIA demarre...')
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

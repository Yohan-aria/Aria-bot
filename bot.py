import os
import logging
from anthropic import Anthropic
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
ANTHROPIC_KEY = os.environ.get('ANTHROPIC_KEY', '')

SYSTEM_PROMPT = 'Tu es ARIA, une assistante IA personnelle et professionnelle francophone. Tu aides avec l agenda, les emails, la gestion de projets, le coaching et la productivite. Reponds toujours en francais, sois directe et bienveillante. Maximum 250 mots par reponse.'

logging.basicConfig(format=”%(asctime)s - %(name)s - %(levelname)s - %(message)s”, level=logging.INFO)
logger = logging.getLogger('ARIA')

client = Anthropic(api_key=ANTHROPIC_KEY)
user_histories = {}

def get_history(user_id):
return user_histories.get(user_id, [])

def add_to_history(user_id, role, content):
if user_id not in user_histories:
user_histories[user_id] = []
user_histories[user_id].append({'role': role, 'content': content})
if len(user_histories[user_id]) > 20:
user_histories[user_id] = user_histories[user_id][-20:]

def clear_history(user_id):
user_histories[user_id] = []

async def ask_aria(user_id, user_message):
add_to_history(user_id, 'user', user_message)
try:
response = client.messages.create(
model='claude-sonnet-4-20250514',
max_tokens=1000,
system=SYSTEM_PROMPT,
messages=get_history(user_id)
)
reply = response.content[0].text
add_to_history(user_id, 'assistant', reply)
return reply
except Exception as e:
logger.error(f'Erreur Anthropic : {e}')
return 'Desole, j ai rencontre une erreur. Reessayez dans un instant.'

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
user = update.effective_user
name = user.first_name if user else “vous”
welcome = 'Bonjour ' + name + ' ! Je suis ARIA, votre assistante IA personnelle et professionnelle. Je peux vous aider avec votre agenda, vos emails, vos projets, le coaching et bien plus. Parlez-moi librement !'
await update.message.reply_text(welcome)

async def cmd_reset(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
user_id = update.effective_user.id
clear_history(user_id)
await update.message.reply_text('Conversation reinitialisee ! Comment puis-je vous aider ?')

async def cmd_aide(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
aide = 'Commandes disponibles :\n/start - Message de bienvenue\n/aide - Cette aide\n/reset - Reinitialiser la conversation\n\nOu ecrivez simplement votre demande en texte libre !'
await update.message.reply_text(aide)

async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
user_id = update.effective_user.id
user_text = update.message.text
await ctx.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
reply = await ask_aria(user_id, user_text)
await update.message.reply_text(reply)

async def handle_error(update: object, ctx: ContextTypes.DEFAULT_TYPE):
logger.error(f”Erreur : {ctx.error}')

def main():
app = Application.builder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler('start', cmd_start))
app.add_handler(CommandHandler('aide', cmd_aide))
app.add_handler(CommandHandler('reset', cmd_reset))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_error_handler(handle_error)
logger.info('ARIA demarre sur Telegram…')
app.run_polling(allowed_updates=Update.ALL_TYPES)

if **name** == '**main**':
main()

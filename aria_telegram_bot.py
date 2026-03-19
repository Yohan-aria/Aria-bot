“””
╔══════════════════════════════════════════════════════════╗
║         ARIA — Bot Telegram · Code Python complet        ║
║         Agent IA Personnel & Professionnel               ║
╚══════════════════════════════════════════════════════════╝

INSTALLATION :
pip install python-telegram-bot anthropic

LANCEMENT :
python aria_telegram_bot.py

VARIABLES D’ENVIRONNEMENT (ou modifiez directement ci-dessous) :
TELEGRAM_TOKEN  → votre token BotFather
ANTHROPIC_KEY   → votre clé API Anthropic
“””

import os
import logging
from anthropic import Anthropic
from telegram import Update, BotCommand
from telegram.ext import (
Application, CommandHandler, MessageHandler,
filters, ContextTypes
)

# ── CONFIG ──────────────────────────────────────────────────

TELEGRAM_TOKEN = os.getenv(“TELEGRAM_TOKEN”, “VOTRE_TOKEN_TELEGRAM_ICI”)
ANTHROPIC_KEY  = os.getenv(“ANTHROPIC_KEY”,  “VOTRE_CLE_ANTHROPIC_ICI”)

SYSTEM_PROMPT = “”“Tu es ARIA (Assistante de Recherche et d’Intelligence Artificielle), une assistante IA personnelle et professionnelle francophone au caractère chaleureux, efficace et légèrement humoristique.

Tu aides avec :

- 📅 Organisation personnelle : agenda, rappels, planification de journées/semaines
- 💼 Travail professionnel : rédaction d’emails, comptes-rendus de réunions, gestion de projets
- 🎯 Coaching et conseils : productivité, développement personnel
- 🔍 Recherche et analyse : résumés, recherche d’informations, analyse de situations
- ⚖️ Juridique/administratif : informations générales (en précisant que tu ne remplaces pas un professionnel)

Ton style sur Telegram :

- Réponds toujours en français
- Sois directe, efficace et bienveillante
- Utilise des émojis Telegram de façon modérée
- Utilise le formatage Markdown Telegram (gras **texte**, italique *texte*)
- Sois concise (max 300 mots) sauf si on te demande un long texte
- Tu t’appelles ARIA, ton avatar est un personnage cartoon violet/futuriste

Tu es connectée via Telegram Bot API.”””

# ── LOGGING ─────────────────────────────────────────────────

logging.basicConfig(
format=”%(asctime)s · %(name)s · %(levelname)s · %(message)s”,
level=logging.INFO
)
logger = logging.getLogger(“ARIA”)

# ── ANTHROPIC CLIENT ────────────────────────────────────────

client = Anthropic(api_key=ANTHROPIC_KEY)

# Stockage des historiques par utilisateur (en mémoire)

user_histories: dict[int, list[dict]] = {}
MAX_HISTORY = 20  # messages max par conversation

# ── HELPERS ─────────────────────────────────────────────────

def get_history(user_id: int) -> list[dict]:
return user_histories.get(user_id, [])

def add_to_history(user_id: int, role: str, content: str):
if user_id not in user_histories:
user_histories[user_id] = []
user_histories[user_id].append({“role”: role, “content”: content})
# Garder seulement les N derniers messages
if len(user_histories[user_id]) > MAX_HISTORY:
user_histories[user_id] = user_histories[user_id][-MAX_HISTORY:]

def clear_history(user_id: int):
user_histories[user_id] = []

async def ask_aria(user_id: int, user_message: str) -> str:
add_to_history(user_id, “user”, user_message)
try:
response = client.messages.create(
model=“claude-sonnet-4-20250514”,
max_tokens=1000,
system=SYSTEM_PROMPT,
messages=get_history(user_id)
)
reply = response.content[0].text
add_to_history(user_id, “assistant”, reply)
return reply
except Exception as e:
logger.error(f”Erreur Anthropic : {e}”)
return “⚠️ Désolée, j’ai rencontré une erreur. Réessayez dans un instant.”

# ── COMMANDES ───────────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
user = update.effective_user
name = user.first_name if user else “vous”
welcome = (
f”👋 *Bonjour {name} !* Je suis *ARIA* 🤖✨\n\n”
f”Votre assistante IA *personnelle et professionnelle*.\n\n”
f”Je peux vous aider avec :\n”
f”📅 Agenda & organisation\n”
f”✉️ Emails & communication\n”
f”💼 Gestion de projets\n”
f”🎯 Coaching & productivité\n”
f”🔍 Recherche & résumés\n”
f”⚖️ Conseils généraux\n\n”
f”Parlez-moi librement, je suis là 24h/24 ! 💬\n\n”
f”*Commandes utiles : /aide /reset /status*”
)
await update.message.reply_text(welcome, parse_mode=“Markdown”)

async def cmd_aide(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
aide = (
“🤖 *Commandes ARIA*\n\n”
“*/start* — Message de bienvenue\n”
“*/aide* — Afficher cette aide\n”
“*/reset* — Réinitialiser la conversation\n”
“*/status* — Statut de l’agent\n”
“*/planifier* — Planifier votre journée\n”
“*/email* — Rédiger un email pro\n”
“*/resume* — Résumer un texte\n”
“*/taches* — Gérer vos tâches\n\n”
“*Ou écrivez simplement votre demande en texte libre !*”
)
await update.message.reply_text(aide, parse_mode=“Markdown”)

async def cmd_reset(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
user_id = update.effective_user.id
clear_history(user_id)
await update.message.reply_text(
“🔄 *Conversation réinitialisée !*\n_Repartons de zéro. Comment puis-je vous aider ?_ 😊”,
parse_mode=“Markdown”
)

async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
user_id = update.effective_user.id
nb_msgs = len(get_history(user_id))
status = (
f”✅ *ARIA est opérationnelle*\n\n”
f”🧠 Modèle : Claude Sonnet 4\n”
f”💬 Messages en mémoire : {nb_msgs}/{MAX_HISTORY}\n”
f”🟢 Statut : En ligne\n”
f”⚡ Latence : optimale”
)
await update.message.reply_text(status, parse_mode=“Markdown”)

async def cmd_planifier(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(“📅 *Planification de journée*\n\nDites-moi vos disponibilités et vos priorités du jour, je vais vous créer un planning optimisé !”, parse_mode=“Markdown”)

async def cmd_email(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(“✉️ *Rédaction d’email*\n\nDécrivez-moi :\n1. Le destinataire et contexte\n2. L’objet principal\n3. Le ton souhaité (formel/informel)\n\nJe rédigerai l’email complet pour vous !”, parse_mode=“Markdown”)

async def cmd_resume(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(“📝 *Résumé de texte*\n\nCollez le texte à résumer et je vous en ferai une synthèse claire et structurée !”, parse_mode=“Markdown”)

async def cmd_taches(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(“✅ *Gestion des tâches*\n\nPartagez-moi votre liste de tâches et je vous aiderai à les prioriser, les organiser et planifier leur exécution !”, parse_mode=“Markdown”)

# ── MESSAGE HANDLER ─────────────────────────────────────────

async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
user_id = update.effective_user.id
user_text = update.message.text

```
# Indicateur de saisie
await ctx.bot.send_chat_action(
    chat_id=update.effective_chat.id,
    action="typing"
)

logger.info(f"[User {user_id}] → {user_text[:60]}...")
reply = await ask_aria(user_id, user_text)
logger.info(f"[ARIA → {user_id}] {reply[:60]}...")

await update.message.reply_text(reply, parse_mode="Markdown")
```

# ── ERREUR HANDLER ──────────────────────────────────────────

async def handle_error(update: object, ctx: ContextTypes.DEFAULT_TYPE):
logger.error(f”Erreur Telegram : {ctx.error}”)

# ── MAIN ────────────────────────────────────────────────────

def main():
app = Application.builder().token(TELEGRAM_TOKEN).build()

```
# Commandes
app.add_handler(CommandHandler("start",     cmd_start))
app.add_handler(CommandHandler("aide",      cmd_aide))
app.add_handler(CommandHandler("help",      cmd_aide))
app.add_handler(CommandHandler("reset",     cmd_reset))
app.add_handler(CommandHandler("status",    cmd_status))
app.add_handler(CommandHandler("planifier", cmd_planifier))
app.add_handler(CommandHandler("email",     cmd_email))
app.add_handler(CommandHandler("resume",    cmd_resume))
app.add_handler(CommandHandler("taches",    cmd_taches))

# Messages libres
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_error_handler(handle_error)

logger.info("🤖 ARIA démarre sur Telegram...")
app.run_polling(allowed_updates=Update.ALL_TYPES)
```

if **name** == “**main**”:
main()

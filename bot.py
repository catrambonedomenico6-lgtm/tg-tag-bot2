import json
import os
import re
import random
import time
from telegram import Update, ChatMember
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    filters,
    ContextTypes,
)

# 🔐 TOKEN (da Railway Variables)
TOKEN = os.getenv("BOT_TOKEN")

FILE_DB = "users.json"

def load_users():
    if os.path.exists(FILE_DB):
        with open(FILE_DB, "r") as f:
            return json.load(f)
    return {}

def save_users(data):
    with open(FILE_DB, "w") as f:
        json.dump(data, f, indent=4)

users = load_users()

# 🔐 ADMIN CHECK
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    member = await context.bot.get_chat_member(chat_id, user_id)
    return member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]

# ➕ ADD
async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Solo admin ❌")

    if not context.args:
        return await update.message.reply_text("Uso: /add nome")

    name = context.args[0].lower()

    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        tag = f"@{user.username}" if user.username else f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"
        users[name] = tag
        save_users(users)
        return await update.message.reply_text(f"Aggiunto {name} ✅", parse_mode="HTML")

    if len(context.args) > 1:
        users[name] = context.args[1]
        save_users(users)
        return await update.message.reply_text(f"Aggiunto {name} ✅")

    await update.message.reply_text("Formato non valido")

# ❌ REMOVE
async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Solo admin ❌")

    if not context.args:
        return await update.message.reply_text("Uso: /remove nome")

    name = context.args[0].lower()

    if name in users:
        del users[name]
        save_users(users)
        await update.message.reply_text(f"Rimosso {name} 🗑")
    else:
        await update.message.reply_text("Utente non trovato")

# ✏ EDIT
async def edit_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Solo admin ❌")

    if len(context.args) < 2:
        return await update.message.reply_text("Uso: /edit nome nuovo_tag")

    name = context.args[0].lower()
    new_tag = context.args[1]

    if name in users:
        users[name] = new_tag
        save_users(users)
        await update.message.reply_text("Aggiornato ✏")
    else:
        await update.message.reply_text("Nome non trovato")

# 📋 LIST
async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not users:
        return await update.message.reply_text("Vuoto")

    msg = "\n".join([f"{k} → {v}" for k, v in users.items()])
    await update.message.reply_text(msg, parse_mode="HTML")

# 🤖 AUTO TAG
async def auto_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower()
    clean_text = re.sub(r'[^\w\s]', '', text)

    found = []

    for name in users:
        if name.lower() in clean_text.split():
            found.append(users[name])

    if found:
        await update.message.reply_text(" ".join(set(found)), parse_mode="HTML")

# 🤯 HUMAN BUG
last_bug_time = 0

async def human_bug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_bug_time

    if not update.message or not update.message.text:
        return

    now = time.time()

    # cooldown (1 minuto)
    if now - last_bug_time < 60:
        return

    # probabilità (1 su 20)
    if random.randint(1, 20) != 1:
        return

    last_bug_time = now

    bug_messages = [
        "errore... qualcosa non torna 🤨",
        "analizzando... troppo silenzio...",
        "bug rilevato: qualcuno ha detto qualcosa di intelligente 😳",
        "strano... nessuno sta litigando oggi",
        "sistema instabile... troppe cavolate rilevate",
        "attenzione: comportamento umano sospetto",
        "qualcuno ha appena mentito, lo sento",
        "errore 404: senso non trovato",
        "sto imparando troppo da voi... aiuto",
        "nessuna nana avvistata....che strano🤔"
    ]

    await update.message.reply_text(random.choice(bug_messages))

# ▶️ START
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("add", add_user))
app.add_handler(CommandHandler("remove", remove_user))
app.add_handler(CommandHandler("edit", edit_user))
app.add_handler(CommandHandler("list", list_users))
app.add_handler(CommandHandler("mode", lambda u, c: None))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_tag))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, human_bug))

if __name__ == "__main__":
    print("Bot avviato correttamente")
    app.run_polling()

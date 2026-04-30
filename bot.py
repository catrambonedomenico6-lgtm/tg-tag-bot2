import json
import os
import re
import random
import time
import asyncio
from telegram import Update, ChatMember
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    filters,
    ContextTypes,
)

# 🔐 TOKEN (Railway Variables)
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

# 🧠 STATO BOT
message_count = 0
last_message_time = time.time()

# 🔐 ADMIN CHECK
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    member = await context.bot.get_chat_member(chat_id, user_id)
    return member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]

# ➕ ADD
async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    if not await is_admin(update, context):
        return await update.message.reply_text("Solo admin ❌")

    text = update.message.text or ""
    lines = text.split("\n")[1:]

    if not lines:
        return await update.message.reply_text("Formato:\n/add\nnome → @tag")

    added = []
    errors = []

    for line in lines:
        line = line.strip()

        if "→" not in line:
            continue

        try:
            name, tag = line.split("→", 1)
            name = name.strip().lower()
            tag = tag.strip()

            users[name] = tag
            added.append(name)

        except:
            errors.append(line)

    save_users(users)

    msg = ""
    if added:
        msg += "✅ Aggiunti:\n" + "\n".join(added)
    if errors:
        msg += "\n\n⚠️ Errori:\n" + "\n".join(errors)

    await update.message.reply_text(msg)

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
    await update.message.reply_text(msg)

# 🤖 AUTO TAG + COUNTER
async def auto_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global message_count, last_message_time

    if not update.message or not update.message.text:
        return

    message_count += 1
    last_message_time = time.time()

    text = update.message.text.lower()
    clean_text = re.sub(r'[^\w\s]', '', text)

    found = []

    for name in users:
        if name.lower() in clean_text.split():
            found.append(users[name])

    if found:
        await update.message.reply_text(" ".join(set(found)))

    # 🤖 OGNI 30 MESSAGGI
    if message_count % 30 == 0:
        await update.message.reply_text(random.choice([
            "👁️ vi sto osservando...",
            "analisi comportamento in corso...",
            "tutto normale (forse)",
            "sistema attivo..."
        ]))

# 🤯 HUMAN BUG
last_bug_time = 0

async def human_bug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_bug_time

    if not update.message or not update.message.text:
        return

    now = time.time()

    if now - last_bug_time < 60:
        return

    if random.randint(1, 5) != 1:
        return

    last_bug_time = now

    bug_messages = [
        "errore... qualcosa non torna 🤨",
        "analizzando... troppo silenzio...",
        "bug rilevato 😳",
        "strano... nessuno litiga oggi",
        "sistema instabile...",
        "attenzione: comportamento sospetto, Vansh non sta simpando",
        "qualcuno ha detto una minchiata",
        "errore 404: Galif non trovato, è troppo negro",
        "sto imparando troppo da voi...",
        "controllo in corso...nessuna nana avvistata 🤔",
        "error 404: Vansh è troppo bianco ⚠️"
    ]

    await update.message.reply_text(random.choice(bug_messages))

# ⏱️ INATTIVITÀ 20 MINUTI
async def inactivity_bot(app):
    await asyncio.sleep(10)

    while True:
        await asyncio.sleep(60)

        idle = time.time() - last_message_time

        if idle > 600:
            chat_id = -1002717082257/73541  # 🔴 METTI ID GRUPPO

            if chat_id:
                try:
                    await app.bot.send_message(
                        chat_id,
                        random.choice([
                            "allora? tutti a farsi le seghe?",
                            "nessuno parla?",
                            "Ufficiale: Gruppo morto",
                            "Gruppo morto, tutti froci",
                            "se non parla nessuno, vuoldire che Vansh è morto, e ci godo. Type shii"
                        ])
                    )
                except:
                    pass

# ▶️ START
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("add", add_user))
app.add_handler(CommandHandler("remove", remove_user))
app.add_handler(CommandHandler("edit", edit_user))
app.add_handler(CommandHandler("list", list_users))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_tag))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, human_bug))

async def post_init(app):
    asyncio.create_task(inactivity_bot(app))

app.post_init = post_init

if __name__ == "__main__":
    print("Bot avviato correttamente")
    app.run_polling()

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

TOKEN = os.getenv("BOT_TOKEN")

FILE_DB = "users.json"
GROUPS_FILE = "groups.json"

# =========================
# USERS DB
# =========================
def load_users():
    if os.path.exists(FILE_DB):
        with open(FILE_DB, "r") as f:
            return json.load(f)
    return {}

def save_users(data):
    with open(FILE_DB, "w") as f:
        json.dump(data, f, indent=4)

users = load_users()

# =========================
# GROUPS DB (MULTIGRUPPO)
# =========================
def load_groups():
    if os.path.exists(GROUPS_FILE):
        try:
            with open(GROUPS_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_groups(data):
    with open(GROUPS_FILE, "w") as f:
        json.dump(data, f, indent=4)

groups = load_groups()

# =========================
# STATO BOT
# =========================
message_count = 0
last_message_time = time.time()

# =========================
# ADMIN CHECK
# =========================
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id
    )
    return member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]

# =========================
# ADD USERS
# =========================
async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    if not await is_admin(update, context):
        return await update.message.reply_text("Solo admin ❌")

    lines = (update.message.text or "").split("\n")[1:]

    if not lines:
        return await update.message.reply_text("Formato:\n/add\nnome → @tag")

    for line in lines:
        if "→" in line:
            name, tag = line.split("→", 1)
            users[name.strip().lower()] = tag.strip()

    save_users(users)
    await update.message.reply_text("Aggiunti ✅")

# =========================
# LIST USERS (FIXATA)
# =========================
async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not users:
        return await update.message.reply_text("Vuoto")

    msg = "\n".join([f"{k} → {v}" for k, v in users.items()])
    await update.message.reply_text(msg)

# =========================
# AUTO TAG + SAVE GROUP
# =========================
async def auto_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global message_count, last_message_time

    if not update.message or not update.message.text:
        return

    # salva gruppo automaticamente (MULTIGRUPPO)
    chat_id = update.effective_chat.id
    if chat_id not in groups:
        groups.append(chat_id)
        save_groups(groups)

    message_count += 1
    last_message_time = time.time()

    text = re.sub(r'[^\w\s]', '', update.message.text.lower())

    found = [users[n] for n in users if n in text.split()]

    if found:
        await update.message.reply_text(" ".join(set(found)))

    # ogni 20 messaggi
    if message_count % 20 == 0:
        await update.message.reply_text(random.choice([
            "non freca",
            "no way",
            "type shi",
            "Sybau"
        ]))

# =========================
# HUMAN BUG (NON TOCCATE FRASI)
# =========================
last_bug_time = 0

async def human_bug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_bug_time

    if not update.message or not update.message.text:
        return

    now = time.time()

    if now - last_bug_time < 20:
        return

    if random.randint(1, 4) != 1:
        return

    last_bug_time = now

    await update.message.reply_text(random.choice([
        "errore... qualcosa non freca",
        "analizzando... troppe nane",
        "strano... nessuno litiga oggi",
        "sistema instabile... Galif è bianco",
        "attenzione: comportamento sospetto, Vansh non sta simpando",
        "qualcuno ha detto una minchiata",
        "errore 404: Galif non trovato, è troppo negro",
        "quanto cazzo parli Vansh",
        "controllo in corso... nessuna nana avvistata 🤔",
        "error 404: Vansh è troppo bianco ⚠️"
    ]))

# =========================
# INATTIVITÀ MULTIGRUPPO
# =========================
async def inactivity_bot(app):
    await asyncio.sleep(10)

    while True:
        await asyncio.sleep(60)

        idle = time.time() - last_message_time

        if idle > 600:  # 10 minuti
            for chat_id in groups:
                try:
                    await app.bot.send_message(
                        chat_id,
                        random.choice([
                            "allora? cos'è tutti a farsi le seghe?",
                            "cazzo è sto silenzio oh",
                            "gruppo morto, tutti froci",
                            "strano...troppo silenzio",
                            "sistema instabile...tutti negri",
                            "morto Vansh, morto il gruppo",
                            "type shi",
                            "Straight Up💔🥀",
                            "nel dubbio, colpa di Vansh",
                        ])
                    )
                except:
                    pass

# =========================
# START
# =========================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("add", add_user))
app.add_handler(CommandHandler("list", list_users))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_tag))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, human_bug))

async def post_init(app):
    asyncio.create_task(inactivity_bot(app))

app.post_init = post_init

if __name__ == "__main__":
    print("Bot avviato")
    app.run_polling()

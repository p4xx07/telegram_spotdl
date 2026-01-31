import os
import re
import json
import time
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ===== ENV =====
TOKEN = os.getenv("TELEGRAM_TOKEN")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
GENIUS_TOKEN = os.getenv("GENIUS_TOKEN")

# ===== PATHS =====
CONFIG_DIR = "/root/.config/spotdl"
CONFIG_PATH = f"{CONFIG_DIR}/config.json"
MUSIC_OUTPUT = "/music/{artist}/{title}.{output-ext}"

# ===== BOT SETTINGS =====
BUFFER_TIME = 5  # seconds between telegram updates
SPOTIFY_REGEX = r"(https?://open\.spotify\.com/[^\s]+)"

with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

config["client_id"] = SPOTIFY_CLIENT_ID
config["client_secret"] = SPOTIFY_CLIENT_SECRET
config["genius_token"] = GENIUS_TOKEN
config["output"] = MUSIC_OUTPUT

with open(CONFIG_PATH, "w") as f:
    json.dump(config, f, indent=4)

ALLOWED_TELEGRAM_USERS = os.getenv("ALLOWED_TELEGRAM_USERS")

if ALLOWED_TELEGRAM_USERS:
    ALLOWED_TELEGRAM_USERS = {
        int(uid.strip())
        for uid in ALLOWED_TELEGRAM_USERS.split(",")
        if uid.strip().isdigit()
    }
else:
    ALLOWED_TELEGRAM_USERS = None  # allow all


# ===== TELEGRAM HANDLER =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if ALLOWED_TELEGRAM_USERS and user_id not in ALLOWED_TELEGRAM_USERS:
        await update.message.reply_text("You are not allowed to use this bot.")
        return

    text = update.message.text or ""
    match = re.search(SPOTIFY_REGEX, text)
    if not match:
        await update.message.reply_text(f"insert a valid spotify url")
        return

    spotify_link = match.group(1)
    await update.message.reply_text(f"Downloading:\n{spotify_link}")

    process = subprocess.Popen(
        ["spotdl", "download", spotify_link],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    for line in process.stdout:
        print(line.rstrip())

    if process.returncode == 0:
        await update.message.reply_text("Download complete ✅")
    else:
        await update.message.reply_text("Download failed ❌")


# ===== MAIN =====
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

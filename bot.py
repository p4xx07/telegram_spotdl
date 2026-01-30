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

# ===== PATHS =====
CONFIG_DIR = "/root/.config/spotdl"
CONFIG_PATH = f"{CONFIG_DIR}/config.json"
MUSIC_OUTPUT = "/music/{artist}/{title}.{ext}"

# ===== BOT SETTINGS =====
BUFFER_TIME = 5  # seconds between telegram updates
SPOTIFY_REGEX = r"(https?://open\.spotify\.com/track/[a-zA-Z0-9]+)"

# ===== SETUP SPOTDL CONFIG =====
os.makedirs(CONFIG_DIR, exist_ok=True)

if not os.path.exists(CONFIG_PATH):
    subprocess.run(["spotdl", "--generate-config"], check=True)

with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

config.setdefault("spotify", {})
config["spotify"]["client_id"] = SPOTIFY_CLIENT_ID
config["spotify"]["client_secret"] = SPOTIFY_CLIENT_SECRET
config["output"] = MUSIC_OUTPUT

with open(CONFIG_PATH, "w") as f:
    json.dump(config, f, indent=4)


# ===== TELEGRAM HANDLER =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    match = re.search(SPOTIFY_REGEX, text)
    if not match:
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

    buffer = []
    last_sent = time.time()

    for line in process.stdout:
        buffer.append(line.rstrip())

        if time.time() - last_sent >= BUFFER_TIME:
            await update.message.reply_text(
                "```\n" + "\n".join(buffer[-15:]) + "\n```", parse_mode="Markdown"
            )
            last_sent = time.time()

    process.wait()

    if process.returncode == 0:
        await update.message.reply_text("Download complete ✅")
    else:
        await update.message.reply_text("Download failed ❌")


# ===== MAIN =====
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

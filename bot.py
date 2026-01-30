import os
import re
import subprocess
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")
CONFIG_PATH = "/app/spotdl.config.json"

SPOTIFY_REGEX = r"(https?://open\.spotify\.com/track/[a-zA-Z0-9]+)"

BUFFER_TIME = 5  # seconds between messages


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    match = re.search(SPOTIFY_REGEX, text)
    if not match:
        return

    spotify_link = match.group(1)
    await update.message.reply_text(f"Downloading {spotify_link}...")

    # Run spotdl and capture stdout
    process = subprocess.Popen(
        ["spotdl", "download", spotify_link, "--config", CONFIG_PATH],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    buffer = []
    last_sent = time.time()

    for line in process.stdout:
        buffer.append(line.strip())
        # Send buffer every BUFFER_TIME seconds
        if time.time() - last_sent > BUFFER_TIME:
            if buffer:
                await update.message.reply_text(
                    "```\n" + "\n".join(buffer) + "\n```", parse_mode="Markdown"
                )
                buffer = []
                last_sent = time.time()

    # Send any remaining output
    if buffer:
        await update.message.reply_text(
            "```\n" + "\n".join(buffer) + "\n```", parse_mode="Markdown"
        )

    process.wait()
    if process.returncode == 0:
        await update.message.reply_text("Download complete!")
    else:
        await update.message.reply_text("Download failed.")

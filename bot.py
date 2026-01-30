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


ALLOWED_USERS = {
    int(uid)
    for uid in os.getenv("ALLOWED_TELEGRAM_USERS", "").split(",")
    if uid.strip().isdigit()
}


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if ALLOWED_USERS and user.id not in ALLOWED_USERS:
        await update.message.reply_text(f"user not allowed")
        return

    text = update.message.text
    match = re.search(SPOTIFY_REGEX, text)
    if not match:
        await update.message.reply_text(f"this link is not valid: {text}...")
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


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()


if __name__ == "__main__":
    main()

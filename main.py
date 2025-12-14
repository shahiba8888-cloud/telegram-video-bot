import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp

BOT_TOKEN = "8309321138:AAFqV5eD2yivqTETECq0XyaP6RRmCqDNTJg"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Send me any public video link or direct file link."
    )

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    chat_id = update.message.chat_id
    await update.message.reply_text("⏳ Processing...")

    # Try video
    try:
        ydl_opts = {'format': 'best', 'outtmpl': 'video.%(ext)s'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(info)

        await context.bot.send_video(chat_id=chat_id, video=open(file, 'rb'))
        os.remove(file)
        return
    except:
        pass

    # Try direct file
    try:
        r = requests.get(url, stream=True, timeout=20)
        if r.status_code == 200:
            name = url.split("/")[-1] or "file"
            with open(name, "wb") as f:
                for c in r.iter_content(1024 * 1024):
                    if c:
                        f.write(c)

            await context.bot.send_document(chat_id=chat_id, document=open(name, 'rb'))
            os.remove(name)
        else:
            await update.message.reply_text("❌ Invalid link")
    except:
        await update.message.reply_text("❌ Download failed")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

print("Bot running...")
app.run_polling()

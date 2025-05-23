import os
import yt_dlp
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, ContextTypes, filters

LOG_FILE = "log.csv"

def save_log(user_id, username, format_choice, url):
    data = {'user_id': [user_id], 'username': [username], 'format': [format_choice], 'url': [url]}
    df = pd.DataFrame(data)
    if os.path.exists(LOG_FILE):
        df.to_csv(LOG_FILE, mode='a', index=False, header=False)
    else:
        df.to_csv(LOG_FILE, index=False)

def download(url, format_choice):
    if format_choice == "480p":
        out_file = "download_480p.mp4"
        ydl_opts = {
            'outtmpl': out_file,
            'format': 'bestvideo[height<=480]+bestaudio/best',
            'merge_output_format': 'mp4',
            'noplaylist': True,
            'quiet': True,
        }
    elif format_choice == "720p":
        out_file = "download_720p.mp4"
        ydl_opts = {
            'outtmpl': out_file,
            'format': 'bestvideo[height<=720]+bestaudio/best',
            'merge_output_format': 'mp4',
            'noplaylist': True,
            'quiet': True,
        }
    else:
        raise Exception("❌ Định dạng không hợp lệ.")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return out_file

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    context.user_data['url'] = url

    buttons = [
        [InlineKeyboardButton("📺 MP4 480p", callback_data='480p')],
        [InlineKeyboardButton("📺 MP4 720p", callback_data='720p')],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("🔽 Chọn chất lượng video muốn tải:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    format_choice = query.data
    url = context.user_data.get('url')
    user = query.from_user

    await query.edit_message_text("⏳ Đang tải video...")

    try:
        file_path = download(url, format_choice)
        save_log(user.id, user.username, format_choice, url)
        await query.message.reply_video(video=open(file_path, 'rb'))
        os.remove(file_path)
    except Exception as e:
        await query.message.reply_text(f"⚠️ Lỗi khi tải video: {e}")

if __name__ == '__main__':
    TOKEN = "7577926725:AAG2evwhjXmhbNzCMEnwFv7uR-ys4FGTIL0"
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("🚀 Bot đang chạy...")
    app.run_polling()

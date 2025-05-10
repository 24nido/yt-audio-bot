import threading
import os
import glob
import asyncio
import ffmpeg
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from http.server import BaseHTTPRequestHandler, HTTPServer

# Environment variable for bot token
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Function to get the duration of the audio
def get_audio_duration(filename):
    try:
        info = ffmpeg.probe(filename, select_streams='a:0', show_entries='stream=duration', v='error')
        return float(info['streams'][0]['duration'])
    except:
        return None

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎧 𝑺𝒆𝒏𝒅 𝒎𝒆 𝒂 𝒀𝒐𝒖𝑻𝒖𝒃𝒆 𝒍𝒊𝒏𝒌 𝒕𝒐 𝒈𝒆𝒕 𝒕𝒉𝒆 𝒂𝒖𝒅𝒊𝒐!")

# Handle message and process the YouTube link
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("𝑷𝒍𝒆𝒂𝒔𝒆 𝒔𝒆𝒏𝒅 𝒂 𝒗𝒂𝒍𝒊𝒅 𝒀𝒐𝒖𝑻𝒖𝒃𝒆 𝑼𝑹𝑳.")
        return

    # Convert Shorts link to standard format
    if "youtube.com/shorts" in url:
        video_id = url.split("/")[-1].split("?")[0]
        url = f"https://www.youtube.com/watch?v={video_id}"

    await update.message.reply_text("𝑫𝒐𝒘𝒏𝒍𝒐𝒂𝒅𝒊𝒏𝒈 𝒉𝒊𝒈𝒉-𝒒𝒖𝒂𝒍𝒊𝒕𝒚 𝒂𝒖𝒅𝒊𝒐... 𝑷𝒍𝒆𝒂𝒔𝒆 𝒘𝒂𝒊𝒕.")
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
            'noplaylist': True,
            'quiet': False,
            'geo_bypass': True,  # 👈 ye line add karni hai
            'forceipv4': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        mp3_files = glob.glob("*.mp3")
        if mp3_files:
            duration = get_audio_duration(mp3_files[0])
            if duration and duration > 2100:
                await update.message.reply_text("❌ 𝑽𝒊𝒅𝒆𝒐 𝒊𝒔 𝒕𝒐𝒐 𝒍𝒐𝒏𝒈. 𝑴𝒂𝒙 𝒂𝒍𝒍𝒐𝒘𝒆𝒅 𝒍𝒆𝒏𝒈𝒕𝒉 𝒊𝒔 ~35 𝒎𝒊𝒏𝒖𝒕𝒆𝒔.")
                os.remove(mp3_files[0])
                return

            # Send the audio
            with open(mp3_files[0], 'rb') as audio_file:
                await update.message.reply_audio(audio=audio_file)

            # Optional message after sending
            await update.message.reply_text("✅ 𝑨𝒖𝒅𝒊𝒐 𝒔𝒆𝒏𝒕. 𝑺𝒂𝒗𝒆 𝒊𝒕 𝒊𝒇 𝒚𝒐𝒖 𝒘𝒊𝒔𝒉.")

            # Delete file
            os.remove(mp3_files[0])
        else:
            await update.message.reply_text("❌ 𝘾𝙤𝙪𝙡𝙙 𝙣𝙤𝙩 𝙙𝙤𝙬𝙣𝙡𝙤𝙖𝙙 𝙖𝙪𝙙𝙞𝙤. 𝙏𝙧𝙮 𝙖𝙜𝙖𝙞𝙣 𝙡𝙖𝙩𝙚𝙧.")

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# Web server handler to keep the service running
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Telegram bot is running.')

# Function to run web server
def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('', port), Handler)
    server.serve_forever()

# Start the web server in a separate thread
threading.Thread(target=run_web_server).start()

# Main function to set up the bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()

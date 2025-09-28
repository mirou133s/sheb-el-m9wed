from flask import Flask
from threading import Thread
import asyncio
import discord
from discord.ext import commands
import os

# Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

# كود البوت - انسخ كل محتوى main.py هنا
from __future__ import annotations
import re
import requests
from discord import Embed, Intents, Activity, Status, Color, ActivityType, FFmpegOpusAudio
from yt_dlp import YoutubeDL
from youtubesearchpython import VideosSearch

# ... ضع كل كود البوت هنا بنفس الترتيب ...

# بدلاً من bot.run(DISCORD_TOKEN) في النهاية، استخدم هذا:
def run_bot():
    bot.run(os.environ['discordkey'])

def run_web():
    app.run(host='0.0.0.0', port=10000, debug=False)

def keep_alive():
    # تشغيل البوت في thread منفصل
    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # تشغيل الويب سيرفر
    run_web()

if __name__ == "__main__":
    keep_alive()

from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} is online!')

@bot.command()
async def test(ctx):
    await ctx.send('✅ Bot is working!')

def run_web():
    app.run(host='0.0.0.0', port=10000, debug=False)

# تشغيل الويب سيرفر
web_thread = Thread(target=run_web)
web_thread.daemon = True
web_thread.start()

# تشغيل البوت
bot.run(os.environ['discordkey'])

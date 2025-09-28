from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
import os

# ويب سيرفر
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

# البوت
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} is online!')

@bot.command()
async def test(ctx):
    await ctx.send('Bot is working!')

def run_bot():
    bot.run(os.environ['discordkey'])

def run_web():
    app.run(host='0.0.0.0', port=10000, debug=False)

if __name__ == "__main__":
    # تشغيل الويب سيرفر
    web_thread = Thread(target=run_web)
    web_thread.daemon = True
    web_thread.start()
    
    # تشغيل البوت
    run_bot()

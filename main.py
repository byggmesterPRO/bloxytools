#Importing Packages
import asyncio
import discord
intents = discord.Intents.default()
intents.members = True
import json
import asyncpg
import time
import os
import sys
import requests

from flask import Flask, request, Response
from discord_webhook import DiscordWebhook, DiscordEmbed
from functools import lru_cache
from discord.ext import commands, tasks
from aiohttp import web
from datetime import datetime, timedelta

#Opening Config.json to customize bot.
with open("lib/json/config.json", "r") as f:
    config = json.load(f)

#Defining variables
#Prefix/etc
PREFIX = config["prefix"]
UNIVERSAL_PREFIX = config["universal_prefix"]
#Database Variables
HOST = config['host']
DB_PW = config['db_pw']
DBL_TOKEN = config['dbl_token']
loop = asyncio.get_event_loop()

#Printing to verify for me ;)
print("Current UNIVERSAL_PREFIX is: {}".format(UNIVERSAL_PREFIX))
print("Current default PREFIX is: {}".format(PREFIX))

#Create the database Connection
async def create_db_pool():
    bot.db = await asyncpg.create_pool(database="einar", user="einar", host=HOST, password=DB_PW)
    print(f"Started database connection to {HOST}")




#Get's the prefix of the current server using their ID, this will default to ! unless they have changed their prefix
@lru_cache(maxsize=150)
async def get_prefix(bot, message):
    try:
        GUILD_PREFIX = await bot.db.fetch(f"SELECT guild_prefix FROM guild_prefixes WHERE guild_id=$1;", message.guild.id)
    except:
        GUILD_PREFIX = None
    if GUILD_PREFIX:
        prefix = [GUILD_PREFIX[0]['guild_prefix'], UNIVERSAL_PREFIX]
    else:
        prefix = [PREFIX, UNIVERSAL_PREFIX]
    return commands.when_mentioned_or(*prefix)(bot, message)

#Defining bot
bot = commands.Bot(command_prefix=get_prefix, description='Helper Bot', intents=intents)
bot.remove_command('help')

#Loading Cogs
cogsToBeLoaded = ['ErrorHandler', 'TestCog', 'Developer', 'ModMail']

for f in cogsToBeLoaded:
    bot.load_extension(f'lib.cogs.{f}')
    print(f'Loaded {f} cog')

#Starting Vote Tracker
def on_vote(data):
    response = requests.get(url=f'https://discord.com/api/v6/users/{data["user"]}', headers = {
        'Authorization': f"Bot {DBL_TOKEN}"
    })
    response = response.json()
    embed = DiscordEmbed(colour=discord.Colour(
            0x5d4b98), url="https://discordapp.com", description="Thanks for your vote!")
    embed.set_footer(text="Voting Tracker")
    embed.set_author(name=f"{response['username']}#{response['discriminator']} Voted!", url="https://discordapp.com",
                 icon_url=f"https://cdn.discordapp.com/avatars/{response['id']}/{response['avatar']}")

    webhook = DiscordWebhook(url='https://discord.com/api/webhooks/834082592957530152/1pVHnoKi70Xq2E9G9rIZAAI4bNVUvWz4F4P825FIqQhykgc7OFVy5oLlodKYgNuO4y3p')
    webhook.add_embed(embed)
    response = webhook.execute()
app = Flask(__name__)
@app.route('/webhook', methods=['POST'])
def respond():
    on_vote(request.json)
    return Response(status=200)
 



@tasks.loop(hours=24)
async def clear_today():
    with open('lib/json/stats.json', 'r') as f:
        stats = json.load(f)
    stats['commands_today'] = 0
    stats['verified_users_today'] = 0
    with open('lib/json/stats.json', 'w') as f:
        stats = json.dump(stats, f)
"""
@clear_today.before_loop
async def before_my_task():
    hour = 16
    minute = 42
    await bot.wait_until_ready()
    now = datetime.now()
    future = datetime.datetime(now.year, now.month, now.day, hour, minute)
    if now.hour >= hour and now.minute > minute:
        future += timedelta(days=1)
    await asyncio.sleep((future-now).seconds)
"""

#Run Connections/API's etc.
loop.run_until_complete(create_db_pool())
clear_today.start()

TOKEN = config['token2']
bot.run(TOKEN)
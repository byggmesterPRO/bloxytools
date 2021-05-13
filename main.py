#Importing Packages
import asyncio
import discord
"""
intents = discord.Intents.default()
intents.members = True
"""
import json
import asyncpg
import time
import os
import sys
import requests

from functools import lru_cache
from discord.ext import commands, tasks
from aiohttp import web
from datetime import datetime, timedelta

#Opening Config.json for the configuration of the bot
with open("lib/json/config.json", "r") as f:
    config = json.load(f)

#Defining variables
#Prefix/etc
PREFIX = config["prefix"]
UNIVERSAL_PREFIX = config["universal_prefix"]
#Database Variables
HOST = config['host']
DB_PW = config['db_pw']
DBL_TOKEN = config['token2']
loop = asyncio.get_event_loop()

#Printing to verify for me ;)
print("Current UNIVERSAL_PREFIX is: {}".format(UNIVERSAL_PREFIX))
print("Current default PREFIX is: {}".format(PREFIX))

#Create the database Connection
async def create_db_pool():
    bot.db = await asyncpg.create_pool(database="einar", user="einar", host=HOST, password=DB_PW)
    print("Started database connection")




#Get's the prefix of the current server using their ID, this will default to ! unless they have changed their prefix
async def get_prefixDict():
    fetched = await bot.db.fetch("SELECT guild_id, guild_prefix FROM guild_prefixes;")
    processedDict = {}
    for _ in range(len(fetched)):
        processedDict.update({str(fetched[_]['guild_id']) : str(fetched[_]['guild_prefix'])})
    with open("lib/json/guild_prefixes.json", "r") as f:
        guild_prefixes = json.load(f)
    guild_prefixes.clear()
    with open("lib/json/guild_prefixes.json", "w") as f:
        dump = json.dumps(processedDict)

    return processedDict



async def get_prefix(bot, message):
    try:
        GUILD_PREFIX = await bot.db.fetch("SELECT guild_prefix FROM guild_prefixes WHERE guild_id=$1;", message.guild.id)
    except:
        GUILD_PREFIX = None
    if GUILD_PREFIX:
        prefix = [GUILD_PREFIX[0]['guild_prefix'], UNIVERSAL_PREFIX]
    else:
        prefix = [PREFIX, UNIVERSAL_PREFIX]
    return commands.when_mentioned_or(*prefix)(bot, message)

#Defining bot
#bot = commands.Bot(command_prefix=get_prefix, description='Helper Bot', intents=intents)
bot = commands.Bot(command_prefix=get_prefix, description='Helper Bot')
bot.remove_command('help')

#Loading Cogs
cogsToBeLoaded = ['ErrorHandler', 'TestCog', 'Developer', 'ModMail', 'PointStore', 'Verification']

for f in cogsToBeLoaded:
    bot.load_extension(f'lib.cogs.{f}')
    print(f'Loaded {f} cog')

@bot.command()
async def reload(ctx):
    if ctx.author.id != 257073333273624576:
        return
    errorMessage = ''
    for cog in cogsToBeLoaded:
        try:
            bot.unload_extension(f'lib.cogs.{cog}')
        except:
            errorMessage += f'{cog} failed to unload\n'
    await ctx.send("Unloaded all the cogs | Error: " + errorMessage)
    errorMessage = ''
    for cog in cogsToBeLoaded:
        try:
            bot.load_extension(f'lib.cogs.{cog}')
        except:
            errorMessage += f'{cog} failed to load\n'
    await ctx.send("Loaded all the cogs | Error: " + errorMessage)




@tasks.loop(hours=24)
async def clear_today():
    with open('lib/json/stats.json', 'r') as f:
        stats = json.load(f)
    stats['commands_today'] = 0
    stats['verified_users_today'] = 0
    with open('lib/json/stats.json', 'w') as f:
        stats = json.dump(stats, f)


#Run Connections/API's etc.
loop.run_until_complete(create_db_pool())
clear_today.start()
TOKEN = config['token']
bot.run(TOKEN)
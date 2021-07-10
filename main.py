#Importing Packages
import asyncio
import discord
"""
intents = discord.Intents.default()
intents.members = True
"""
import json
import asyncpg
from datetime import datetime as date
from discord.ext import commands, tasks
from cache import AsyncLRU
def bloxy_print(message):
    print("[ {}  Bloxy Console ] {}".format(date.today().strftime("%d/%m/%Y %H:%M:%S"), message))

#Opening Config.json for the configuration of the bot
with open("lib/json/config.json", "r") as f:
    config = json.load(f)
with open("lib/json/channels.json", "r") as f:
    channels = json.load(f)
with open("lib/json/var.json", "r") as f:
    var = json.load(f)
#Defining variables
#Prefix/etc
PREFIX = config["prefix"]
UNIVERSAL_PREFIX = config["universal_prefix"]
#Database Variables
HOST = config['host']
DB_PW = config['db_pw']
DBL_TOKEN = config['token2']
loop = asyncio.get_event_loop()

print("""

.______    __        ______   ___   ___ ____    ____   .___________.  ______     ______    __          _______.
|   _  \  |  |      /  __  \  \  \ /  / \   \  /   /   |           | /  __  \   /  __  \  |  |        /       |
|  |_)  | |  |     |  |  |  |  \  V  /   \   \/   /    `---|  |----`|  |  |  | |  |  |  | |  |       |   (----`
|   _  <  |  |     |  |  |  |   >   <     \_    _/         |  |     |  |  |  | |  |  |  | |  |        \   \    
|  |_)  | |  `----.|  `--'  |  /  .  \      |  |           |  |     |  `--'  | |  `--'  | |  `----.----)   |   
|______/  |_______| \______/  /__/ \__\     |__|           |__|      \______/   \______/  |_______|_______/    
                                                                                                               

""")
#Printing to verify for me ;)
bloxy_print("Current UNIVERSAL_PREFIX is: {}".format(UNIVERSAL_PREFIX))
bloxy_print("Current default PREFIX is: {}".format(PREFIX))

#Create the database Connection
async def create_db_pool():
    bot.db = await asyncpg.create_pool(database="einar", user="einar", host=HOST, password=DB_PW)
    bloxy_print("Started database connection")


async def get_prefix(bot, message):
    try:
        GUILD_PREFIX = await bot.db.fetchrow("SELECT guild_prefix FROM guild_prefixes WHERE guild_id=$1;", message.guild.id)
    except:
        GUILD_PREFIX = None
    if GUILD_PREFIX:
        prefix = [GUILD_PREFIX['guild_prefix'], UNIVERSAL_PREFIX]
    else:
        prefix = [PREFIX, UNIVERSAL_PREFIX]
    return commands.when_mentioned_or(*prefix)(bot, message)

#Defining bot
#bot = commands.Bot(command_prefix=get_prefix, description='Helper Bot', intents=intents)
bot = commands.AutoShardedBot(command_prefix=get_prefix, description='Helper Bot', help_command=None)

#Loading Cogs
cogsToBeLoaded = ['ErrorHandler', 'Developer', 'PointStore', 'RobloxCommands', 'Misc']

for f in cogsToBeLoaded:
    bot.load_extension(f'lib.cogs.{f}')
    bloxy_print(f'Loaded {f} cog')


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
    await ctx.send("Unloaded all the cogs... "+ errorMessage)
    errorMessage = ''
    for cog in cogsToBeLoaded:
        bot.load_extension(f'lib.cogs.{cog}')
    await ctx.send("Loaded all the cogs..." + errorMessage)




@tasks.loop(hours=24)
async def clear_today():
    with open('lib/json/stats.json', 'r') as f:
        stats = json.load(f)
    stats['commands_today'] = 0
    stats['verified_users_today'] = 0
    with open('lib/json/stats.json', 'w') as f:
        stats = json.dump(stats, f)
def get_guildCount():
    guild_count = 0
    for guild in bot.guilds:
        guild_count += 1
    return str(guild_count)

@tasks.loop(seconds=60)
async def change_pr():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="{} Servers | bt!help".format(get_guildCount())))


@bot.event
async def on_shard_ready(shard_id):
    bloxy_print("SHARD_ID: " + str(shard_id) + " | your " + var['shards'][int(shard_id)] + " Is ready!")



#Run Connections/API's etc.
loop.run_until_complete(create_db_pool())
clear_today.start()
bot.loop.create_task(change_pr())
TOKEN = config['token']
bot.run(TOKEN)
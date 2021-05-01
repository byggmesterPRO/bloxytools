from main import UNIVERSAL_PREFIX
import discord
import requests
import json
import aiohttp

from discord.ext import commands
from lib.styling import EmbedMaker
from lib.Functions import CommandProcess as cp

with open("lib/json/config.json", "r") as f:
    config = json.load(f)
with open("lib/json/store.json", "r") as f:
    store = json.load(f)

UNIVERSAL_PREFIX = config['universal_prefix']
storeIds = []
for _ in store['store']:    
    storeIds = storeIds + [store['store'][_]['id']]
class PointStore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def shop(self, ctx):
        embed = EmbedMaker.pointStore_Embed(ctx)
        await ctx.send(embed=embed)
        cp.process_command(ctx)
    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def buy(self, ctx, *, msg=None):
        if not msg:
            await ctx.send("Be sure to choose one of the numbers infront of the rank. type `bt!buy <id>`")
        if msg in storeIds:
            l = [storeIds.index(i) for i in storeIds if msg in i]
        cp.process_command(ctx)
    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def leaderboard(self, ctx, msg=None):
        if not msg:
            await ctx.send("Remember to type either `points` or `votes` when typing the command next time")
            return
        if msg.lower() not in ['votes', 'points']:
            await ctx.send("Remember to choose between `points` and `votes` when typing the command next time")
            return
        elif msg == 'votes':
            result = await self.bot.db.fetch("SELECT user_id, total_votes FROM point_data ORDER by total_votes DESC LIMIT 10;")
            value = 1
            processedString = "```\n"
            message = await ctx.send("Loading leaderboard...")
            for _ in range(len(result)):
                async with aiohttp.ClientSession() as session:
                    async with session.get(url=f'https://discord.com/api/v6/users/' + str(result[_]['user_id']), headers = {'Authorization': f"Bot Nzg5OTExNjMzMzIwMzQ1NjIw.X948iQ.k-Q5SMlQc7eGyOlmsPbWQ2_8QDo"}) as resp:
                        response = await resp.json()
                        username = response['username']
                        discriminator = response['discriminator']
                        processedString += (str(value) + " : " + username + "#" + discriminator + " | " +  str(result[_]['total_votes']) + " Total votes" +"\n")
                        value +=1
            processedString += "\n```"
            embed = EmbedMaker.default_embed(ctx, processedString)
            await message.edit(content="",embed=embed)
        elif msg == "points":
            result = await self.bot.db.fetch("SELECT user_id, points FROM point_data ORDER by points DESC LIMIT 10;")
            value = 1
            processedString = "```\n"
            message = await ctx.send("Loading leaderboard...")
            for _ in range(len(result)):
                async with aiohttp.ClientSession() as session:
                    async with session.get(url=f'https://discord.com/api/v6/users/' + str(result[_]['user_id']), headers = {'Authorization': f"Bot Nzg5OTExNjMzMzIwMzQ1NjIw.X948iQ.k-Q5SMlQc7eGyOlmsPbWQ2_8QDo"}) as resp:
                        response = await resp.json()
                        username = response['username']
                        discriminator = response['discriminator']
                        processedString += (str(value) + " : " + username + "#" + discriminator + " | " +  str(result[_]['points']) + " Total points" +"\n")
                        value +=1
            processedString += "\n```"
            embed = EmbedMaker.default_embed(ctx, processedString)
            await message.edit(content="",embed=embed)

        cp.process_command(ctx)

   

def setup(bot):
    bot.add_cog(PointStore(bot))

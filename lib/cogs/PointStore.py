import discord
import requests
import json
import aiohttp
import time
import asyncio

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

    @commands.command(aliases=['inv'])
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def inventory(self, ctx, *, arg=None):
        inv = await self.bot.db.fetchrow("SELECT inventory FROM point_data WHERE user_id=$1;", ctx.author.id)
        invString = ""
        if not inv['inventory']:
            invString = "Your inventory is empty!"
        else:
            for _ in range(len(inv['inventory'])):
                invString += (inv['inventory'][_] + "\n")
        embed = EmbedMaker.default_embed(ctx)
        embed.add_field(name="Inventory", value=invString)
        await ctx.send(embed=embed)
    @commands.command()
    @commands.is_owner()
    async def givepoints(self, ctx, user_id, *, arg:int):
        balance = await self.bot.db.fetchrow("SELECT points FROM point_data WHERE user_id=$1;", ctx.author.id)
        await self.bot.db.execute("UPDATE point_data SET points=$1 WHERE user_id=$2;", balance['points']+arg, int(user_id))
        await ctx.send(f"Gave `{user_id}`, {str(arg)} points!")
    @commands.command()
    @commands.is_owner()
    async def setpoints(self, ctx, user_id, *, arg:int):
        await self.bot.db.execute("UPDATE point_data SET points=$1 WHERE user_id=$2;", arg, int(user_id))
        await ctx.send(f"{user_id}'s points now set to `{str(arg)}`")
    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def shop(self, ctx):
        embed = EmbedMaker.pointStore_Embed(ctx)
        await ctx.send(embed=embed)
        cp.process_command(ctx)
    @commands.command(aliases=['bal', 'points'])
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def balance(self, ctx):
        balance = await self.bot.db.fetchrow("SELECT points FROM point_data WHERE user_id=$1;", ctx.author.id)
        embed = EmbedMaker.default_embed(ctx, f"You have {balance['points']} points!")
        await ctx.send(embed=embed)    
    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def buy(self, ctx, *, msg=None):
        if not msg:
            await ctx.send(f"Be sure to choose one of the numbers infront of the rank. type `{UNIVERSAL_PREFIX}buy <id>`")
        if msg in storeIds:
            cp.process_command(ctx)
            l = [storeIds.index(i) for i in storeIds if msg in i]
            price = store['store'][storeIds[l[0]]]['price']
            title = store['store'][storeIds[l[0]]]['title']
            id = store['store'][storeIds[l[0]]]['id']
            balance = await self.bot.db.fetchrow("SELECT points, inventory FROM point_data WHERE user_id=$1;", ctx.author.id)
            if balance['points'] >= price:
                pass
            else:
                await ctx.send("You can't afford this!")
                return
            message = await ctx.send(f"Are you sure you want to buy `{title}` for `{price}` points?")
            def check(reaction, user):
                return user == ctx.author and reaction.emoji in ['✅', '❌']
            await message.add_reaction(emoji="✅")
            await message.add_reaction(emoji="❌")
            try:
                reaction = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("You've used too long to answer!")
            else:
                reaction = str(reaction[0])
                if reaction == "✅":
                    newInventory = balance['inventory']
                    if not newInventory:
                        newInventory = []
                    newInventory += [id]
                    try:
                        await self.bot.db.execute("UPDATE point_data SET points=$1, inventory=$2 WHERE user_id=$3;", balance['points']-price, newInventory, ctx.author.id)
                    except:
                        embed = EmbedMaker.error_embed(ctx, "Failed to update points in database, report this in the support server.")
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send(f"{ctx.author.mention}, ✅ Successfully bought `{title}`!")
                elif reaction == "❌":
                    await ctx.send("❌, Cancelled!")
                else:
                    await ctx.send("weird " + reaction)
        
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
            t0 = time.time()
            result = await self.bot.db.fetch("SELECT user_id, total_votes FROM point_data ORDER by total_votes DESC LIMIT 10;")
            value = 1

            
            processedString = "```\n"
            message = await ctx.send("Loading leaderboard...")
            userIdsList = []
            userNamesList = []
            for _ in range(len(result)):
                userIdsList += [str(result[_]['user_id'])]
            async with aiohttp.ClientSession() as session:
                for _ in range(len(userIdsList)):
                    async with session.get(url=f'https://discord.com/api/v6/users/' + str(result[_]['user_id']), headers = {'Authorization': f"Bot Nzg5OTExNjMzMzIwMzQ1NjIw.X948iQ.k-Q5SMlQc7eGyOlmsPbWQ2_8QDo"}) as resp:
                        response = await resp.json()
                        userNamesList += [response['username'] + '#' + response['discriminator'] + ' | ']
            for _ in range(len(userNamesList)):
                processedString += (str(value) + ' | ' + userNamesList[_] + str(result[_]['total_votes']) + ' Total Votes\n')
                value+=1
            t1 = time.time()
            processedString += ("\n```\n" + ' Time it took:' + str(t1-t0))
            embed = EmbedMaker.default_embed(ctx, processedString)
            
            await message.edit(content="",embed=embed)
        elif msg == "points":
            t0 = time.time()
            result = await self.bot.db.fetch("SELECT user_id, points FROM point_data ORDER by points DESC LIMIT 10;")
            value = 1
            processedString = "```\n"
            message = await ctx.send("Loading leaderboard...")
            userIdsList = []
            userNamesList = []
            for _ in range(len(result)):
                userIdsList += [str(result[_]['user_id'])]
            async with aiohttp.ClientSession() as session:
                for _ in range(len(userIdsList)):
                    async with session.get(url=f'https://discord.com/api/v6/users/' + str(result[_]['user_id']), headers = {'Authorization': f"Bot Nzg5OTExNjMzMzIwMzQ1NjIw.X948iQ.k-Q5SMlQc7eGyOlmsPbWQ2_8QDo"}) as resp:
                        response = await resp.json()
                        userNamesList += [response['username'] + '#' + response['discriminator'] + ' | ']
            for _ in range(len(userNamesList)):
                processedString += (str(value) + ' | ' + userNamesList[_] + str(result[_]['points']) + ' Points\n')
                value+=1
            t1 = time.time()
            processedString += ("\n```\n" + ' Time it took:' + str(t1-t0))
            embed = EmbedMaker.default_embed(ctx, processedString)
            
            await message.edit(content="",embed=embed)

        cp.process_command(ctx)

   

def setup(bot):
    bot.add_cog(PointStore(bot))

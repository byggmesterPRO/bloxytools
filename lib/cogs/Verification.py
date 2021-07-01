import discord
import asyncio
import aiohttp
import json
import random

from lib.Functions import CommandProcess as cp 
from datetime import date
from discord.ext import commands

RANDOMWORDS = ['dino', 'orange', 'yellow', 'purple', 'green', 'red', 'roblox']
RANDOMWORDS2 = ['or', 'and']
def randomString():
    string1 = ""
    for i in range(0, 5):
        randomChoice = random.choice(RANDOMWORDS)
        randomChoice2 = random.choice(RANDOMWORDS2)
        string1 += (randomChoice2 + " " + randomChoice)
    return string1

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    


    @commands.command()
    @commands.cooldown(1.0, 10.0, commands.BucketType.user)
    async def verify(self, ctx, *, arg=None):
        await cp.process_command(ctx)
        IF_DEVELOPER = await self.bot.db.fetch("SELECT discord_id FROM developers WHERE discord_id=$1", ctx.author.id)
        if IF_DEVELOPER[0]['discord_id']:
            arg = arg or ctx.author.id
            checkIfAlreadyVerified = await self.bot.db.fetchrow("SELECT roblox_id FROM user_data WHERE discord_id=$1;", int(arg))
        else:
            checkIfAlreadyVerified = await self.bot.db.fetchrow("SELECT roblox_id FROM user_data WHERE discord_id=$1;", ctx.author.id)
        if checkIfAlreadyVerified == None:
            message = await ctx.send(f"{ctx.author.mention} 👋, It doesn't seem like you're verified yet! Do you wish to verify?")
            def check(reaction, user):
                return user == ctx.author and reaction.emoji in ['✅', '❌']
            await message.add_reaction(emoji="✅")
            await message.add_reaction(emoji="❌")
            try:
                reaction = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Command timed out!")
            else:
                reaction = str(reaction[0])
                if reaction == "✅":
                    await ctx.send("What's your roblox username? (Ex. ROBLOX) `You got 300 seconds`")
                    def check2(m):
                        return ctx.author == m.author and m.channel == ctx.channel
                    try:
                        username = await self.bot.wait_for('message', timeout=300.0, check=check2)
                        username = username.content.replace(" ", "%20")
                    except asyncio.TimeoutError:
                        await ctx.send("Command timed out!")
                    else:
                        async with aiohttp.ClientSession() as self.bot.session:
                            async with self.bot.session.get(f"https://api.roblox.com/users/get-by-username?username={username}") as r:
                                resp = await r.json()
                                try:
                                    error = resp['errorMessage']
                                except:
                                    pass
                                else:
                                    await ctx.send(f"{error}, please try using the verification command again!")
                                    return
                                randomGeneratedString = randomString()
                                await ctx.send(f"Put this into your description `{randomGeneratedString}` and type in the chat `done` when you have placed it there `You got 300 seconds`")
                                def check3(m):
                                    return ctx.author == m.author and m.channel == ctx.channel and m.content.lower() == 'done'
                                try:
                                    message = await self.bot.wait_for('message', timeout=300.0, check=check3)
                                except asyncio.TimeoutError:
                                    await ctx.send("Command timed out!")
                                else:
                                    if message.content.lower() == "done":
                                        robloxId = resp['Id']
                                        async with self.bot.session.get(f"https://users.roblox.com/v1/users/{robloxId}") as r:
                                            resp2 = await r.json()
                                            description = resp2['description']
                                            if description.replace(" ", "").lower() == randomGeneratedString.replace(" ", ""):
                                                await self.bot.db.execute("INSERT INTO user_data(roblox_id, discord_id, verified_at, verify_code) VALUES($1, $2, $3, $4);", robloxId, ctx.author.id, date.today(), randomGeneratedString)
                                                await ctx.send("You are now verified!")
                                            else:
                                                await ctx.send("It looks like you didn't put it correctly into your description, do the verify command again")



                                
                            
                elif reaction == "❌":
                    await message.edit(content="❌ Cancelled verification!")
        else:
            
            await ctx.send("You are verified! If you wish to change account or unverify type bt!unverify!")

    @commands.command()
    @commands.cooldown(1.0, 20.0, commands.BucketType.user)
    async def getroles(self, ctx):
        await cp.process_command(ctx)
        verified = await self.bot.db.fetchrow("SELECT discord_id FROM user_data WHERE discord_id=$1;", ctx.author.id)
        if not verified:
            await self.verify.callback(self, ctx)
            return
        


    @commands.command()
    async def unverify(self, ctx, *, arg=None):
        await cp.process_command(ctx)
        if arg and ctx.author.id == 257073333273624576:
            checkIfAlreadyVerified = await self.bot.db.fetchrow("SELECT roblox_id FROM user_data WHERE discord_id=$1;", int(arg))
            RobloxId = int(arg)
        else:
            checkIfAlreadyVerified = await self.bot.db.fetchrow("SELECT roblox_id FROM user_data WHERE discord_id=$1;", ctx.author.id)
            RobloxId = ctx.author.id 
        if checkIfAlreadyVerified == None:
            await ctx.send("You are not verified!")
            return
        await self.bot.db.execute("DELETE FROM user_data WHERE discord_id=$1;", RobloxId)
        await ctx.send("You are now unverified!")
def setup(bot):
    bot.add_cog(Verification(bot))
    
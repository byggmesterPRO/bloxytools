import discord
import asyncio
import aiohttp
import json
import random

from datetime import date
from discord.ext import commands

RANDOMWORDS = ['dino', 'orange', 'yellow', 'purple', 'green', 'red']
def randomString():
    string1 = ""
    for i in range(0, 5):
        randomChoice = random.choice(RANDOMWORDS)
        string1 += (" " + randomChoice)
    return string1

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    


    @commands.command()
    @commands.cooldown(1.0, 10.0, commands.BucketType.user)
    async def verify(self, ctx, *, arg=None):
        if arg:
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
                                try:
                                    message = await self.bot.wait_for('message', timeout=300.0, check=check2)
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
            
            await ctx.send("You are verified")

def setup(bot):
    bot.add_cog(Verification(bot))
    
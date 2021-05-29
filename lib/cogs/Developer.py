#Importing stuff
import discord
import asyncio
import os
import sys
import datetime
import time


from discord.ext import commands
from lib.styling import EmbedMaker

#The Cog itself
class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot=bot        
    @commands.command(name="restart", aliases=['RE', 'Re', 'rE', 're'])
    @commands.is_owner()
    async def restart(self, ctx):
        embed = discord.Embed(title=':octagonal_sign: I am restarting...', timestamp=datetime.datetime.utcnow(), color=0xff0000)
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="me restart."))
        await ctx.send(embed=embed)
        await asyncio.sleep(0.5)
        python = sys.executable
        os.execl(python, python, *sys.argv)

    @commands.command()
    @commands.is_owner()
    async def sql_execute(self, ctx, *, arg=None):
        if not arg:
            await ctx.send("No arg")
        else:
            await self.bot.db.execute(arg)
            await ctx.send("SQL String Executed!")

    @commands.command()
    @commands.is_owner()
    async def forceerror(self, ctx, *, arg):
        if arg.lower() == "TypeError".lower():
            arg = 1+""
        if arg.lower() == "argument":
            def argumentForceError(e):
                pass
            argumentForceError() 
def setup(bot):
    bot.add_cog(Developer(bot))
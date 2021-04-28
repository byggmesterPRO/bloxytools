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


    def prepare(self, string):
        arr = string.strip("```").replace("py\n", "").replace("python\n", "").split("\n")
        if not arr[::-1][0].replace(" ", "").startswith("return"):
            arr[len(arr) - 1] = "return " + arr[::-1][0]
        return "".join(f"\n\t{i}" for i in arr)

    @commands.command(pass_context=True, aliases=['eval', 'exec', 'evaluate'])
    @commands.is_owner()
    async def _eval(self, ctx, *, code: str):
        code = self.prepare(code)
        code = exec(code)
        await ctx.send(code)


def setup(bot):
    bot.add_cog(Developer(bot))
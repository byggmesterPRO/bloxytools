import discord
import requests
import json
from discord.ext import commands
from lib.styling import EmbedMaker

class PointStore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def shop(self, ctx):
        embed = EmbedMaker.pointStore_Embed(ctx)
        await ctx.send(embed=embed)


   

def setup(bot):
    bot.add_cog(PointStore(bot))

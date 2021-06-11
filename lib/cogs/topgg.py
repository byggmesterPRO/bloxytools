import dbl
import discord
import json
from discord.ext import commands, tasks
from lib.styling import EmbedMaker
import json

from lib.Functions import CommandProcess as cp
import asyncio
import logging

class TopGG(commands.Cog):
    """Handles interactions with the top.gg API"""

    def __init__(self, bot):
        self.bot = bot
        self.token = ('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Ijc4OTkxMTYzMzMyMDM0NTYyMCIsImJvdCI6dHJ1ZSwiaWF0IjoxNjExODU0NDAzfQ.jDj2_Mzsrn5Sest9yxzS92fNf-_p_buvg4HuW6sJwpo') # set this to your DBL token
        self.dblpy = dbl.DBLClient(self.bot, self.token, autopost=True) # Autopost will post your guild count every 30 minutes

    async def on_guild_post():
        print("Server count posted successfully")


    @commands.command()
    async def votecheck(self, ctx, *, arg=None):
        await cp.process_command(ctx)
        IF_DEVELOPER = await self.bot.db.fetch("SELECT discord_id FROM developers WHERE discord_id=$1", ctx.author.id)
        if IF_DEVELOPER[0]['discord_id']:
            arg = arg or ctx.author.id
        else:
            arg = ctx.author.id
        data = await self.dblpy.get_user_vote(arg)
        if data == True:
            response = "Thank you for voting :D I appreciate it!"
        else:
            response = "You haven't voted? Vote [here](https://top.gg/bot/789911633320345620/vote)!"
            embed = EmbedMaker.default_embed(ctx, response)
            await ctx.send(embed=embed)

    async def vote_check(self, ctx):
        data = await self.dblpy.get_user_vote(ctx.author.id)
        return data
def setup(bot):
    bot.add_cog(TopGG(bot))
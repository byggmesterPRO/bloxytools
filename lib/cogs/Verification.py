import discord
from discord.ext import commands


class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    

def setup(bot):
    bot.add_cog(Verification(bot))
    
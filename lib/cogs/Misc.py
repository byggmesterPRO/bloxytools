import discord
from discord.ext import commands
from lib.styling import EmbedMaker

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def support(self, ctx):
        embed = EmbedMaker.default_embed(ctx, "To get support then join the [support server](https://discord.gg/W3b6jHPMCg) or DM me!")
        await ctx.send(embed=embed)
    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def invite(self, ctx):
        pass    
    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def help(self, ctx):
        pass    
    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def language(self, ctx):
        embed = EmbedMaker.default_embed(ctx, "I'm a bot made in pure python!")
        await ctx.send(embed=embed)
    
    

def setup(bot):
    bot.add_cog(Misc(bot))

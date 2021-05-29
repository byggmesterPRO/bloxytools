import discord
import time
import json

from discord.ext import commands
from lib.styling import EmbedMaker
from lib.Functions import CommandProcess as cp
class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def support(self, ctx):
        cp.process_command(ctx)
        embed = EmbedMaker.default_embed(ctx, "To get support then join the [support server](https://discord.gg/W3b6jHPMCg) or DM me!")
        await ctx.send(embed=embed)
    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def invite(self, ctx):
        cp.process_command(ctx)
        embed = EmbedMaker.default_embed(ctx, "If you want to invite me to your server click this link; [invite Bloxy Tools]()")
        await ctx.send(embed=embed)
    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def help(self, ctx):
        cp.process_command(ctx)
        await ctx.send("This is not available yet...")
    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def language(self, ctx):
        cp.process_command(ctx)
        embed = EmbedMaker.default_embed(ctx, "I'm a bot made in pure python!")
        await ctx.send(embed=embed)
    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def ping(self, ctx):
        cp.process_command(ctx)
        latency = round(self.bot.latency * 1000)
        content = f"The current bot latency is `{latency}`ms"
        start = time.time()
        await ctx.send(content)
        end = time.time()
        await content.edit(content=(content + f" | Response time: {(end-start)*1000:,.0f}" ))
    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def changelog(self, ctx):
        cp.process_command(ctx)
        await ctx.send("This is not available yet...")
    
    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def stats_test(self, ctx):
        with open("lib/json/stats.json", "r") as f:
            stats = json.load(f)
        embed = EmbedMaker.default_embed(ctx, "This is the statistics for commands etc.")
        for i, j in stats.items():
            embed.add_field(name=str(i), value=str(stats[i]))
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Misc(bot))

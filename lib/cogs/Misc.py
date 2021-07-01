import discord
import time
import json

from datetime import date
from discord.ext import commands
from lib.styling import EmbedMaker
from lib.Functions import CommandProcess as cp
class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def support(self, ctx):
        await cp.process_command(ctx)
        embed = EmbedMaker.default_embed(ctx, "To get support then join the [support server](https://discord.gg/W3b6jHPMCg) or DM me!")
        await ctx.send(embed=embed)
    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def invite(self, ctx):
        await cp.process_command(ctx)
        embed = EmbedMaker.default_embed(ctx, "If you want to invite me to your server click this link; [invite Bloxy Tools]()")
        await ctx.send(embed=embed)
    @commands.command(aliases=['tools', 'cmds', 'commands'])
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def help(self, ctx, *, index):
        await cp.process_command(ctx)
        embed = EmbedMaker.default_embed(ctx)

    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def language(self, ctx):
        await cp.process_command(ctx)
        embed = EmbedMaker.default_embed(ctx, "I'm a bot made in pure python!")
        await ctx.send(embed=embed)
    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def ping(self, ctx):
        await cp.process_command(ctx)
        latency = round(self.bot.latency * 1000)
        content = f"The current bot latency is `{latency}`ms"
        start = time.time()
        await ctx.send(content)
        end = time.time()
        await content.edit(content=(content + f" | Response time: {(end-start)*1000:,.0f}" ))
    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def changelog(self, ctx):
        await cp.process_command(ctx)
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

    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def credits(self, ctx):
        await cp.process_command(ctx)
        await ctx.send("This bot was developed by byggmesterPRO#8206")
    @commands.command()
    @commands.cooldown(1.0, 30.0, commands.BucketType.user)
    @commands.has_permissions(administrator = True)
    async def changeprefix(self, ctx, *, prefix):
        check_prefix = await self.bot.db.fetchrow("SELECT guild_id FROM guild_prefixes WHERE guild_id=$1;", ctx.guild.id)
        if len(prefix) >= 6:
            await ctx.send("This is too long! Max length of a prefix is __*6*__")
            return
        if prefix == "!":
            await self.bot.db.execute("DELETE guild_prefixes WHERE guild_id=$1", ctx.guild.id)
        if not check_prefix:
            await self.bot.db.execute("INSERT INTO guild_prefixes(guild_id, guild_prefix, made_at) VALUES($1, $2, $3);", ctx.guild.id, prefix, date.today())
        else:
            await self.bot.db.execute("UPDATE guild_prefixes SET guild_prefix=$1, made_at=$2 WHERE guild_id=$3", prefix, date.today(), ctx.guild.id)
        await ctx.send("Changed prefix!")
    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def prefix(self, ctx):
        prefix = await self.bot.db.fetchrow("SELECT guild_prefix FROM guild_prefixes WHERE guild_id=$1;", ctx.guild.id)
        if not prefix:
            prefix = "!"
        else:
            prefix = prefix['guild_prefix']
        await ctx.send(f'Prefix for this server is `{prefix}`')

    

            
            
        


def setup(bot):
    bot.add_cog(Misc(bot))

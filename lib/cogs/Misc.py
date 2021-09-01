import discord
import time
import json

from datetime import date
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
         
        embed = EmbedMaker.default_embed(ctx, "If you want to invite me to your server click this link; [invite Bloxy Tools](https://discord.com/oauth2/authorize?client_id=789911633320345620&scope=bot&permissions=8)")
        await ctx.send(embed=embed)
    @commands.command(aliases=['tools', 'cmds', 'commands'])
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def help(self, ctx, *, index=None):
         
        embed = EmbedMaker.default_embed(ctx)
        embed.add_field(name="Roblox Commands", value="`user` - This command displays information about a Roblox user \n`randomuser` - This command displays a random user from Roblox!\n`age` - This command displays a more accurate representation of age on a Roblox user\n`game` - This displays information about a game, remember to choose a number between 1 and 5!\n")
        embed.add_field(name="Misc commands", value=" `changeprefix` - This command lets you change prefix for the guild as long as you got admin perms\n`prefix` - This command lets you know what prefix you have in your server \n`language` - Tells you what language this bot was made in!\n`ping` - pong\n`invite` - If you want to invite bloxy tools use this command!\n`changelog` - Show recent updates and fixes to the bot!\n`credits` - This displays the owner and creator of this bot.")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def language(self, ctx):
         
        embed = EmbedMaker.default_embed(ctx, "I'm a bot made in pure python!")
        await ctx.send(embed=embed)
    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def ping(self, ctx):
         
        latency = round(self.bot.latency * 1000)
        content = f"The current bot latency is `{latency}`ms"
        start = time.time()
        await ctx.send(content)
        end = time.time()
        await content.edit(content=(content + f" | Response time: {(end-start)*1000:,.0f}" ))
    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def changelog(self, ctx):
         
        await ctx.send("This is not available yet...")
    
    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def stats(self, ctx):
        stats = await self.bot.db.fetchrow("SELECT number FROM statistics WHERE type='commands_total'")
        embed = EmbedMaker.default_embed(ctx, "This is the statistics for commands etc.")
        embed.add_field(name="commands_total", value=stats['number'])
        guild_count = 0
        member_count = 0
        for guild in self.bot.guilds:
            member_count += guild.member_count
            guild_count += 1
        embed.add_field(name="Guilds and Members", value=f"Total Members = {member_count} | Total Guilds = {guild_count}")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def credits(self, ctx):
         
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
            await self.bot.db.execute("DELETE FROM guild_prefixes WHERE guild_id=$1;", ctx.guild.id)
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

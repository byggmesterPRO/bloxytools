#Importing stuff
import discord
import time
import json
import datetime
import asyncio

from discord.ext import commands
from lib.styling import EmbedMaker
from lib.Functions import CommandProcess as cp

#The Cog itself
class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot=bot        
    @commands.command()
    async def setlang(self, ctx, arg):
        arg = arg.lower()
        languages = ['en', 'no']
        IF_GUILD = await self.bot.db.fetch("SELECT guild_id FROM guild_prefixes WHERE guild_id=$1;", ctx.guild.id)
        if arg in languages:
            ARG_BOOL = True
        else:
            ARG_BOOL = False
        if IF_GUILD:
            if ARG_BOOL:
                await self.bot.db.execute("""
                UPDATE guild_prefixes SET lang=$1 WHERE guild_id=$2""", arg, ctx.guild.id)
                await ctx.send("Changed language!")
            else:
                await ctx.send("This is not a language!")
        else:
            if ARG_BOOL:
                await self.bot.db.execute("INSERT INTO guild_prefixes(guild_id, made_at, lang) VALUES($1, $2, $3);", ctx.guild.id, datetime.today(), arg)
                await ctx.send("Changed language!")
            else:
                await ctx.send("This is not a language")


    @commands.command()
    async def cooldown_embed(self, ctx):
        lang = await self.get_lang(ctx)
        embed = EmbedMaker.cooldown_embed(ctx, lang)
        embed.add_field(name="Cooldown!", value="You may retry after `this many seconds` seconds")
        await ctx.send(embed=embed)
        await cp.process_command(ctx)        

    @commands.command()
    async def embed_t(self, ctx):
        with open("lib/json/channels.json", "r") as f:
            channel = json.load(f)
        msg = "Yes message mhm good"
        main_guild = self.bot.get_guild(channel["server"])
        author = main_guild.get_member(611912213778661409)
        embed = discord.Embed(title="BLOXY_TITLE", description="", colour=author.author.color)

        embed.set_author(name="{} ({}#{})".format(author.display_name, ctx.author.name, ctx.author.discriminator),
                            icon_url=author.avatar_url)


        embed.timestamp = ctx.message.created_at

        embed.add_field(name="Message", value=msg[:1000] or "blank", inline=False)
        if len(msg) > 1000:
            embed.add_field(name="(Continued)", value=msg[1000:], inline=False)

        if ctx.message.attachments:
            embed.add_field(name="Attachments", value=", ".join([i.url for i in ctx.message.attachments]))

        embed.add_field(name="Sent from", value=f"**{ctx.author.display_name}** / {str(ctx.author.top_role)}")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1.0, 15.0, commands.BucketType.user)
    async def default_embed(self, ctx):
        embed = EmbedMaker.default_embed(ctx, "Default Embed Test")
        await ctx.send(embed=embed)
        await cp.process_command(ctx)

    @commands.command()
    async def error_embed(self, ctx):
        lang = await self.get_lang(ctx)
        embed = EmbedMaker.error_embed(ctx, "Error Embed Test", lang)
        await ctx.send(embed=embed)
        await cp.process_command(ctx)

    @commands.command()
    async def dbtest(self, ctx):
        t1 = time.time()
        RESPONSE = await self.bot.db.fetch(f"SELECT guild_prefix FROM guild_prefixes WHERE guild_id=$1;", ctx.guild.id)
        RESPONSE = RESPONSE[0]['guild_prefix']
        t2 = time.time()
        amount_time = t2 - t1
        await ctx.send(f"Time it took {amount_time}, Fetched {RESPONSE}")
    @commands.command()
    async def stats_test(self, ctx):
        with open("lib/json/stats.json", "r") as f:
            stats = json.load(f)
        embed = EmbedMaker.default_embed(ctx, "This is the statistics for commands etc.")
        for i, j in stats.items():
            embed.add_field(name=str(i), value=str(stats[i]))
        await ctx.send(embed=embed)
    @commands.command()
    async def updateall(self, ctx):
        await ctx.send("Fetching the member list and updating.")
        await asyncio.sleep(60)
        await ctx.send("All users is updated!")

def setup(bot):
    bot.add_cog(TestCog(bot))
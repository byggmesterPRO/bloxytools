#Importing stuff
import discord
import json
import os
import sys
import traceback

from discord.ext import commands
from discord.errors import Forbidden
from discord.ext.commands import CommandNotFound, BadArgument, MissingRequiredArgument, CommandOnCooldown, MissingPermissions
from lib.styling import EmbedMaker

#Defining variables
IGNORE_EXCEPTIONS=(CommandNotFound, BadArgument)

with open("lib/json/config.json", "r") as f:
    config = json.load(f)
UNIVERSAL_PREFIX = config['universal_prefix']
#The Cog itself
class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot=bot        
    @commands.Cog.listener()
    async def on_command_error(self, ctx, exc):
        if isinstance(exc, commands.CommandInvokeError):
            error = exc.original
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
            pass
        elif isinstance(exc, CommandNotFound):
            pass
        elif isinstance(exc, MissingPermissions):
            embed = EmbedMaker.error_embed(ctx, "I am missing one or more permissions to execute this command!")
            try:
                await ctx.send(embed=embed)
            except:
                try:
                    await ctx.send("I am missing permission to do this!")
                except:
                    user = await self.bot.fetch_user(ctx.author.id)
                    await user.send("I am missing permissions to do this?")
        elif isinstance(exc, Forbidden):
            embed = EmbedMaker.error_embed(ctx, "I am missing one or more permissions to execute this command!")
            try:
                await ctx.send(embed=embed)
            except:
                try:
                    await ctx.send("I am missing permission to do this!")
                except:
                    pass
        elif isinstance(exc, MissingRequiredArgument):
            embed = EmbedMaker.default_embed(ctx)
            error = str(exc).split(' ', 1)[0]
            embed.add_field(name="Missing Required Argument", value=f"```diff\n- Missing required argument <{error}>\n+ {UNIVERSAL_PREFIX}{ctx.command.qualified_name} <{error}>\n``` ")
            await ctx.send(embed=embed)
        elif isinstance(exc, CommandOnCooldown):
            embed = EmbedMaker.cooldown_embed(ctx, f"You may retry after {exc.retry_after:,.2f} seconds")
            await ctx.send(embed=embed)
        elif isinstance(exc, MissingPermissions):
            embed = EmbedMaker.error_embed(ctx, "You are missing permissions!")
            await ctx.send(embed=embed)
        elif isinstance(exc, KeyError):
            embed = EmbedMaker.error_embed(ctx, "That's not a username my guy")
            await ctx.send(embed=embed)
        else:
            embed = EmbedMaker.error_embed(ctx, "Unkown error! Please screenshot this and send it in the support server!")
            try:
                await ctx.send(embed=embed)
            except:
                print(str(exc))
                print("\n\n")
            embed = EmbedMaker.errorReport_embed(ctx, (str(exc.original) + "\n" + str(exc) + "\n```\n" + str(traceback.format_exc()) + "\n```"))
                

            channel = self.bot.get_channel(843395745741537310)
            if not str(exc) == "You do not own this bot.":
                if "Command raised an exception: Forbidden: 403 Forbidden (error code: 50013): Missing Permissions" in str(exc):
                    return
                await channel.send(embed=embed)
            try:
                raise exc.original
            except:
                raise exc

def setup(bot):
    bot.add_cog(ErrorHandler(bot))
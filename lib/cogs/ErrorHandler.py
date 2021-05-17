#Importing stuff
import discord


from discord.ext import commands
from discord.errors import Forbidden
from discord.ext.commands import CommandNotFound, BadArgument, MissingRequiredArgument, CommandOnCooldown, MissingPermissions
from lib.styling import EmbedMaker

#Defining variables
IGNORE_EXCEPTIONS=(CommandNotFound, BadArgument)

#The Cog itself
class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot=bot        
    @commands.Cog.listener()
    async def on_command_error(self, ctx, exc):
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
            pass
        elif isinstance(exc, CommandNotFound):
            pass
        elif isinstance(exc, Forbidden):
            embed = EmbedMaker.error_embed(ctx, "I am missing one or more permissions to execute this command!")
            await ctx.send(embed=embed)
        elif isinstance(exc, MissingRequiredArgument):
            embed = EmbedMaker.error_embed(ctx, "One or more required arguments is missing!")
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
            await ctx.send(embed=embed)
            embed = EmbedMaker.errorReport_embed(ctx, (str(exc.original) + "\n" + str(exc)))
            channel = self.bot.get_channel(843395745741537310)
            await channel.send(embed=embed)
            print(str(exc))
            raise exc.original
def setup(bot):
    bot.add_cog(ErrorHandler(bot))
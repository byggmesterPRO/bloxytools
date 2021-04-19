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
    async def get_lang(self, ctx):
        try:
            lang = await self.bot.db.fetch("SELECT lang FROM guild_prefixes WHERE guild_id=$1", ctx.guild.id)
            lang = lang[0]['lang']
        except Exception as e:
            lang = 'en'
        if lang == None:
            lang = 'en'
        else:
            lang = lang
        return lang
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
            lang = await self.get_lang(ctx)
            embed = EmbedMaker.error_embed(ctx, "One or more required arguments is missing!", lang)
            await ctx.send(embed=embed)
        elif isinstance(exc, CommandOnCooldown):
            try:
                lang = await self.bot.db.fetch("SELECT lang FROM guild_prefixes WHERE guild_id=$1", ctx.guild.id)
                lang = lang[0]['lang']
            except Exception as e:
                lang = 'en'
            if lang == None:
                lang = 'en'
            else:
                lang = lang
            embed = EmbedMaker.cooldown_embed(ctx, lang)
            embed.add_field(name="Cooldown!", value=f"You may retry after {exc.retry_after:,.2f} seconds")
            await ctx.send(embed=embed)
        elif isinstance(exc, MissingPermissions):
            lang = await self.get_lang(ctx)
            embed = EmbedMaker.error_embed(ctx, "You are missing permissions!", lang)
            await ctx.send(embed=embed)
        elif isinstance(exc, KeyError):
            embed = EmbedMaker.error_embed(ctx, "That's not a username my guy")
            await ctx.send(embed=embed)
        else:
            lang = await self.get_lang(ctx)
            embed = EmbedMaker.error_embed(ctx, "Unkown error! Please screenshot this and send it in the support server!", lang)
            await ctx.send(embed=embed)
            raise exc.original
def setup(bot):
    bot.add_cog(ErrorHandler(bot))
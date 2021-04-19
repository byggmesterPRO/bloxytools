#Importing stuff
import discord
import asyncpg
import json
import asyncio
import datetime

from datetime import date
from discord.ext import commands
from lib.styling import EmbedMaker







#The Cog itself
class ModMail(commands.Cog):
    def __init__(self, bot):
        self.bot=bot        
    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        with open('lib/json/channels.json') as f:
            config = json.load(f)
        if await self.bot.db.fetch("SELECT discord_id FROM user_blacklist WHERE discord_id=$1;", message.author.id):
            return
        else:
            if not isinstance(message.channel, discord.DMChannel) or message.author.id == self.bot.user.id:
                # not a DM, or it's just the bot itself
                return
            channel = self.bot.get_channel(config["mail_channel"])
            if not channel:
                print("Mail channel not found! Reconfigure bot!")

            main_guild = self.bot.get_guild(config["server"])
            if not main_guild:
                print("Main Server ID is incorrect!  Reconfigure bot!")
                author = message.author
            else:
                author = main_guild.get_member(message.author.id)
                if not author:
                    author = message.author

            content = message.clean_content


            embed = EmbedMaker.modmail_embed(message, author, content)
 
            await channel.send(content=f"{message.author.id}", embed=embed)

            try:
                await message.add_reaction('📬')
            except discord.ext.commands.errors.CommandInvokeError:
                await message.channel.send('📬')

            self.last_user = author

        async def _shutdown(self):
            await self.bot.logout()
            await self.bot.close()
            self.bot.loop.stop()

    @commands.command()
    async def dm(self, ctx, user : discord.User, *, msg):
        with open("lib/json/channels.json", "r") as f:
            channel = json.load(f)
        if ctx.channel.id != channel["mail_channel"]:
            return
        with open("lib/json/modmail.json", "r") as f:
            replace = json.load(f)
        main_guild = self.bot.get_guild(channel["server"])
        if not main_guild:
            print("Main Server ID is incorrect!  Reconfigure bot!")
            return ctx.send('Main Server Unavailable')
        else:
            if ctx.message.author.id in replace['replacements']:
                author = main_guild.get_member(611912213778661409)
                if not author:
                    author = self.bot.user

                try:
                    await ctx.message.add_reaction('🕵️')
                except:
                    await ctx.send('🕵️')
            else:
                author = main_guild.get_member(ctx.message.author.id)
                if not author:
                    author = self.bot.user
        if ctx.author.id in replace["replacements"]:
            author2 = main_guild.get_member(611912213778661409)
        else:
            author2 = ctx
        embed = EmbedMaker.modmail_embed2(author2, author, msg)
        try:
            await user.send(embed=embed)
        except:
            await ctx.send("This user has blocked the bot or doesn't share a server.")
        else:
            try:
                await ctx.send("Message successfully sent!")
            except:
                await ctx.message.add_reaction('📬')

        self.last_user = user


    @commands.command()
    async def hideme(self, ctx):
        with open("lib/json/channels.json", "r") as f:
            channels = json.load(f)
        if ctx.channel.id != channels['mail_channel']:
            return
        with open("lib/json/modmail.json", "r") as f:
            modmail = json.load(f)
        if ctx.author.id in modmail["replacements"]:
            await ctx.send("You're already hidden! 🕵️")
            return
        modmail['replacements'] += [ctx.author.id]
        with open("lib/json/modmail.json", "w") as f:
            channels = json.dump(modmail, f)
        await ctx.send("You're now hidden! 🕵️")

    @commands.command()
    async def unhideme(self, ctx):
        with open("lib/json/channels.json", "r") as f:
            channels = json.load(f)
        if ctx.channel.id != channels['mail_channel']:
            return
        with open("lib/json/modmail.json", "r") as f:
            modmail = json.load(f)
        if ctx.author.id in modmail["replacements"]:
            index = modmail["replacements"].index(ctx.author.id)
            del modmail["replacements"][index]
            with open("lib/json/modmail.json", "w") as f:
                channels = json.dump(modmail, f)
            await ctx.send("You're now unhidden! 🙆")
        else:
            await ctx.send("You are not hidden! 😡")
            print(modmail["replacements"])
            return


    @commands.command()
    async def reply(self, ctx, *, msg):
        with open("lib/json/channels.json", "r") as f:
            config = json.load(f)
        if ctx.channel.id != config["mail_channel"]:
            return

        if self.last_user is None:
            await ctx.send("No user to reply to!")
            return
        await self.dm.callback(self, ctx, user=self.last_user, msg=msg)
    @commands.command()
    async def spam(self, ctx, user : discord.User, times : int, *, msg):
        with open("lib/json/channels.json", "r") as f:
            config = json.load(f)
        IF_DEV = await self.bot.db.fetch("SELECT discord_id FROM developers WHERE discord_id=$1", ctx.author.id)
        if IF_DEV:
            return
        with ctx.typing():
            for i in range(times):
                await user.send(msg)
                await asyncio.sleep(1.25)
            await ctx.message.add_reaction('📬')        

    @commands.command()
    async def blacklist(self, ctx, user : int, *, reason=None):
        developers = await self.bot.db.fetch("SELECT discord_id FROM developers WHERE discord_id=$1;", ctx.author.id)
        if developers:
            blacklist_check = await self.bot.db.fetch("SELECT discord_id FROM user_blacklist WHERE discord_id=$1;", user)
            if not blacklist_check:
                await self.bot.db.execute("INSERT INTO user_blacklist(discord_id, blacklist_at, blacklist_reason) VALUES ($1, $2, $3);", user, date.today(), reason)
                await ctx.send(f"User `{user}` has been blacklisted from Bloxy Tools Direct Messages.")
            else:
                await ctx.send("This user is already blacklisted!")
    @commands.command()
    async def unblacklist(self, ctx, user : int):
        developers = await self.bot.db.fetch("SELECT discord_id FROM developers WHERE discord_id=$1;", ctx.author.id)
        if developers:
            blacklist_check = await self.bot.db.fetch("SELECT discord_id FROM user_blacklist WHERE discord_id=$1;", user)
            if blacklist_check:
                await self.bot.db.execute("DELETE FROM user_blacklist WHERE discord_id=$1;", user)
                await ctx.send(f"User `{user}` has been unblacklisted")
            else:
                await ctx.send("Couldn't find a user with that ID!")

def setup(bot):
    bot.add_cog(ModMail(bot))
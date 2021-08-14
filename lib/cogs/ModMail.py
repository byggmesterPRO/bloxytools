
import discord
import json
import asyncio
from lib.Functions import CommandProcess as cp 

from datetime import date
from lib.styling import EmbedMaker
from discord.ext import commands
from discord.ext import commands
from asyncio import sleep

from discord.ext.commands.core import check

with open("lib/json/channels.json", "r") as f:
    channel = json.load(f)
main_guild = channel['server']
class Modmail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        if message.content.startswith("bt!") or message.content.startswith("!"):
            return
        ticketOpened = await self.bot.db.fetchrow("SELECT discord_id, channel_id FROM tickets WHERE channel_id=$1;", message.channel.id)
        if ticketOpened and not message.author.id == self.bot.user.id:
            embed = EmbedMaker.modmail_embed2(message, message.author, message.content)
            user =  self.bot.get_user(ticketOpened['discord_id'])
            await user.send(embed=embed)
            return
        if not isinstance(message.channel, discord.DMChannel) or message.author.id == self.bot.user.id:
            return
        elif isinstance(message.channel, discord.DMChannel):
            ticketOpened = await self.bot.db.fetchrow("SELECT discord_id, channel_id FROM tickets WHERE discord_id=$1;", message.author.id)
        blacklisted = await self.bot.db.fetchrow("SELECT discord_id FROM user_blacklist WHERE discord_id=$1;", message.author.id)
        if blacklisted:
            return
        guild = self.bot.get_guild(main_guild)
        ticket_category = guild.get_channel(channel['ticket_category'])
        if ticketOpened:
            ticket = guild.get_channel(ticketOpened['channel_id'])
            embed = EmbedMaker.modmail_embed(message,message.content, message.author)
            await ticket.send(embed=embed)
            return
        embed = EmbedMaker.default_embed(message, "You are about to open a support ticket!\nIf you don't need help click ❌, otherwise click ✅.")
        bot_message = await message.author.send(embed=embed)
        def check(reaction, user):
            return user == message.author and reaction.emoji in ['✅', '❌']
        await bot_message.add_reaction(emoji="❌")
        await bot_message.add_reaction(emoji="✅")
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            pass
        else:
            if str(reaction) == "✅":
                ticketOpened = await self.bot.db.fetchrow("SELECT discord_id, channel_id FROM tickets WHERE discord_id=$1;", message.author.id)
                if not ticketOpened:
                    ticket = await ticket_category.create_text_channel(message.author.name + "-" + message.author.discriminator)
                    await ticket.send(message.author.name + "#" + message.author.discriminator + " opened a ticket and said\n```" + message.content + "\n```")
                    await bot_message.delete()  
                    await message.author.send(embed=None, content="✅ Support ticket opened! You are now chatting with support!")
                    await self.bot.db.execute("INSERT INTO tickets(discord_id, channel_id) VALUES($1, $2);", message.author.id, ticket.id)

    @commands.command()
    async def close(self, ctx, argument=None):
        await cp.process_command(ctx)
        permission = await self.bot.db.fetchrow("SELECT rank FROM permissions WHERE discord_id=$1;", ctx.author.id)
        if permission['rank'] in [0,1]:
            argument = argument or ctx.channel.id
        else:
            argument = ctx.channel.id
        ticket = await self.bot.db.fetchrow("SELECT channel_id FROM tickets WHERE channel_id=$1", argument)
        if not ticket:
            return
        ticket = self.bot.get_channel(ticket['channel_id'])
        bot_message = await ctx.send("Are you sure you want to close this ticket?")
        await bot_message.add_reaction(emoji="❌")
        await bot_message.add_reaction(emoji="✅")
        def check(reaction, user):
            return user == ctx.author and reaction.emoji in ['✅', '❌']
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            pass
        else:
            if str(reaction) == "✅":
                await ctx.send("Closing in 5 seconds...")
                await self.bot.db.execute("DELETE FROM tickets WHERE channel_id=$1;", argument)
                await asyncio.sleep(5)
                await ticket.delete(reason="Closed ticket")
    @commands.command()
    async def blacklist(self, ctx, user_id, *, reason):
        await cp.process_command(ctx)
        permission = await self.bot.db.fetchrow("SELECT rank FROM permissions WHERE discord_id=$1;", ctx.author.id)
        if permission['rank'] in [0,1]:
            if user_id.lower() == "channel":
                user = await self.bot.db.fetchrow("SELECT discord_id, channel_id FROM tickets WHERE channel_id=$1;", ctx.channel.id)
                if user:
                    user_id = user['discord_id']
                else:
                    return
            await ctx.send("✅ Blacklisted "+str(user_id))
            await self.bot.db.execute("INSERT INTO user_blacklist(discord_id, blacklist_at, blacklist_reason) VALUES ($1,$2,$3);", user_id, date.today(), reason)
    @commands.command()
    async def unblacklist(self, ctx, user_id):
        await cp.process_command(ctx)
        permission = await self.bot.db.fetchrow("SELECT rank FROM permissions WHERE discord_id=$1;", ctx.author.id)
        if permission['rank'] in [0,1]:
            if user_id.lower() == "channel":
                user = await self.bot.db.fetchrow("SELECT discord_id, channel_id FROM tickets WHERE channel_id=$1;", ctx.channel.id)
                if user:
                    try:
                        user_id = user['discord_id']
                    except:
                        pass
            await ctx.send("✅ Un-blacklisted "+str(user_id))
            await self.bot.db.execute("DELETE FROM user_blacklist WHERE discord_id=$1;", int(user_id))

def setup(bot):
    bot.add_cog(Modmail(bot))
    
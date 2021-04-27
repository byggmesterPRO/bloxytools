import discord
import requests
import json
from discord.ext import commands
from flask import Flask, request, Response
from discord_webhook import DiscordWebhook, DiscordEmbed
from lib.Functions import CommandProcess as cp


class PointStore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1.0, 15.0, commands.BucketType.user)
    async def shop(ctx, *, msg):
        pass
        cp.process_command(ctx)


   

def setup(bot):
    bot.add_cog(PointStore(bot))

import discord
import requests
import json
from discord.ext import commands
from flask import Flask, request, Response
from discord_webhook import DiscordWebhook, DiscordEmbed

with open("lib/json/config.json", "r") as f:
    config = json.load(f)
DBL_TOKEN = config['dbl_token']

class PointStore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot




   

def setup(bot):
    bot.add_cog(PointStore(bot))

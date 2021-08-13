from typing import List
import discord
import json
import random
import datetime

from discord.ext import commands
from discord import Embed, Color

with open('lib/json/var.json', 'r') as f:
    var = json.load(f)


BLOXY_TITLE = var['title']
BUILD = var['build']
VERSION = var['version']
COLOR = 0xe85755
RARE_COOLDOWN_TITLES = var['rare_cooldown_titles']
COOLDOWN_TITLES = var['cooldown_titles']
SUPPORTSERVER = "https://discord.gg/W3b6jHPMCg"

def cooldown_title():
    RANDOM_NUMBER = random.randint(0, 100)
    if RANDOM_NUMBER == 2: #NoNameUltra the banana god chose this
        COOLDOWN_TITLE = random.choice(RARE_COOLDOWN_TITLES)
    else:
        COOLDOWN_TITLE = random.choice(COOLDOWN_TITLES)
    return COOLDOWN_TITLE


def handle_embed(ctx, embed):
    embed.set_author(name="{}#{}".format(ctx.author.name, ctx.author.discriminator), icon_url=ctx.author.avatar_url)
    embed.set_footer(text=f"{BUILD} Alpha System | {SUPPORTSERVER}", icon_url="https://i.imgur.com/UZAgLJ6.png")
    return embed


def default_embed(ctx, desc=None):
    embed = Embed(title=BLOXY_TITLE, timestamp=datetime.datetime.utcnow(), color=COLOR, description=desc)
    embed = handle_embed(ctx, embed)
    return embed

def error_embed(ctx, msg):
    embed = Embed(title="An error occured!", timestamp=datetime.datetime.utcnow(), color=Color.red())
    embed.add_field(name="Error", value=msg)
    embed.add_field(name="Solutions", value="-Try doing the command again \n-Wait longer and try again \n-Report it in the support server!")
    embed.add_field(name="Support", value=f"If you believe this was wrong please join our [support]({SUPPORTSERVER}) server and report it there!")
    embed = handle_embed(ctx, embed)
    return embed


def cooldown_embed(ctx, desc=None):
    embed = Embed(title=cooldown_title(), timestamp=datetime.datetime.utcnow(), color=Color.blue(), description=desc)
    embed = handle_embed(ctx, embed)
    return embed



def modmail_embed(message_object,message, author,):
    embed = Embed(title=BLOXY_TITLE, timestamp=datetime.datetime.utcnow(), color=COLOR)
    embed.set_author(name="{} ({}#{})".format(author.display_name, author.name, author.discriminator),
                    icon_url=author.avatar_url)
    embed.timestamp = message_object.created_at
    embed.set_footer(text='User ID: {}'.format(author.id))
    embed.color = COLOR

    embed.add_field(name="Message", value=message[:1000] or "blank")
    if len(message[1000:]) > 0:
        embed.add_field(name="(Continued)", value=message[1000:])
    return embed

def modmail_embed2(message_object, author, msg):
    if isinstance(author, commands.Context):
        embed = Embed(title=BLOXY_TITLE, description="", colour=author.color)

        embed.set_author(name="{} ({}#{})".format(author.display_name, author.name, author.discriminator),
                            icon_url=author.avatar_url)


        embed.timestamp = message_object.message.created_at

        embed.add_field(name="Message", value=msg[:1000] or "blank", inline=False)
        if len(msg) > 1000:
            embed.add_field(name="(Continued)", value=msg[1000:], inline=False)

        if message_object.attachments:
            embed.add_field(name="Attachments", value=", ".join([i.url for i in message_object.attachments]))

        embed.add_field(name="Sent from", value=f"**{author.display_name}** / {str(author.top_role)}")
    else:
        embed = Embed(title=BLOXY_TITLE, description="", colour=author.color)

        embed.set_author(name="{} ({}#{})".format(author.display_name, author.name, author.discriminator),
                            icon_url=author.avatar_url)


        embed.timestamp = message_object.created_at

        embed.add_field(name="Message", value=msg[:1000] or "blank", inline=False)
        if len(msg) > 1000:
            embed.add_field(name="(Continued)", value=msg[1000:], inline=False)

        if message_object.attachments:
            embed.add_field(name="Attachments", value=", ".join([i.url for i in message_object.attachments]))

        embed.add_field(name="Sent from", value=f"**{author.display_name}**")
    return embed

def pointStore_embed(ctx):
    with open('lib/json/store.json', 'r') as f:
        pointData = json.load(f)
    embed = default_embed(ctx, f"This is the store, this is where you may purchase roles and other perks that will come along with Bloxy Tools\n\nYou are able to claim these roles in the [support server!]({SUPPORTSERVER})")
    for i in pointData['store']:
        embed.add_field(name=pointData["store"][i]['title'], value=f"```\nPrice: {str(pointData['store'][i]['price'])} points.\nDescription: {pointData['store'][i]['description']}\nID: {pointData['store'][i]['id']}```", inline=False)
    return embed

def errorReport_embed(ctx, error):
    embed = Embed(title="An error occured!",description=error ,timestamp=datetime.datetime.utcnow(), color=Color.red())
    embed.add_field(name="User", value=ctx.author.mention)
    embed.add_field(name="Server", value=ctx.guild.name)
    embed = handle_embed(ctx, embed)
    return embed

#The data this embed receives = [roblox_id, roblox_name, roblox_displayName, roblox_description, created, days_ago, roblox_isBanned, roblox_friends, roblox_followings, roblox_followers]
def user_embed(ctx, data):
    if isinstance(data, list):
        roblox_id = data[0]
        username = data[1]
        displayName = data[2]
        description = data[3]
        created = data[4]
        days_ago = data[5]
        isBanned = data[6]
        friends = data[7]
        followings = data[8]
        followers = data[9]
        badges = data[10]
        profilePicture = data[11]
        if isBanned:
            isBanned = " | **User is banned from Roblox!**"
        else:
            isBanned = ""
        embed = default_embed(ctx, f"Display name **{displayName}**\nAccount Created at **{created}** | **{days_ago}** days ago" + isBanned)
        embed.add_field(name="Account name", value=f"[{username}](https://www.roblox.com/users/{roblox_id}/profile)", inline=True)
        embed.add_field(name="Description", value=description, inline=False)
        embed.add_field(name="Friends", value=friends, inline=True)
        embed.add_field(name="Followers", value=followers, inline=True)
        embed.add_field(name="Following", value=followings, inline=True)
        embed.add_field(name="Badges", value=badges)
        embed.set_thumbnail(url=profilePicture)
    else:
        embed = False
    return embed
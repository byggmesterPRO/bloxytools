import discord
import asyncio
import aiohttp
import time
import random

from lib.Functions import CommandProcess as cp
from datetime import datetime as dt, timedelta, date
from lib.styling import EmbedMaker
from discord.ext import commands


async def calculate_days(user_date):
    user_date = user_date.replace("T", " ").replace("Z", "").replace("-", "/")
    d1 = user_date
    d2 = date.today()
    d2 = str(d2).replace("-", "/")
    if len(d2) > 10:
        leni = int(len(d2)) - 10
        d2 = d2[:-leni]
        print (d2)
    if len(d1) > 10:
        leni = int(len(d1)) - 10
        d1 = d1[:-leni]
    calc1 = dt.strptime(d1, "%Y/%m/%d") 
    calc2 = dt.strptime(d2, "%Y/%m/%d")
    delta = calc2 - calc1
    return (d1, delta.days)


#Checking if there's an error, if there is it returns true as there is an error indeed. ;)
async def check_error(status):
    if status == 404:
        return True
    if status == 200:
        return False

#Fetching the roblox_id and username of a user based on their username or id.
async def fetch_id(value):
    async with aiohttp.ClientSession() as session:
        if value.startswith("id:"):
            value = value.replace("id:", "")
            async with session.get(f"https://users.roblox.com/v1/users/{value}") as resp:
                error = await check_error(resp.status)
                response = await resp.json()

            if not error:
                roblox_id = response['id']
                roblox_name = response['name']
                roblox_description = response['description']
                if not roblox_description:
                    roblox_description = "No description."
                roblox_created = response['created']
                roblox_isBanned = response['isBanned']
                roblox_displayName = response['displayName']
            else:
                return False

        else:
            async with session.get(f"https://api.roblox.com/users/get-by-username?username={value}") as resp:
                error = await check_error(resp.status)
                response = await resp.json()
            if not error:
                try:
                    roblox_id = response['Id']
                    roblox_name = response['Username']
                except:
                    return False
                else:
                    async with session.get(f"https://users.roblox.com/v1/users/{roblox_id}") as resp:
                        error = await check_error(resp.status)
                        response = await resp.json()
                        if not error:
                            roblox_description = response['description']
                            if not roblox_description:
                                roblox_description = "No description."

                            roblox_created = response ['created']
                            roblox_isBanned = response['isBanned']
                            roblox_displayName = response['displayName']
                        else:
                            return False
            else:
                return False
        return (roblox_id, roblox_name, roblox_description, roblox_created, roblox_isBanned, roblox_displayName)

async def fetch_userinfo(value):
    data = await fetch_id(value)
    if not data:
        return False
    roblox_id = data[0]
    async with aiohttp.ClientSession() as session:
        #Get their thumbnail and or profile picture.
        async with session.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={roblox_id}&size=420x420&format=Png&isCircular=false") as resp:
            error = await check_error(resp.status)
            response = await resp.json()
            if not error:
                profilePicture = response['data'][0]['imageUrl']
            else:
                profilePicture = "https://cdn.discordapp.com/attachments/843395793540218901/859724991197347880/ErrorRed.png"
        async with session.get(f"https://friends.roblox.com/v1/users/{roblox_id}/friends/count") as resp:
            error = await check_error(resp.status)
            response = await resp.json()
            if not error:
                roblox_friends = response['count']
            else:
                roblox_friends = "N/A"
        async with session.get(f"https://friends.roblox.com/v1/users/{roblox_id}/followers/count") as resp:
            error = await check_error(resp.status)
            response = await resp.json()
            if not error:
                roblox_followers = response['count']
            else:
                roblox_followers = "N/A"
        async with session.get(f"https://friends.roblox.com/v1/users/{roblox_id}/followings/count") as resp:
            error = await check_error(resp.status)
            response = await resp.json()
            if not error:
                roblox_followings = response['count']
            else:
                roblox_followings = "N/A"
        async with session.get(f"https://www.roblox.com/badges/roblox?userId={roblox_id}") as resp:
            error = await check_error(resp.status)
            response = await resp.json()
            if not error:
                if response:
                    badges = response['RobloxBadges']
                    badge_list = []
                    for name in badges:
                        badge = name['Name']
                        badge_list.append(badge)
                    badge_list = ", ".join(badge_list)
                    
                else:
                    badge_list = "This user has no badges"
            else:
                badge_list = "N/A"
    #Some variables are defined as themself, these are just to make a visible list of all the variables and data.
    profilePicture = profilePicture
    roblox_id = roblox_id #
    roblox_friends = roblox_friends
    roblox_followings = roblox_followings
    roblox_followers = roblox_followers
    badge_list = badge_list
    roblox_name = data[1] #
    roblox_displayName = data [5] #
    roblox_description = data[2]
    roblox_created = data[3]
    days = await calculate_days(roblox_created)
    days_ago = days[1]
    created = days[0]
    roblox_isBanned = data[4]
    return [roblox_id, roblox_name, roblox_displayName, roblox_description, created, days_ago, roblox_isBanned, roblox_friends, roblox_followings, roblox_followers, badge_list, profilePicture]
    
    

class RobloxCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(aliases=['u', 'profile'])
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def user(self, ctx, *, value):
        await cp.process_command(ctx)
        data = await fetch_userinfo(value)
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
            embed = EmbedMaker.default_embed(ctx, f"Display name **{displayName}**\nAccount Created at **{created}** | **{days_ago}** days ago" + isBanned)
            embed.add_field(name="Account name", value=f"[{username}](https://www.roblox.com/users/{roblox_id}/profile)", inline=True)
            embed.add_field(name="Description", value=description, inline=False)
            embed.add_field(name="Friends", value=friends, inline=True)
            embed.add_field(name="Followers", value=followers, inline=True)
            embed.add_field(name="Following", value=followings, inline=True)
            embed.add_field(name="Badges", value=badges)
            embed.set_thumbnail(url=profilePicture)
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Couldn't find that user!")
        
    @commands.command(aliases=['age', 'a'])
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def howold(self, ctx, *, value):
        await cp.process_command(ctx)
        data = await fetch_id(value)
        created = data[3]
        username = data[1]
        days = await calculate_days(created)
        days_ago = days[1]
        created = days[0]
        years = (days_ago/365)
        years = round(years, 2)
        embed = EmbedMaker.default_embed(ctx, f"The user {username} is {days_ago} days old.")
        embed.add_field(name="Created", value=created)
        embed.add_field(name="Account Age", value=f"This account is {years} years old")
        await ctx.send(embed=embed)
    
    @commands.command(aliases=['ru'])
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def randomuser(self, ctx):
        await self.user.callback(self, ctx, value=("id:" + str(random.randint(1,2040000000))))





def setup(bot):
    bot.add_cog(RobloxCommands(bot))

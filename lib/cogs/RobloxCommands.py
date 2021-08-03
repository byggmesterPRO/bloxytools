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


async def fetch_game(ctx, game):
    game.replace(" ", "%A0")
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://games.roblox.com/v1/games/list?model.keyword={game}&model.maxRows=5') as resp:
            error = await check_error(resp.status)
            response = await resp.json()
            if not error:
                embed = EmbedMaker.default_embed(ctx, "Type in chat the number of the game you want to display, *hurry you got 30 seconds*")
                results = ""
                for i in range(len(response['games'])):
                    UniverseID = response['games'][i]['universeId']
                    async with session.get(f'https://games.roblox.com/v1/games?universeIds={UniverseID}') as resp:
                        error = await check_error(resp.status)
                        response2 = await resp.json()
                    results += f"**{i+1}** - **{response['games'][i]['name']}**/ `Price - {response['games'][i]['price']}`\nCreator: `{response['games'][i]['creatorName']}`\n\n"
                embed.add_field(name="Results", value=results)
                return embed, response, response2
            else:
                return False
                    


#Fetching the roblox_id and username of a user based on their username or id.
async def fetch_id(value):
    value = value.replace(" ","%20")
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
                if profilePicture == None:
                    profilePicture = "https://cdn.discordapp.com/attachments/843395793540218901/859724991197347880/ErrorRed.png"
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
    @commands.command(aliases=['qid', 'id'])
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def quickid(self, ctx, *, username_or_id):
        await cp.process_command(ctx)
        result = ""
        message = await ctx.send("Fetching user ids...")
        users = username_or_id.replace(" ", "").split(",")
        if len(users) > 25:
            await message.edit(content="❌ That's too many users! Max is __25__!")
            return
        for i in range(len(users)):
            user = await fetch_id(users[i])
            if not user:
                result += f"**{i+1}.** ❌ Couldn't fetch **{users[i]}**\n\n"
            else:
                result += f"**{i+1}.** ✅ **{user[1]}** / ID: `{user[0]}` / DisplayName: {user[5]}**\n\n"
        await message.edit(content=result)
    @commands.command(aliases=['u', 'profile'])
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def user(self, ctx, *, username_or_id):
        await cp.process_command(ctx)
        data = await fetch_userinfo(username_or_id)
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
    async def howold(self, ctx, *, username_or_id):
        await cp.process_command(ctx)
        data = await fetch_id(username_or_id)
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
        await self.user.callback(self, ctx, username_or_id=("id:" + str(random.randint(1,2040000000))))
    
    @commands.command(aliases=['ga'])
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def game(self, ctx, *, game_name):
        await cp.process_command(ctx)
        game = await fetch_game(ctx, game_name)
        if not game:
            await ctx.send("Couldn't find this game!")
            return
        else:
            message = await ctx.send(embed=game[0])
            def check(m):
                try:
                    if ctx.channel == m.channel and m.author == ctx.author and isinstance(int(m.content), int) and m.content in ["1","2","3","4","5"]:
                        return True
                    else:
                        return False
                except:
                    return False
            try:
                response = await self.bot.wait_for('message', check=check, timeout=30)
            except asyncio.TimeoutError:
                await message.edit(embed=None, content="Used too long to answer!")
            else:
                async with aiohttp.ClientSession() as session:
                    response = int(response.content)-1
                    embed = EmbedMaker.default_embed(ctx)

                    async with session.get(f'https://thumbnails.roblox.com/v1/games/icons?universeIds={game[1]["games"][response]["universeId"]}&size=512x512&format=Png&isCircular=false') as resp:
                        thumbnail = await resp.json()
                    embed.set_thumbnail(url=thumbnail['data'][0]['imageUrl'])

                    async with session.get(f'https://thumbnails.roblox.com/v1/games/multiget/thumbnails?universeIds={game[1]["games"][response]["universeId"]}&size=768x432&format=Png&isCircular=false') as resp:
                        image = await resp.json()

                    embed.set_image(url=image['data'][0]['thumbnails'][0]['imageUrl'])
                    embed.add_field(name='Price', value=game[1]["games"][response]["price"], inline=False)
                    embed.add_field(name='Likes', value=game[1]["games"][response]["totalUpVotes"])
                    embed.add_field(name='Dislikes', value=game[1]["games"][response]["totalDownVotes"])
                    embed.add_field(name='Visits', value=game[2]['data'][0]['visits'])
                    embed.add_field(name='Playing', value=game[2]['data'][0]['playing'])
                    embed.add_field(name='Max Players', value=game[2]['data'][0]['maxPlayers'])

                    createdAt = game[2]['data'][0]['created'].split("T")[0]
                    embed.add_field(name='Created', value=dt.strptime(createdAt, '%Y-%m-%d').strftime("%b %d %Y"), inline=False)

                    updated = game[2]['data'][0]['updated'].split("T")[0]
                    embed.add_field(name='Last Updated', value=dt.strptime(updated, '%Y-%m-%d').strftime("%b %d %Y"), inline=False)

                    embed.add_field(name='Genre', value=game[2]['data'][0]['genre'], inline=False)
                await message.edit(embed=embed)

    @commands.group(aliases=['ch'])
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def check(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("❌ You need to choose a type! Possible types are `group, audio`!")
        await cp.process_command(ctx)
    
    @check.command()
    async def group(self, ctx, group_id, *, users):
        message = await ctx.send("Checking users...")
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://groups.roblox.com/v1/groups/{group_id}') as resp:
                error = await check_error(resp.status)
                group_data = await resp.json(encoding="utf-8-sig")
                if error:
                    await message.edit(content="❌ Couldn't find this group id.")
                    return
                else:
                    group_name = group_data['name']
            users = users.replace(" ", "").split(",")
            if len(users) > 15:
                await message.edit(content="❌ That's too many users!")
                return
            result = ""
            for i in range(len(users)):
                user = await fetch_id(users[i])
                if not user:
                    result += f"❌ Couldn't fetch **{users[i]}**\n\n"
                else:
                    async with session.get(f'https://groups.roblox.com/v2/users/{user[0]}/groups/roles') as resp:
                        error = await check_error(resp.status)
                        response = await resp.json()
                        if not error:
                            if_in_group = False
                            groups = response['data']
                            for j in range(len(groups)):
                                if str(groups[j]['group']['id']) == group_id:
                                    if_in_group = True
                            if if_in_group:
                                result += f"**{i+1}.** ✅ **{user[1]}** / ID: `{user[0]}` is in group **{group_name}**\n\n"
                            else:
                                result += f"**{i+1}.** ❌ **{user[1]}** / ID: `{user[0]}` is **NOT** in group **{group_name}**\n\n"
                        else:
                            result += f"**{i+1}.** ❌ Couldn't fetch **{users[i]}** / ID: `{user[0]}`\n\n"
            await message.edit(content=result)

    @check.command()
    async def audio(self, ctx, *, audio_ids):
        message = await ctx.send("Checking audio_ids...")
        audio_ids = audio_ids.lower().replace(" ", "").split(",")
        result = "Please remember that this is only checking if it exists, nothing more nothing less. *This is also experimental and might say it exists or doesn't even though it exists*\n\n"
        if len(audio_ids) > 25:
            await message.edit(content="❌ That's too many audio ids!")
            return
        async with aiohttp.ClientSession() as session:
            for i in range(len(audio_ids)):
                async with session.get(f"https://web.roblox.com/library/{i}/unknown?Category=Audio") as resp:
                    error = await check_error(resp.status)
                    if error:
                        result += (f"**{i+1}.** ❌ ID: {audio_ids[i]} Couldn't find this audio.\n\n")
                    else:
                        result += (f"**{i+1}.** ✅ ID: {audio_ids[i]} Found find this audio.\n\n")
        await message.edit(content=result)




#❌✅
def setup(bot):
    bot.add_cog(RobloxCommands(bot))

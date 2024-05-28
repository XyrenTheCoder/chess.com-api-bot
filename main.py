# Imports
import discord
import json
import os
import io
import berserk
import chessdotcom
import chess
import chess.svg
import stockfish
import platform
import re
import random
import string
import numpy as np
import urllib.request
import time
import aspose.words as aw

from datetime import datetime
from typing import Union
from discord import option, ApplicationContext
from discord.ext import commands
from discord.ext.pages import Paginator, Page
from matplotlib import pyplot as plt
from matplotlib import transforms
from distutils.dir_util import copy_tree, remove_tree
from stockfish import Stockfish


# Load databases
print("[client/startup] Populating databases...")
with open("db/chesscom_users.json", 'r') as f:
    cc_user = json.load(f)

with open("config/commands.json", 'r') as f:
    commands_db = json.load(f)

with open("config/auth.json", 'r', encoding="utf-8") as f:
    auth_config = json.load(f)


# Global variables
intents = discord.Intents.default()
intents.message_content = True
client = discord.Bot(intents=intents)
color = discord.Color.random()

cc = chessdotcom
cc.Client.request_config["headers"]["User-Agent"] = (
    "Discord bot by XyrenChess."
)
try:
    session = berserk.TokenSession(auth_config["API_TOKEN"])
    berserker = berserk.Client(session=session)
    commands_db["lcpuzzle"]["disabled"] = 'false'
    with open("config/commands.json", 'w+') as f:
        json.dump(commands_db, f, indent=4)
except:
    print("Error: You have not added a Lichess API token yet. Add one first in 'API_TOKEN' in 'config/auth.json'.")
    print("You can get an API token from https://lichess.org/account/oauth/token.")
    print('[client] Command /lcpuzzle has been disabled.')
    commands_db["lcpuzzle"]["disabled"] = 'true'
    with open("config/commands.json", 'w+') as f:
        json.dump(commands_db, f, indent=4)

flairs = [
    "<:diamond0:1229010811268239400>",
    "<:diamond1:1229012475022807191>",
    "<:diamond2:1229012509206380555>",
    "<:diamond3:1229012532308480100>",
    "<:diamond4:1229012556757074022>",
    "<:diamond5:1229012590945107989>",
    "<:diamond6:1229012630195273819>",
    "<:diamond7:1229012658175611012>",
    "<:diamond8:1229012680711475340>",
    "<:crown0:1229037903695581214>",
    "<:crown1:1229037989661904916>",
    "<:crown2:1229038014249046017>",
    "<:crown3:1229038034960384060>",
    "<:crown4:1229038084616753214>",
    "<:crown5:1229038105416306849>",
    "<:crown6:1229038131555336252>",
    "<:crown7:1229038174534111323>",
    "<:crown8:1229038204993409097>",
    "<:star0:1229041993402028043>",
    "<:star1:1229042017116618882>",
    "<:star2:1229042061030850652>",
    "<:star3:1229042083080306838>",
    "<:star4:1229042112922652722>",
    "<:star5:1229042137295749120>",
    "<:star6:1229042177129185341>",
    "<:star7:1229042203335069706>",
    "<:star8:1229042224113778800>",
    "<:blunder_emote:1229437688537419806>",
    "<:brilliant_emote:1229437692056567848>",
    "<:knight_fork:1229437621244133427>",
    "<:checkmate_king:1230085805201162262>",

    "<:wp:1229437684066553916>",
    "<:wn:1229437675660906547>",
    "<:wb:1229437672439808130>",
    "<:wr:1229437679263940772>",
    "<:wq:1229437668245639322>",
    "<:wk:1229437664491602001>",
    "<:bp:1229437681566613636>",
    "<:bn:1229437674121592894>",
    "<:bb:1229437670652907561>",
    "<:br:1229437677464453220>",
    "<:bq:1229437666022658242>",
    "<:bk:1229437662289727589>",
]


# Check for databases and autogenerate them
if not os.path.isdir("db"):
    os.mkdir("db")
    os.mkdir("db/cache")
    os.mkdir("db/game_archive")

if not os.path.isfile("db/chesscom_users.json"):
    with open("db/chesscom_users.json", 'x', encoding="utf-8") as f:
        json.dump({}, f)


# Pre-initialization
def save(data: str) -> int:
    with open("db/chesscom_users.json", 'w+') as f:
        json.dump(data, f, indent=4)
    return 0


if platform.system() == 'Windows':
    stockfish = Stockfish(path='./stockfish_15.1_win_x64_avx2/stockfish-windows-2022-x86-64-avx2.exe')
    commands_db["analyse"]["disabled"] = 'false'
    with open("config/commands.json", 'w+') as f:
        json.dump(commands_db, f, indent=4)

elif platform.system() == 'Linux':
    stockfish = Stockfish(path='./stockfish_15.1_linux_x64/stockfish-ubuntu-20.04-x86-64')
    commands_db["analyse"]["disabled"] = 'false'
    with open("config/commands.json", 'w+') as f:
        json.dump(commands_db, f, indent=4)

else:
    print('Error: Failed to start Stockfish as your OS not supported, please try to use another OS instead.') # mac bad
    print('[client] Command /analyse has been disabled.')
    commands_db["analyse"]["disabled"] = 'true'
    with open("config/commands.json", 'w+') as f:
        json.dump(commands_db, f, indent=4)


# Events
@client.event
async def on_ready():
    print(f"[client] Discord bot user logged in as {client.user.name}.")
    print("[client] Ready to accept commands.")
    print("-------------")

    botactivity = discord.Activity(type=discord.ActivityType.playing, name="Chess.com", state="10+0 Rapid", large_image="chess_com")
    await client.change_presence(activity=botactivity, status=discord.Status.streaming)


@client.event
async def on_message(message: discord.Message):
    if message.content == "!reload":
        if message.author.id == 706697300872921088:
            global cc_user, commands_db

            with open("db/chesscom_users.json", 'r', encoding="utf-8") as f:
                cc_user = json.load(f)

            with open("config/commands.json", 'r') as f:
                commands_db = json.load(f)

            print("[main/!reload] Reloaded database.")
            return cc_user, commands_db

        else:
            print(f"[main/!reload] User {message.author.name} ({message.author.id}) does not have permission to trigger !reload.")

    elif message.content == "!clearcache":
        if message.author.id == 706697300872921088:
            try:
                remove_tree("db/cache")
                os.mkdir("db/cache")

                print("[main/!clearcache] Cleared cache.")

            except:
                print("[main/!clearcache] Data is being used right now, please try again later.")

        else:
            print(f"[main/!clearcache] User {message.author.name} ({message.author.id}) does not have permission to trigger !clearcache.")

    elif message.content == "!wipe":
        if message.author.id == 706697300872921088:
            try:
                remove_tree("db")
                os.mkdir("db")
                os.mkdir("db/cache")
                os.mkdir("db/game_archive")

                print("[main/!wipe] Wiped all data.")

            except:
                print("[main/!wipe] Data is being used right now, please try again later.")

        else:
            print(f"[main/!wipe] User {message.author.name} ({message.author.id}) does not have permission to trigger !wipe.")

    elif message.content == "!backup":
        if message.author.id == 706697300872921088:
            copy_tree("db", f"backups/{time.time()}")

            print("[main/!backup] Created backup of database.")

        else:
            print(f"[main/!backup] User {message.author.name} ({message.author.id}) does not have permission to trigger !backup.")

    elif message.content == "!recover":
        if message.author.id == 706697300872921088:
            db = max(os.listdir("backups"))
            copy_tree(f"backups/{db}", "db")

            print(f"[main/!recover] Recovered from database backup at {db}.")

        else:
            print(f"[main/!recover] User {message.author.name} ({message.author.id}) does not have permission to trigger !recover.")

    elif message.content == "!wipearchive":
        if message.author.id == 706697300872921088:
            remove_tree("db/game_archive")
            os.mkdir("db/game_archive")

            print("[main/!wipearchive] Wiped game archive.")

        else:
            print(f"[main/!wipearchive] User {message.author.name} ({message.author.id}) does not have permission to trigger !wipearchive.")

    else:
        pass

# Slash commands
@client.slash_command(
    name="help",
    description="Need some help?"
)
@option(name="detailed", description="Detailed command list.", type=bool, choices=[True, False], default=False)
async def _help(ctx: ApplicationContext, detailed: bool):
    await ctx.defer(invisible=True)
    if detailed == True:
        parsed_desc = ""

        for command in commands_db:
            if commands_db[command]['disabled'] == 'false':
                parsed_desc += f"\n\n**{commands_db[command]['name']}**: {commands_db[command]['description']}\nFormat: /{command} {commands_db[command]['args']}"
            else:
                pass

        localembed = discord.Embed(
            title="My Commands",
            description=parsed_desc,
            color=discord.Color.random()
        )

        localembed.set_footer(text="`< >`: Required, else optional.")

    else:
        parsed = ', '.join(commands_db)

        localembed = discord.Embed(
            title="Commands overview",
            description=parsed,
            color=discord.Color.random()
        )

        localembed.set_footer(text="Use `/help detailed: True` for detailed command list.")

    await ctx.respond(embed=localembed)


@client.slash_command(
    name="ping",
    description="Get the bot's latency."
)
async def ping(ctx: ApplicationContext):
    await ctx.respond(f'Pong! My current latency is {round(client.latency * 1000)}ms.')


@client.slash_command(
    name="code",
    description="."
)
@option(name="code", description="Enter code.", type=str)
async def code(ctx: ApplicationContext, code: str):
    try:
        uname = cc_user[str(ctx.author.id)]["uname"]
        uinfo = cc.get_player_profile(uname).json

        if code == "IBRS92DVT":
            sflair = "<:stockfish_big:1230122081945915423>"
        elif code == "N5LVC5JC2":
            sflair = "<:gothamknights:1230122050228850811>"
        elif code == "7FWOX8STE":
            sflair = "<:ethereal:1230122168801562655>"
        elif code == "3PWQLLUSF":
            sflair = "<:komodo:1230122124547461140>"
        elif code == "3JJWF3A03":
            sflair = "<:komododragon:1230122147746287656>"
        elif code == "ICGM891PL":
            sflair = "<:torch:1230122102951120918>"
        else:
            localembed = discord.Embed(
                title=f"Failed!",
                description=f"Error: Code does not exist.",
                color=discord.Color.random()
            )

            return await ctx.respond(embed=localembed)

        if cc_user[str(ctx.author.id)]["flair"] == sflair:
            try:
                localembed = discord.Embed(
                    title=f"{uinfo['player']['name']} ({uname}) {cc_user[str(ctx.author.id)]['flair']}",
                    description="You have already claimed this hidden flair!",
                    color=discord.Color.random()
                )

            except:
                localembed = discord.Embed(
                    title=f"{uname} {cc_user[str(ctx.author.id)]['flair']}",
                    description="You have already claimed this hidden flair!",
                    color=discord.Color.random()
                )

        else:
            cc_user[str(ctx.author.id)]["flair"] = sflair
            save(cc_user)

            try:
                localembed = discord.Embed(
                    title="Wow, you found this hidden flair!",
                    description=f"Your flair has been set to {cc_user[str(ctx.author.id)]['flair']} !",
                    color=discord.Color.random()
                )
            except:
                localembed = discord.Embed(
                    title="Wow, you found this hidden flair!",
                    description=f"Your flair has been set to {cc_user[str(ctx.author.id)]['flair']} !",
                    color=discord.Color.random()
                )

    except:
        localembed = discord.Embed(
            title="You do not have a connected account.",
            description="If this is inaccurate, please report this bug to **xyrenchess**.",
            color=discord.Color.random()
        )

    await ctx.respond(embed=localembed)


@client.slash_command(
    name="connect",
    description="Connect to your Chess.com account."
)
@option(name="username", description="Your Chess.com username.", type=str)
async def connect(ctx: ApplicationContext, username: str):
    await ctx.defer(invisible=True)
    try:
        pf = cc.get_player_profile(username).json
        vcode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))
        ids = str(ctx.author.id)
        cc_user[ids] = {}
        cc_user[ids]["uname"] = username
        cc_user[ids]["verified"] = "No"
        cc_user[ids]["verification_code"] = vcode
        cc_user[ids]["premium"] = pf["player"]["status"]
        cc_user[ids]["flair"] = "None"
        save(cc_user)

        user = await client.fetch_user(ctx.author.id)
        localembed0 = discord.Embed(
            title=f"Connecting user `{username}` to **{ctx.author.name}**.",
            description=f"Your one-time verification code is ||`{vcode}`||. Do not give this information to anyone.",
            color=discord.Color.random()
        )

        await user.send(embed=localembed0)

        localembed = discord.Embed(
            title=f"User `{username}` is being connected to **{ctx.author.name}**.",
            description="",
            color=discord.Color.random()
        )
        localembed.add_field(
            name="Your one-time verification code has been sent to DM.",
            value="Please use `/verify verify` to verify your connected account."
        )
        localembed.set_footer(text="Do not know what to do? Use `/verify help` for the guide to verify your account.")

        await ctx.respond(embed=localembed)

    except cc.ChessDotComError:
        localembed = discord.Embed(
            title=f"User `{username}` does not exist.",
            description="If this is inaccurate, please report this bug to **xyrenchess**.",
            color=discord.Color.random()
        )

        await ctx.respond(embed=localembed)


@client.slash_command(
    name="verify",
    description="Verify your connected Chess.com account."
)
@option(name="action", description="What to do?", type=str, choices=["help", "verify", "newcode"])
async def verify(ctx: ApplicationContext, action: str):
    await ctx.defer(invisible=True)
    ids = str(ctx.author.id)

    if action == "help":
        localembed = discord.Embed(
            title="Verifying using one-time verification code provided when connecting Chess.com account.",
            description="To verify your Chess.com account, follow the instructions below.",
            color=discord.Color.random()
        )
        localembed.add_field(
            name="Step 1:",
            value="You need to use `/connect {Chess.com_username}`. The bot will send you a one-time verification code in your DM.\nCopy the one-time verification code that is only visible to you.",
            inline=False
        )
        localembed.set_image(url="https://cdn.discordapp.com/attachments/915526429293285466/1229369078171435058/Untitled991.png?ex=662f6e2c&is=661cf92c&hm=dfa5b45b4c38aa64104a0288f7b97ec05dbc77aa74f6791e3fcd8914c385aa6e&")

        localembed2 = discord.Embed(
            color=discord.Color.random()
        )
        localembed2.add_field(
            name="Step 2:",
            value="Open Chess.com and login, and go to settings of your account.",
            inline=False
        )
        localembed2.set_image(url="https://cdn.discordapp.com/attachments/915526429293285466/1228938134511812618/Untitled984.png?ex=662ddcd3&is=661b67d3&hm=e298c9ce5081c374b33d8b4f4de638914648ec034b3474cf515d6a611acee0d2&")

        localembed3 = discord.Embed(
            color=discord.Color.random()
        )
        localembed3.add_field(
            name="Step 3:",
            value="Paste the verification code into the `Location` field and save the settings.",
            inline=False
        )
        localembed3.set_image(url="https://cdn.discordapp.com/attachments/915526429293285466/1228938135359197277/Untitled985.png?ex=662ddcd4&is=661b67d4&hm=84f3c856300bd143d0e67d692ff5c4626f53b438e7a71b503a8714ac13112284&")

        localembed4 = discord.Embed(
            color=discord.Color.random()
        )
        localembed4.add_field(
            name="Step 4:",
            value="Use `/verify verify` to finish the verifying procedure. You may remove the code in your `Location` field after verifying your account.",
            inline=False
        )
        localembed4.add_field(
            name="What to do if I lost the verification code?",
            value="Use `/verify newcode` to generate a new one-time verification code. You may use the new code to verify your account.",
            inline=False
        )
        localembed4.set_image(url="https://cdn.discordapp.com/attachments/915526429293285466/1229369994542972978/image.png?ex=662f6f07&is=661cfa07&hm=829cfd77d7f7dcb313d74d1743148513d970326c1e356a0b0fedd6b988388deb&")

        localembed5 = discord.Embed(
            title="Extra!",
            description="Verified or not verified?",
            color=discord.Color.random()
        )
        localembed5.add_field(
            name="How do I know if a user is verified with their Chess.com account?",
            value="Verified users has a \"verified\" badge (<:verified:1228974564630069380>) next to their username, while unverified users has a \"unverified\" badge (<:unverified:1228975990932508692>) visible in their profile.",
            inline=False
        )
        localembed5.set_image(url="https://cdn.discordapp.com/attachments/915526429293285466/1229378408266338364/Untitled995.png?ex=662f76dd&is=661d01dd&hm=129cc20e5daf4b46ce28787e0dc07b066c6011f3c6cd42e480e92b48c81d9379&")

        pages = [
            Page(embeds=[localembed]),
            Page(embeds=[localembed2]),
            Page(embeds=[localembed3]),
            Page(embeds=[localembed4]),
            Page(embeds=[localembed5])
        ]
        paginator = Paginator(pages=pages)

        await paginator.respond(ctx.interaction, ephemeral=True)

    elif action == "verify":
        try:
            un = cc_user[ids]["uname"]
            verified = cc_user[ids]["verified"]
            vc = cc_user[ids]["verification_code"]
            pf = cc.get_player_profile(un).json

            if verified == "No":
                try:
                    if pf["player"]["location"] == vc:
                        cc_user[ids]["verified"] = "Yes"
                        cc_user[ids]["verification_code"] = "**Expired**"
                        save(cc_user)

                        localembed = discord.Embed(
                            title=f"Account `{un}` has been verified successfully!",
                            description="You may now remove the verification code from your Chess.com profile.",
                            color=discord.Color.random()
                        )

                    else:
                        cc_user[ids]["verification_code"] = "**Expired**"
                        save(cc_user)

                        localembed = discord.Embed(
                            title="Verification failed!",
                            description="Error: Verification code mismatched.",
                            color=discord.Color.random()
                        )
                        localembed.add_field(name="How do I fix this?", value="You should get a new one-time verification code with `/verify newcode` and try again.")
                        localembed.set_footer(text="Old verification code expired!")

                except discord.errors.ApplicationCommandInvokeError:
                    cc_user[ids]["verification_code"] = "**Expired**"
                    save(cc_user)

                    localembed = discord.Embed(
                        title="Verification failed!",
                        description="Error: No verification code detected.",
                        color=discord.Color.random()
                    )
                    localembed.add_field(name="How do I fix this?", value="You should get a new one-time verification code with `/verify newcode` and try again.")
                    localembed.set_footer(text="Old verification code expired!")

            else:
                localembed = discord.Embed(
                    title=f"Account `{un}` is already verified.",
                    description="You do not need to verify twice.",
                    color=discord.Color.random()
                )

        except:
            localembed = discord.Embed(
                title="You do not have a connected account.",
                description="If this is inaccurate, please report this bug to **xyrenchess**.",
                color=discord.Color.random()
            )

    elif action == "newcode":
        try:
            verified = cc_user[ids]["verified"]

            if verified == "No":
                username = cc_user[ids]["uname"]
                pf = cc.get_player_profile(username).json
                vcode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))
                cc_user[ids]["verification_code"] = vcode

                save(cc_user)

                user = await client.fetch_user(ctx.author.id)
                localembed0 = discord.Embed(
                    title="Requested new verification code.",
                    description=f"Your new one-time verification code is ||`{vcode}`||. Do not give this information to anyone.",
                    color=discord.Color.random()
                )

                await user.send(embed=localembed0)

                localembed = discord.Embed(
                    title="Requested new verification code.",
                    color=discord.Color.random()
                )
                localembed.add_field(
                    name="Your new one-time verification code has been sent to DM!",
                    value="Please check your DM list."
                )

                await ctx.respond(embed=localembed)

            else:
                localembed = discord.Embed(
                    title=f"Account `{un}` is already verified.",
                    description="You do not need a new verification code.",
                    color=discord.Color.random()
                )

        except:
            localembed = discord.Embed(
                title="You do not have a connected account.",
                description="If this is inaccurate, please report this bug to **xyrenchess**.",
                color=discord.Color.random()
            )

    await ctx.respond(embed=localembed)


@client.slash_command(
    name="viewprofile",
    description="View the profile of a Chess.com user."
)
@option(name="user", description="Specify a user.", type=str)
@option(name="format", description="Specify a format.", type=str, choices=["daily", "rapid", "blitz", "bullet"], default=None)
async def viewprofile(ctx: ApplicationContext, user: str, format: str):
    await ctx.defer(invisible=True)
    try:
        uinfo = cc.get_player_profile(user).json
        ustats = cc.get_player_stats(user).json
    except:
        localembed = discord.Embed(
            title="User does not exist.",
            description="",
            color=discord.Color.random()
        )

        return await ctx.respond(embed=localembed)

    uname = uinfo["player"]["username"]
    since = uinfo["player"]["joined"]
    lastonline = uinfo["player"]["last_online"]
    followers = uinfo["player"]["followers"]
    uid = uinfo["player"]["player_id"]

    try:
        av = uinfo["player"]["avatar"]
    except:
        av = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQTlCxyf01tNZOzuEuqFgstHMj2EMz8uOjJtrC159vgmg&s"

    try:
        dailyelo = ustats["stats"]["chess_daily"]["last"]["rating"]
        dailybest = ustats["stats"]["chess_daily"]["best"]["rating"]
    except:
        dailyelo = "*No record*"
        dailybest = 0

    try:
        rapidelo = ustats["stats"]["chess_rapid"]["last"]["rating"]
        rapidbest = ustats["stats"]["chess_rapid"]["best"]["rating"]
    except:
        rapidelo = "*No record*"
        rapidbest = 0

    try:
        blitzelo = ustats["stats"]["chess_blitz"]["last"]["rating"]
        blitzbest = ustats["stats"]["chess_blitz"]["best"]["rating"]
    except:
        blitzelo = "*No record*"
        blitzbest = 0

    try:
        bulletelo = ustats["stats"]["chess_bullet"]["last"]["rating"]
        bulletbest = ustats["stats"]["chess_bullet"]["best"]["rating"]
    except:
        bulletelo = "*No record*"
        bulletbest = 0

    try:
        puzzlepeak = ustats["stats"]["tactics"]["highest"]["rating"]
    except:
        puzzlepeak = "*No record*"

    try:
        puzzlerush = ustats["stats"]["puzzle_rush"]["best"]["score"]
    except:
        puzzlerush = "*No record*"

    if format == None:
        try:
            localembed = discord.Embed(
                title=f"{uinfo['player']['name']} ({uname})",
                description=f"Member since <t:{since}> | Last online: <t:{lastonline}>",
                color=discord.Color.random()
            )

        except:
            localembed = discord.Embed(
                title=f"{uname}",
                description=f"Member since <t:{since}> | Last online: <t:{lastonline}>",
                color=discord.Color.random()
            )

        localembed.set_thumbnail(url=av)
        localembed.add_field(
            name="<:followers:1228979708197081179> Followers:",
            value=followers
        )
        localembed.add_field(
            name="<:daily:1132115979124617297> Daily:",
            value=f"{dailyelo} ({dailybest} peak)"
        )
        localembed.add_field(
            name="<:rapid:1132112926090743940> Rapid:",
            value=f"{rapidelo} ({rapidbest} peak)"
        )
        localembed.add_field(
            name="<:blitz:1132113580788031618> Blitz:",
            value=f"{blitzelo} ({blitzbest} peak)"
        )
        localembed.add_field(
            name="<:bullet:1132114505262956606> Bullet:",
            value=f"{bulletelo} ({bulletbest} peak)"
        )
        localembed.add_field(
            name="<:puzzle:1228978258608132237> Puzzle peak rating:",
            value=f"{puzzlepeak}"
        )
        localembed.add_field(
            name="<:puzzlerush:1228972358920962188> Puzzle rush best attempt:",
            value=f"{puzzlerush}"
        )

        await ctx.respond(embed=localembed)

    else:
        try:
            localembed = discord.Embed(
                title=f"{uinfo['player']['name']} ({uname})",
                description=f"{format.upper()} stats",
                color=discord.Color.random()
            )

        except:
            localembed = discord.Embed(
                title=f"{uname}",
                description=f"{format.upper()} stats",
                color=discord.Color.random()
            )

        localembed.set_thumbnail(url=av)

        try:
            w = ustats['stats'][f'chess_{format}']['record']['win']
            d = ustats['stats'][f'chess_{format}']['record']['draw']
            l = ustats['stats'][f'chess_{format}']['record']['loss']
            total = w + d + l

            if format == "daily":
                localembed.add_field(
                    name="<:daily:1132115979124617297> Daily:",
                    value=f"Last game played at: <t:{ustats['stats']['chess_daily']['last']['date']}>",
                    inline=False
                )
                globals()[format+'elo'] = dailyelo
                globals()[format+'best'] = dailybest

            elif format == "rapid":
                localembed.add_field(
                    name="<:rapid:1132112926090743940> Rapid:",
                    value=f"Last game played at: <t:{ustats['stats']['chess_rapid']['last']['date']}>",
                    inline=False
                )
                globals()[format+'elo'] = rapidelo
                globals()[format+'best'] = rapidbest

            elif format == "blitz":
                localembed.add_field(
                    name="<:blitz:1132113580788031618> Blitz:",
                    value=f"Last game played at: <t:{ustats['stats']['chess_blitz']['last']['date']}>",
                    inline=False
                )
                globals()[format+'elo'] = blitzelo
                globals()[format+'best'] = blitzbest

            elif format == "bullet":
                localembed.add_field(
                    name="<:bullet:1132114505262956606> Bullet:",
                    value=f"Last game played at: <t:{ustats['stats']['chess_bullet']['last']['date']}>",
                    inline=False
                )
                globals()[format+'elo'] = bulletelo
                globals()[format+'best'] = bulletbest

        except:
            localembed.add_field(
                name=f"This user has not played any {format} games.",
                value=""
            )

            return await ctx.respond(embed=localembed)

        localembed.add_field(
            name="Rating:",
            value=f"{globals()[format+'elo']} ({globals()[format+'best']} peak)"
        )
        localembed.add_field(
            name="W/D/L (games):",
            value=f"{w}/{d}/{l} ({total} games played)",
            inline=False
        )
        localembed.add_field(
            name="Rates:",
            value=f"{round(w / total * 100, 2)}% **Win**, {round(d / total * 100, 2)}% **Draw**, {round(l / total * 100, 2)}% **Loss**",
            inline=False
        )

        data_stream = io.BytesIO()
        label = ['']

        fig = plt.figure(figsize=(10, 1))
        rot = transforms.Affine2D().rotate_deg(-90)

        plt.barh(label, w, 0.1, label='Win', color='green')
        plt.barh(label, d, 0.1, left=w, label='Draw', color='grey')
        plt.barh(label, l, 0.1, left=np.add(w,d), label='Loss', color='red')
        plt.title('Win/Draw/Loss record:', fontsize=15)

        plt.savefig(data_stream, format='png', bbox_inches="tight", dpi = 80)
        plt.close()

        data_stream.seek(0)
        chart = discord.File(data_stream,filename="wdl.png")

        localembed.set_image(url="attachment://wdl.png")
        localembed.set_footer(text=f"User id: {uid}")

        await ctx.respond(embed=localembed, file=chart)


@client.slash_command(
    name="profile",
    description="View the profile of a user."
)
@option(name="user", description="Specify a user.", type=discord.User, default=None)
@option(name="format", description="Specify a format.", type=str, choices=["daily", "rapid", "blitz", "bullet"], default=None)
async def profile(ctx: ApplicationContext, user: discord.User, format: str):
    await ctx.defer(invisible=True)
    if user == None:
        user = str(ctx.author.id)
    else:
        user = str(user.id)

    try:
        member = cc_user[user]["uname"]
        uinfo = cc.get_player_profile(member).json
        ustats = cc.get_player_stats(member).json

    except:
        localembed = discord.Embed(
            title="You do not have a connected account.",
            description="If this is inaccurate, please report this bug to **xyrenchess**.",
            color=discord.Color.random()
        )

        return await ctx.respond(embed=localembed)

    # status = uinfo["player"]["status"]
    uname = uinfo["player"]["username"]
    since = uinfo["player"]["joined"]
    lastonline = uinfo["player"]["last_online"]
    followers = uinfo["player"]["followers"]
    uid = uinfo["player"]["player_id"]

    try:
        av = uinfo["player"]["avatar"]
    except:
        av = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQTlCxyf01tNZOzuEuqFgstHMj2EMz8uOjJtrC159vgmg&s"

    try:
        dailyelo = ustats["stats"]["chess_daily"]["last"]["rating"]
        dailybest = ustats["stats"]["chess_daily"]["best"]["rating"]
    except:
        dailyelo = "*No record*"
        dailybest = 0

    try:
        rapidelo = ustats["stats"]["chess_rapid"]["last"]["rating"]
        rapidbest = ustats["stats"]["chess_rapid"]["best"]["rating"]
    except:
        rapidelo = "*No record*"
        rapidbest = 0

    try:
        blitzelo = ustats["stats"]["chess_blitz"]["last"]["rating"]
        blitzbest = ustats["stats"]["chess_blitz"]["best"]["rating"]
    except:
        blitzelo = "*No record*"
        blitzbest = 0

    try:
        bulletelo = ustats["stats"]["chess_bullet"]["last"]["rating"]
        bulletbest = ustats["stats"]["chess_bullet"]["best"]["rating"]
    except:
        bulletelo = "*No record*"
        bulletbest = 0

    try:
        puzzlepeak = ustats["stats"]["tactics"]["highest"]["rating"]
    except:
        puzzlepeak = "*No record*"

    try:
        puzzlerush = ustats["stats"]["puzzle_rush"]["best"]["score"]
    except:
        puzzlerush = "*No record*"

    if format == None:
        if cc_user[user]["flair"] == "None":
            flair = "<:placeholder:1229006396150779904>"
        else:
            flair = cc_user[user]["flair"]

        try:
            if cc_user[user]["verified"] == "Yes":
                localembed = discord.Embed(
                    title=f"{uinfo['player']['name']} ({uname}) <:verified:1228974564630069380> {flair}",
                    description=f"Member since <t:{since}> | Last online: <t:{lastonline}>",
                    color=discord.Color.random()
                )

            else:
                localembed = discord.Embed(
                    title=f"{uinfo['player']['name']} ({uname}) <:unverified:1228975990932508692> {flair}",
                    description=f"Member since <t:{since}> | Last online: <t:{lastonline}>",
                    color=discord.Color.random()
                )

        except:
            if cc_user[user]["verified"] == "Yes":
                localembed = discord.Embed(
                    title=f"{uname} <:verified:1228974564630069380> {flair}",
                    description=f"Member since <t:{since}> | Last online: <t:{lastonline}>",
                    color=discord.Color.random()
                )

            else:
                localembed = discord.Embed(
                    title=f"{uname} <:unverified:1228975990932508692> {flair}",
                    description=f"Member since <t:{since}> | Last online: <t:{lastonline}>",
                    color=discord.Color.random()
                )

        localembed.set_thumbnail(url=av)

        localembed.add_field(
            name="<:followers:1228979708197081179> Followers:",
            value=followers
        )
        localembed.add_field(
            name="<:daily:1132115979124617297> Daily:",
            value=f"{dailyelo} ({dailybest} peak)"
        )
        localembed.add_field(
            name="<:rapid:1132112926090743940> Rapid:",
            value=f"{rapidelo} ({rapidbest} peak)"
        )
        localembed.add_field(
            name="<:blitz:1132113580788031618> Blitz:",
            value=f"{blitzelo} ({blitzbest} peak)"
        )
        localembed.add_field(
            name="<:bullet:1132114505262956606> Bullet:",
            value=f"{bulletelo} ({bulletbest} peak)"
        )
        localembed.add_field(
            name="<:puzzle:1228978258608132237> Puzzle peak rating:",
            value=f"{puzzlepeak}"
        )
        localembed.add_field(
            name="<:puzzlerush:1228972358920962188> Puzzle rush best attempt:",
            value=f"{puzzlerush}"
        )

        await ctx.respond(embed=localembed)

    else:
        if cc_user[user]["flair"] == "None":
            flair = "<:placeholder:1229006396150779904>"
        else:
            flair = cc_user[user]["flair"]

        try:
            if cc_user[user]["verified"] == "Yes":
                localembed = discord.Embed(
                    title=f"{uinfo['player']['name']} ({uname}) <:verified:1228974564630069380> {flair}",
                    description=f"{format.upper()} stats",
                    color=discord.Color.random()
                )

            else:
                localembed = discord.Embed(
                    title=f"{uinfo['player']['name']} ({uname}) <:unverified:1228975990932508692> {flair}",
                    description=f"{format.upper()} stats",
                    color=discord.Color.random()
                )

        except:
            if cc_user[user]["verified"] == "Yes":
                localembed = discord.Embed(
                    title=f"{uname} <:verified:1228974564630069380> {flair}",
                    description=f"{format.upper()} stats",
                    color=discord.Color.random()
                )

            else:
                localembed = discord.Embed(
                    title=f"{uname} <:unverified:1228975990932508692> {flair}",
                    description=f"{format.upper()} stats",
                    color=discord.Color.random()
                )

        localembed.set_thumbnail(url=av)

        try:
            w = ustats['stats'][f'chess_{format}']['record']['win']
            d = ustats['stats'][f'chess_{format}']['record']['draw']
            l = ustats['stats'][f'chess_{format}']['record']['loss']
            total = w + d + l

            if format == "daily":
                localembed.add_field(
                    name="<:daily:1132115979124617297> Daily:",
                    value=f"Last game played at: <t:{ustats['stats']['chess_daily']['last']['date']}>",
                    inline=False
                )
                globals()[format+'elo'] = dailyelo
                globals()[format+'best'] = dailybest

            elif format == "rapid":
                localembed.add_field(
                    name="<:rapid:1132112926090743940> Rapid:",
                    value=f"Last game played at: <t:{ustats['stats']['chess_rapid']['last']['date']}>",
                    inline=False
                )
                globals()[format+'elo'] = rapidelo
                globals()[format+'best'] = rapidbest

            elif format == "blitz":
                localembed.add_field(
                    name="<:blitz:1132113580788031618> Blitz:",
                    value=f"Last game played at: <t:{ustats['stats']['chess_blitz']['last']['date']}>",
                    inline=False
                )
                globals()[format+'elo'] = blitzelo
                globals()[format+'best'] = blitzbest

            elif format == "bullet":
                localembed.add_field(
                    name="<:bullet:1132114505262956606> Bullet:",
                    value=f"Last game played at: <t:{ustats['stats']['chess_bullet']['last']['date']}>",
                    inline=False
                )
                globals()[format+'elo'] = bulletelo
                globals()[format+'best'] = bulletbest

        except:
            localembed.add_field(
                name=f"This user has not played any {format} games.",
                value=""
            )

            return await ctx.respond(embed=localembed)

        localembed.add_field(
            name="Rating:",
            value=f"{globals()[format+'elo']} ({globals()[format+'best']} peak)"
        )
        localembed.add_field(
            name="W/D/L (games):",
            value=f"{w}/{d}/{l} ({total} games played)",
            inline=False
        )
        localembed.add_field(
            name="Rates:",
            value=f"{round(w / total * 100, 2)}% **Win**, {round(d / total * 100, 2)}% **Draw**, {round(l / total * 100, 2)}% **Loss**",
            inline=False
        )

        data_stream = io.BytesIO()
        label = ['']

        fig = plt.figure(figsize=(10, 1))
        rot = transforms.Affine2D().rotate_deg(-90)

        plt.barh(label, w, 0.1, label='Win', color='green')
        plt.barh(label, d, 0.1, left=w, label='Draw', color='grey')
        plt.barh(label, l, 0.1, left=np.add(w,d), label='Loss', color='red')
        plt.title('Win/Draw/Loss record:', fontsize=15)

        plt.savefig(data_stream, format='png', bbox_inches="tight", dpi = 80)
        plt.close()

        data_stream.seek(0)
        chart = discord.File(data_stream, filename="wdl.png")

        localembed.set_image(url="attachment://wdl.png")
        localembed.set_footer(text=f"User id: {uid}")

        await ctx.respond(embed=localembed, file=chart)


@client.slash_command(
    name="flairlist",
    description="Get the list of flairs available."
)
async def flairlist(ctx: ApplicationContext):
    await ctx.defer(invisible=True)
    localembed1 = discord.Embed(
        title="Premium flairs: Page 1",
        description="List of flairs that can be set by premium Chess.com users.",
        color=discord.Color.random()
    )
    localembed2 = discord.Embed(
        title="Premium flairs: Page 2",
        description="List of flairs that can be set by premium Chess.com users.",
        color=discord.Color.random()
    )

    localb1 = discord.Embed(
        title="Basic flairs: Page 1",
        description="List of flairs that can be set by both basic and premium Chess.com users.",
        color=discord.Color.random()
    )

    for i in range(0, 25):
        localembed1.add_field(name=flairs[i], value=f"(ID: {i})")

    for i in range(25, 31):
        localembed2.add_field(name=flairs[i], value=f"(ID: {i})")

    for i in range(31, 43):
        localb1.add_field(name=flairs[i], value=f"(ID: {i})")

    localembed1.set_footer(text="Use `/setpremiumflair {flair_id}` to display your favourite flair on profile!")
    localembed2.set_footer(text="Use `/setpremiumflair {flair_id}` to display your favourite flair on profile!")
    localb1.set_footer(text="Use `/setbasicflair {flair_id}` to display your favourite flair on profile!")

    pages = [
        Page(embeds=[localembed1]),
        Page(embeds=[localembed2]),
        Page(embeds=[localb1]),
    ]
    paginator = Paginator(pages=pages)

    await paginator.respond(ctx.interaction)


@client.slash_command(
    name="setflair",
    description="Display a flair on profile."
)
@option(name="flair_id", description="ID of the flair.", type=int, default=None)
async def setflair(ctx: ApplicationContext, flair_id: int = None):
    await ctx.defer(invisible=True)
    try:
        uname = cc_user[str(ctx.author.id)]["uname"]
        uinfo = cc.get_player_profile(uname).json

        if flair_id == None:
            if cc_user[str(ctx.author.id)]["flair"] == "<:placeholder:1229006396150779904>":
                try:
                    localembed = discord.Embed(
                        title=f"{uinfo['player']['name']} ({uname}) {cc_user[str(ctx.author.id)]['flair']}",
                        description="You do not have a flair to remove lmao.",
                        color=discord.Color.random()
                    )

                except:
                    localembed = discord.Embed(
                        title=f"{uname} {cc_user[str(ctx.author.id)]['flair']}",
                        description="You do not have a flair to remove lmao.",
                        color=discord.Color.random()
                    )

            else:
                cc_user[str(ctx.author.id)]["flair"] = "<:placeholder:1229006396150779904>"
                save(cc_user)

                try:
                    localembed = discord.Embed(
                        title=f"{uinfo['player']['name']} ({uname}) {cc_user[str(ctx.author.id)]['flair']}",
                        description="Your flair has been removed!",
                        color=discord.Color.random()
                    )

                except:
                    localembed = discord.Embed(
                        title=f"{uname} {cc_user[str(ctx.author.id)]['flair']}",
                        description="Your flair has been removed!",
                        color=discord.Color.random()
                    )

        else:
            if cc_user[str(ctx.author.id)]["flair"] == flairs[flair_id]:
                try:
                    localembed = discord.Embed(
                        title=f"{uinfo['player']['name']} ({uname}) {cc_user[str(ctx.author.id)]['flair']}",
                        description="Interesting, you are trying to display the same flair that you are currently displaying.",
                        color=discord.Color.random()
                    )

                except:
                    localembed = discord.Embed(
                        title=f"{uname} {cc_user[str(ctx.author.id)]['flair']}",
                        description="Interesting, you are trying to display the same flair that you are currently displaying.",
                        color=discord.Color.random()
                    )

            else:
                if flair_id < 31: # premium flairs
                    if cc_user[str(ctx.author.id)]["premium"] == "basic":
                        localembed = discord.Embed(
                            title="Oops! You do not have Chess.com premium to use premium flairs!",
                            description="You can still display basic flairs.",
                            color=discord.Color.random()
                        )
                        localembed.set_footer(text="Not advertising Chess.com premium though.")

                    else:
                        cc_user[str(ctx.author.id)]["flair"] = flairs[int(flair_id)]
                        save(cc_user)

                        try:
                            localembed = discord.Embed(
                                title=f"{uinfo['player']['name']} ({uname}) {cc_user[str(ctx.author.id)]['flair']}",
                                description=f"Your flair has been set to {cc_user[str(ctx.author.id)]['flair']} !",
                                color=discord.Color.random()
                            )

                        except:
                            localembed = discord.Embed(
                                title=f"{uname} {cc_user[str(ctx.author.id)]['flair']}",
                                description=f"Your flair has been set to {cc_user[str(ctx.author.id)]['flair']} !",
                                color=discord.Color.random()
                            )

                else: # basic flairs that can be set by anyone
                    cc_user[str(ctx.author.id)]["flair"] = flairs[int(flair_id)]
                    save(cc_user)

                    try:
                        localembed = discord.Embed(
                            title=f"{uinfo['player']['name']} ({uname}) {cc_user[str(ctx.author.id)]['flair']}",
                            description=f"Your flair has been set to {cc_user[str(ctx.author.id)]['flair']} !",
                            color=discord.Color.random()
                        )

                    except:
                        localembed = discord.Embed(
                            title=f"{uname} {cc_user[str(ctx.author.id)]['flair']}",
                            description=f"Your flair has been set to {cc_user[str(ctx.author.id)]['flair']} !",
                            color=discord.Color.random()
                        )

    except cc.ChessDotComError:
        localembed = discord.Embed(
            title="You do not have a connected account.",
            description="If this is inaccurate, please report this bug to **xyrenchess**.",
            color=discord.Color.random()
        )

    except IndexError:
        localembed = discord.Embed(
            title=f"Flair `{flair_id} does not exist.",
            description="If this is inaccurate, please report this bug to **xyrenchess**.",
            color=discord.Color.random()
        )

    await ctx.respond(embed=localembed)


@client.slash_command(
    name="viewprogress",
    description="View the progression graph of a Chess.com user."
)
@option(name="user", description="Specify a user.", type=str)
@option(name="format", description="Specify a format.", type=str, choices=["daily", "rapid", "blitz", "bullet"], default="rapid")
@option(name="period", description="Specify a period of time.", type=str, choices=["30 days", "60 days", "90 days"], default="60 days")
async def progressgraph(ctx: ApplicationContext, user: str, format: str, period: str):
    await ctx.defer(invisible=True)
    uinfo = cc.get_player_profile(user).json
    ustats = cc.get_player_stats(user).json

    uname = uinfo['player']['username']

    try:
        check = ustats['stats'][f'chess_{format}'] # anything related to an unplayed tc should work

        if period == "30 days":
            req = urllib.request.Request(
                url=f"https://www.chess.com/callback/live/stats/{uname}/chart?daysAgo=30&type={format}",
                headers={'User-Agent': 'Mozilla/5.0'}
            )

        elif period == "60 days":
            req = urllib.request.Request(
                url=f"https://www.chess.com/callback/live/stats/{uname}/chart?daysAgo=60&type={format}",
                headers={'User-Agent': 'Mozilla/5.0'}
            )

        elif period == "90 days":
            req = urllib.request.Request(
                url=f"https://www.chess.com/callback/live/stats/{uname}/chart?daysAgo=90&type={format}",
                headers={'User-Agent': 'Mozilla/5.0'}
            )

        else:
            req = urllib.request.Request(
                url=f"https://www.chess.com/callback/live/stats/{uname}/chart?daysAgo=60&type={format}",
                headers={'User-Agent': 'Mozilla/5.0'}
            )

        with urllib.request.urlopen(req) as url:
            data = json.load(url)

        timer = list()
        xtimer = list()
        ratings = list()

        for i in data:
            if period == "30 days":
                j = time.strftime('%Y-%m-%d', time.localtime(int(i['timestamp'])/1000))
                timer.append(j)
                xtimer.append(int(i['timestamp'])/1000)
                ratings.append(i['rating'])

            elif period == "60 days" or period == "90 days":
                if int(time.strftime('%d', time.localtime(int(i['timestamp'])/1000))) % 2 == 0:
                    j = time.strftime('%Y-%m-%d', time.localtime(int(i['timestamp'])/1000))
                    timer.append(j)
                    xtimer.append(int(i['timestamp'])/1000)
                    ratings.append(i['rating'])

                else:
                    pass

            else:
                print('?') # unknown error, this should never appear/ being used

        x = np.array(timer)
        y = ratings

        data_stream = io.BytesIO()
        fig = plt.figure(figsize=(25, 8))

        plt.plot(x, y)
        plt.xticks(rotation=60)

        plt.savefig(data_stream, format='png', bbox_inches="tight", dpi=80)
        plt.close()

        data_stream.seek(0)
        chart = discord.File(data_stream, filename="psgraph.png")

        localembed = discord.Embed(
            title=f"{uname}'s {period} progress ({format}):",
            description="",
            color=discord.Color.random()
        )

        localembed.set_image(url="attachment://psgraph.png")
        localembed.set_footer(text=f"The collected data from https://www.chess.com/callback/live/stats/{uname}/chart?daysAgo={period}&type={format} is unstable and might be inaccurate.")

        await ctx.respond(embed=localembed, file=chart)

    except:
        localembed = discord.Embed(
            title=f"{uname}'s {period} progress ({format}):",
            description="",
            color=discord.Color.random()
        )
        localembed.add_field(
            name=f"This user has not played any {format} games.",
            value=""
        )

        await ctx.respond(embed=localembed)


@client.slash_command(
    name="progressgraph",
    description="View the progression graph of a user."
)
@option(name="user", description="Specify a user.", type=discord.User, default=None)
@option(name="format", description="Specify a format.", type=str, choices=["daily", "rapid", "blitz", "bullet"], default="rapid")
@option(name="period", description="Specify a period of time.", type=str, choices=["30 days", "60 days", "90 days"], default="60 days")
async def progressgraph(ctx: ApplicationContext, user: discord.User, format: str, period: str):
    await ctx.defer(invisible=True)
    if user == None:
        user = str(ctx.author.id)
    else:
        user = str(user.id)

    try:
        member = cc_user[user]["uname"]
        uinfo = cc.get_player_profile(member).json
        ustats = cc.get_player_stats(member).json

    except:
        localembed = discord.Embed(
            title="You do not have a connected account.",
            description="If this is inaccurate, please report this bug to **xyrenchess**.",
            color=discord.Color.random()
        )

        return await ctx.respond(embed=localembed)

    uname = uinfo['player']['username']

    try:
        check = ustats['stats'][f'chess_{format}'] # anything related to an unplayed tc should work

        if period == "30 days":
            req = urllib.request.Request(
                url=f"https://www.chess.com/callback/live/stats/{uname}/chart?daysAgo=30&type={format}",
                headers={'User-Agent': 'Mozilla/5.0'}
            )

        elif period == "60 days":
            req = urllib.request.Request(
                url=f"https://www.chess.com/callback/live/stats/{uname}/chart?daysAgo=60&type={format}",
                headers={'User-Agent': 'Mozilla/5.0'}
            )

        elif period == "90 days":
            req = urllib.request.Request(
                url=f"https://www.chess.com/callback/live/stats/{uname}/chart?daysAgo=90&type={format}",
                headers={'User-Agent': 'Mozilla/5.0'}
            )

        else:
            req = urllib.request.Request(
                url=f"https://www.chess.com/callback/live/stats/{uname}/chart?daysAgo=60&type={format}",
                headers={'User-Agent': 'Mozilla/5.0'}
            )

        with urllib.request.urlopen(req) as url:
            data = json.load(url)

        timer = list()
        xtimer = list()
        ratings = list()

        for i in data:
            if period == "30 days":
                j = time.strftime('%Y-%m-%d', time.localtime(int(i['timestamp'])/1000))
                timer.append(j)
                xtimer.append(int(i['timestamp'])/1000)
                ratings.append(i['rating'])

            elif period == "60 days" or period == "90 days":
                if int(time.strftime('%d', time.localtime(int(i['timestamp'])/1000))) % 2 == 0:
                    j = time.strftime('%Y-%m-%d', time.localtime(int(i['timestamp'])/1000))
                    timer.append(j)
                    xtimer.append(int(i['timestamp'])/1000)
                    ratings.append(i['rating'])

                else:
                    pass

            else:
                print('?') # unknown error, this should never appear/ being used

        x = np.array(timer)
        y = ratings

        data_stream = io.BytesIO()
        fig = plt.figure(figsize=(25, 8))

        plt.plot(x, y)
        plt.xticks(rotation=60)

        plt.savefig(data_stream, format='png', bbox_inches="tight", dpi=80)
        plt.close()

        data_stream.seek(0)
        chart = discord.File(data_stream, filename="psgraph.png")

        localembed = discord.Embed(
            title=f"{uname}'s {period} progress ({format}):",
            description="",
            color=discord.Color.random()
        )

        localembed.set_image(url="attachment://psgraph.png")
        localembed.set_footer(text=f"The collected data from https://www.chess.com/callback/live/stats/{uname}/chart?daysAgo={period}&type={format} is unstable and might be inaccurate.")

        await ctx.respond(embed=localembed, file=chart)

    except:
        localembed = discord.Embed(
            title=f"{uname}'s {period} progress ({format}):",
            description="",
            color=discord.Color.random()
        )
        localembed.add_field(
            name=f"This user has not played any {format} games.",
            value=""
        )

        await ctx.respond(embed=localembed)


@client.slash_command(
    name="puzzle",
    description="Get a random daily puzzle from Chess.com."
)
async def puzzlerandom(ctx: ApplicationContext):
    await ctx.defer(invisible=True)
    req = urllib.request.Request(
        url="https://api.chess.com/pub/puzzle/random",
        headers={'User-Agent': 'Mozilla/5.0'}
    )

    with urllib.request.urlopen(req) as url:
        data = json.load(url)

    if data['fen'].split()[1] == 'w':
        localembed = discord.Embed(
            title=f"Puzzle from <t:{data['publish_time']}:D>",
            description=f"**White** to move.",
            color=discord.Color.random()
        )

    else:
        localembed = discord.Embed(
            title=f"Puzzle from <t:{data['publish_time']}:D>",
            description=f"**Black** to move.",
            color=discord.Color.random()
        )

    localembed.add_field(name='', value='')

    board = chess.Board(data["fen"])
    setlist = []

    def gensvg():
        if data["fen"].split()[1] == "w":
            boardsvg = chess.svg.board(flipped=False, coordinates=True, board=board, size=350, colors={"square light": "#eeedd5", "square dark": "#7c945d", "square dark lastmove": "#bdc959", "square light lastmove": "#f6f595"})
        else:
            boardsvg = chess.svg.board(flipped=True, coordinates=True, board=board, size=350, colors={"square light": "#eeedd5", "square dark": "#7c945d", "square dark lastmove": "#bdc959", "square light lastmove": "#f6f595"})

        f = open("db/cache/position.svg", "w")
        f.write(boardsvg)
        f.close()

        doc = aw.Document()
        builder = aw.DocumentBuilder(doc)
        shape = builder.insert_image("db/cache/position.svg")

        global log
        log = ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))
        shape.get_shape_renderer().save(f"db/cache/puzzle{log}.png", aw.saving.ImageSaveOptions(aw.SaveFormat.PNG))

    gensvg()
    file = discord.File(f"db/cache/puzzle{log}.png", filename=f"puzzle{log}.png")

    localembed.set_image(url=f"attachment://puzzle{log}.png")
    localembed.set_footer(text=data["url"])

    await ctx.respond(embed=localembed, file=file)

    pgn0 = data['pgn'].split('1.')[1].strip()
    pgn = re.sub('\r\n|\d+\.\s|\d+\.|\.{2}|\*|1-0|0-1|1/2-1/2', '', pgn0).split()

    def check(m):
        return m.channel == ctx.channel

    async def moves():
        if pgn.index(pgn[0]) % 2 == 0:
            msg = await client.wait_for("message", check=check)
            print(re.sub("[x+#=]", '', pgn[0])) # cheating cuz im bad at chess

            if re.match('[QKNBR]?[a-h]?[1-8]?x?[a-h][1-8](=[QNBR])?([+#])?', msg.content):
                try:
                    if re.sub("[x+#=]", '', msg.content) == re.sub("[x+#=]", '', pgn[0]):

                        try:
                            board.push_san(pgn[0]) # your move
                            setlist.append(pgn.pop(0))

                            board.push_san(pgn[0]) # opponents response
                            setlist.append(pgn.pop(0))

                            localembed.set_field_at(0, name=' '.join(setlist), value='')

                            gensvg()
                            file = discord.File(f"db/cache/puzzle{log}.png", filename=f"puzzle{log}.png")

                            localembed.set_image(url=f"attachment://puzzle{log}.png")

                            await ctx.respond(embed=localembed, file=file)
                            return await moves()

                        except IndexError:
                            gensvg()
                            file = discord.File(f"db/cache/puzzle{log}.png", filename=f"puzzle{log}.png")

                            localembed.set_image(url=f"attachment://puzzle{log}.png")
                            localembed.set_field_at(0, name=' '.join(setlist), value='')
                            localembed.add_field(name='Puzzle solved!', value='', inline=False)

                            await ctx.respond(embed=localembed, file=file)

                    else:
                        try:
                            board.parse_san(msg.content)

                            await ctx.respond("Wrong move!")
                            return await moves()

                        except chess.InvalidMoveError:
                            await ctx.respond("Invalid move!")
                            return await moves()

                        except chess.IllegalMoveError:
                            await ctx.respond("Illegal move!")
                            return await moves()

                        except chess.AmbiguousMoveError:
                            await ctx.respond("Please specify which piece youre going to move!\nThere are two or more pieces can reach that square!")
                            return await moves()

                except IndexError:
                    gensvg()
                    file = discord.File(f"db/cache/puzzle{log}.png", filename=f"puzzle{log}.png")

                    localembed.set_image(url=f"attachment://puzzle{log}.png")
                    localembed.set_field_at(0, name=' '.join(setlist))
                    localembed.add_field(name='Puzzle solved!', value='')

                    return await ctx.respond(embed=localembed, file=file)
            else:
                return await moves() # ignore

    for i in pgn:
        try:
            await moves()
        except:
            return await moves()


@client.slash_command(
    name="analyse",
    description="Analyse a position with the given FEN."
)
@option(name="fen", description="Specify position with FEN.", type=str)
@option(name="depth", description="Specify engine's depth.", type=int, choices=[15, 20, 25], default=15)
@option(name="lines", description="Specify how many engine moves to show. (p.s. 8 lines with 25 depths would take longer to analyse.)", type=int, choices=[3, 5, 8], default=3)
async def analyse(ctx: ApplicationContext, fen: str, depth: int, lines: int):
    await ctx.defer(invisible=True)
    if commands_db["analyse"]["disabled"] == 'true':
        return await ctx.respond("This command is temporarily disabled!")
    else:
        try:
            board = chess.Board(fen)
        except:
            localembed = discord.Embed(title=f"Invalid FEN position!: {fen}")
            return await ctx.respond(embed=localembed)

        stockfish.set_depth(depth)
        stockfish.set_fen_position(fen)

        best = stockfish.get_top_moves(lines)
        ev0 = stockfish.get_evaluation()

        if fen.split()[1] == "w":
            boardsvg = chess.svg.board(flipped=False, coordinates=True, board=board, size=350, colors={"square light": "#eeedd5", "square dark": "#7c945d", "square dark lastmove": "#bdc959", "square light lastmove": "#f6f595"})
            localembed = discord.Embed(
                title="__Evaluation (_White_ to move):__",
                description=f'Analysing position {fen}',
                color=discord.Color.random()
            )

        else:
            boardsvg = chess.svg.board(flipped=True, coordinates=True, board=board, size=350, colors={"square light": "#eeedd5", "square dark": "#7c945d", "square dark lastmove": "#bdc959", "square light lastmove": "#f6f595"})
            localembed = discord.Embed(
                title="__Evaluation (_Black_ to move):__",
                description=f'Analysing position {fen}',
                color=discord.Color.random()
            )

        f = open("db/cache/position.svg", "w")
        f.write(boardsvg)
        f.close()

        doc = aw.Document()
        builder = aw.DocumentBuilder(doc)
        shape = builder.insert_image("db/cache/position.svg")

        global log
        log = ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))
        shape.get_shape_renderer().save(f"db/cache/eval{log}.png", aw.saving.ImageSaveOptions(aw.SaveFormat.PNG))

        file = discord.File(f"db/cache/eval{log}.png", filename=f"eval{log}.png")
        localembed.set_image(url=f"attachment://eval{log}.png")

        if ev0["type"] == "cp":
            ev = ev0["value"]/100
        else:
            if ev0["value"] == 0 and board.is_checkmate() and fen.split()[1] == "b":
                ev = "M0"
            elif ev0["value"] == 0 and board.is_checkmate() and fen.split()[1] == "w":
                ev = "-M0"
            else:
                ev = f"M{ev0['value']}"

        if ev == "M0":
            localembed.add_field(name="__Eval:__", value="_White_ won by Checkmate", inline=False)
        elif ev == "-M0":
            localembed.add_field(name="__Eval:__", value="_Black_ won by Checkmate", inline=False)
        else:
            if board.is_stalemate():
                localembed.add_field(name="__Eval:__", value="Draw by Stalemate", inline=False)
            elif board.is_insufficient_material():
                localembed.add_field(name="__Eval:__", value="Draw by Insufficient material", inline=False)
            elif board.is_fifty_moves():
                localembed.add_field(name="__Eval:__", value="Draw by 50 move rule", inline=False)
            else:
                localembed.add_field(name="__Eval:__", value=ev, inline=False)

        if len(best) == 0:
            localembed.add_field(name="", value='', inline=False)
        else:
            localembed.add_field(name="__Top engine moves:__", value='', inline=False)

        for i in best:
            if i["Mate"] == None:
                if i["Centipawn"] > 0:
                    localembed.add_field(name=board.san(chess.Move.from_uci(i["Move"])), value=f"_White_ has the advantage of {i['Centipawn']/100}", inline=False)
                elif i["Centipawn"] < 0:
                    localembed.add_field(name=board.san(chess.Move.from_uci(i["Move"])), value=f"_Black_ has the advantage of {i['Centipawn']/100*-1}", inline=False)
                else:
                    localembed.add_field(name=board.san(chess.Move.from_uci(i["Move"])), value=f"Position is equal ({i['Centipawn']/100})", inline=False)

            else:
                if i["Mate"] > 0:
                    localembed.add_field(name=board.san(chess.Move.from_uci(i["Move"])), value=f"Mate in {i['Mate']} by _White_", inline=False)
                else:
                    localembed.add_field(name=board.san(chess.Move.from_uci(i["Move"])), value=f"Mate in {i['Mate']*-1} by _Black_", inline=False)

        await ctx.respond(embed=localembed, file=file)


@client.slash_command(
    name="deepanalyse",
    description="Deep analyse a position with the given FEN."
)
@option(name="fen", description="Specify position with FEN.", type=str)
@option(name="depth", description="Specify engine's depth.", type=int, choices=[30, 35, 40], default=30)
async def deepanalyse(ctx: ApplicationContext, fen: str, depth: int):
    await ctx.defer(invisible=True)
    if commands_db["analyse"]["disabled"] == 'true':
        return await ctx.respond("This command is temporarily disabled!")
    else:
        try:
            board = chess.Board(fen)
        except:
            localembed = discord.Embed(title=f"Invalid FEN position!: {fen}")
            return await ctx.respond(embed=localembed)

        stockfish.set_depth(depth)
        stockfish.set_fen_position(fen)

        best = stockfish.get_top_moves(3)
        ev0 = stockfish.get_evaluation()

        if fen.split()[1] == "w":
            boardsvg = chess.svg.board(flipped=False, coordinates=True, board=board, size=350, colors={"square light": "#eeedd5", "square dark": "#7c945d", "square dark lastmove": "#bdc959", "square light lastmove": "#f6f595"})
            localembed = discord.Embed(
                title="__Evaluation (_White_ to move):__",
                description=f'Analysing position {fen}',
                color=discord.Color.random()
            )

        else:
            boardsvg = chess.svg.board(flipped=True, coordinates=True, board=board, size=350, colors={"square light": "#eeedd5", "square dark": "#7c945d", "square dark lastmove": "#bdc959", "square light lastmove": "#f6f595"})
            localembed = discord.Embed(
                title="__Evaluation (_Black_ to move):__",
                description=f'Analysing position {fen}',
                color=discord.Color.random()
            )

        f = open("db/cache/position.svg", "w")
        f.write(boardsvg)
        f.close()

        doc = aw.Document()
        builder = aw.DocumentBuilder(doc)
        shape = builder.insert_image("db/cache/position.svg")

        global log
        log = ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))
        shape.get_shape_renderer().save(f"db/cache/eval{log}.png", aw.saving.ImageSaveOptions(aw.SaveFormat.PNG))

        file = discord.File(f"db/cache/eval{log}.png", filename=f"eval{log}.png")
        localembed.set_image(url=f"attachment://eval{log}.png")

        if ev0["type"] == "cp":
            ev = ev0["value"]/100
        else:
            if ev0["value"] == 0 and board.is_checkmate() and fen.split()[1] == "b":
                ev = "M0"
            elif ev0["value"] == 0 and board.is_checkmate() and fen.split()[1] == "w":
                ev = "-M0"
            else:
                ev = f"M{ev0['value']}"

        if ev == "M0":
            localembed.add_field(name="__Eval:__", value="_White_ won by Checkmate", inline=False)
        elif ev == "-M0":
            localembed.add_field(name="__Eval:__", value="_Black_ won by Checkmate", inline=False)
        else:
            if board.is_stalemate():
                localembed.add_field(name="__Eval:__", value="Draw by Stalemate", inline=False)
            elif board.is_insufficient_material():
                localembed.add_field(name="__Eval:__", value="Draw by Insufficient material", inline=False)
            elif board.is_fifty_moves():
                localembed.add_field(name="__Eval:__", value="Draw by 50 move rule", inline=False)
            else:
                localembed.add_field(name="__Eval:__", value=ev, inline=False)

        if len(best) == 0:
            localembed.add_field(name="", value='', inline=False)
        else:
            localembed.add_field(name="__Top engine moves:__", value='', inline=False)

        for i in best:
            if i["Mate"] == None:
                if i["Centipawn"] > 0:
                    localembed.add_field(name=board.san(chess.Move.from_uci(i["Move"])), value=f"_White_ has the advantage of {i['Centipawn']/100}", inline=False)
                elif i["Centipawn"] < 0:
                    localembed.add_field(name=board.san(chess.Move.from_uci(i["Move"])), value=f"_Black_ has the advantage of {i['Centipawn']/100*-1}", inline=False)
                else:
                    localembed.add_field(name=board.san(chess.Move.from_uci(i["Move"])), value=f"Position is equal ({i['Centipawn']/100})", inline=False)

            else:
                if i["Mate"] > 0:
                    localembed.add_field(name=board.san(chess.Move.from_uci(i["Move"])), value=f"Mate in {i['Mate']} by _White_", inline=False)
                else:
                    localembed.add_field(name=board.san(chess.Move.from_uci(i["Move"])), value=f"Mate in {i['Mate']*-1} by _Black_", inline=False)

        await ctx.respond(embed=localembed, file=file)


@client.slash_command(
    name="lcpuzzle",
    description="Get a puzzle from Lichess.org."
)
@option(name="id", description="Specify a puzzle's ID to retrieve.", type=str, default=None)
async def puzzlelc(ctx: ApplicationContext, id: str):
    await ctx.defer(invisible=True)
    if commands_db["lcpuzzle"]["disabled"] == 'true':
        return await ctx.respond("This command is temporarily disabled!")
    else:
        if id == None:
            return await ctx.respond("I have a sh*t pc and this mf wont let me use the lichess database from the csv file... I guess I cant generate random puzzles unless someone do it for me :(\nhttps://cdn.discordapp.com/attachments/1207936256265293856/1238856249634983956/image.png?ex=6640ce4a&is=663f7cca&hm=e3485d8f28d3929c9646aae5da9cddcef216bb78b0b9b38f7953467150ad8618&")
        else:
            try:
                pz = berserker.puzzles.get(id)
            except:
                localembed = discord.Embed(title=f"Puzzle {id} does not exist!")
                return await ctx.respond(embed=localembed)

        rating = pz['puzzle']['rating']

        pgn0 = pz["game"]['pgn'].split()
        board = chess.Board()
        setlist = []

        for i in pgn0:
            board.push(board.parse_san(i))

        fen = board.fen()

        pgn = []
        solution = pz["puzzle"]["solution"]
        for i in solution:
            pgn.append(board.san(board.parse_uci(i)))
            board.push(board.parse_uci(i))

        print(pgn)

        board = chess.Board(fen.split()[0])

        if fen.split()[1] == 'w':
            localembed = discord.Embed(
                title=f"Puzzle {id} | _Rating: ||{rating}||_",
                description=f"**White** to move.",
                color=discord.Color.random()
            )

        else:
            localembed = discord.Embed(
                title=f"Puzzle {id}| _Rating: ||{rating}||_",
                description=f"**Black** to move.",
                color=discord.Color.random()
            )

        localembed.add_field(name='', value='')

        def gensvg():
            if fen.split()[1] == "w":
                boardsvg = chess.svg.board(flipped=False, coordinates=True, board=board, size=350, colors={"square light": "#eeedd5", "square dark": "#7c945d", "square dark lastmove": "#bdc959", "square light lastmove": "#f6f595"})
            else:
                boardsvg = chess.svg.board(flipped=True, coordinates=True, board=board, size=350, colors={"square light": "#eeedd5", "square dark": "#7c945d", "square dark lastmove": "#bdc959", "square light lastmove": "#f6f595"})

            f = open("db/cache/position.svg", "w")
            f.write(boardsvg)
            f.close()

            doc = aw.Document()
            builder = aw.DocumentBuilder(doc)
            shape = builder.insert_image("db/cache/position.svg")

            global log
            log = ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))
            shape.get_shape_renderer().save(f"db/cache/puzzle{log}.png", aw.saving.ImageSaveOptions(aw.SaveFormat.PNG))

        gensvg()
        file = discord.File(f"db/cache/puzzle{log}.png", filename=f"puzzle{log}.png")

        localembed.set_image(url=f"attachment://puzzle{log}.png")
        localembed.set_footer(text=f"https://lichess.org/training/{id}")

        await ctx.respond(embed=localembed, file=file)

        def check(m):
            return m.channel == ctx.channel

        async def moves():
            if pgn.index(pgn[0]) % 2 == 0:
                msg = await client.wait_for("message", check=check)
                print(re.sub("[x+#=]", '', pgn[0])) # cheating cuz im bad at chess

                if re.match('[QKNBR]?[a-h]?[1-8]?x?[a-h][1-8](=[QNBR])?([+#])?', msg.content):
                    try:
                        if re.sub("[x+#=]", '', msg.content) == re.sub("[x+#=]", '', pgn[0]):
                            try:
                                board.push_san(pgn[0]) # your move
                                setlist.append(pgn.pop(0))

                                board.push_san(pgn[0]) # opponents response
                                setlist.append(pgn.pop(0))

                                localembed.set_field_at(0, name=' '.join(setlist), value='')

                                gensvg()
                                file = discord.File(f"db/cache/puzzle{log}.png", filename=f"puzzle{log}.png")

                                localembed.set_image(url=f"attachment://puzzle{log}.png")

                                await ctx.respond(embed=localembed, file=file)
                                return await moves()

                            except IndexError:
                                gensvg()
                                file = discord.File(f"db/cache/puzzle{log}.png", filename=f"puzzle{log}.png")

                                localembed.set_image(url=f"attachment://puzzle{log}.png")
                                localembed.set_field_at(0, name=' '.join(setlist), value='')
                                localembed.add_field(name='Puzzle solved!', value='', inline=False)

                                await ctx.respond(embed=localembed, file=file)

                        else:
                            try:
                                board.parse_san(msg.content)

                                await ctx.respond("Wrong move!")
                                return await moves()

                            except chess.InvalidMoveError:
                                await ctx.respond("Invalid move!")
                                return await moves()

                            except chess.IllegalMoveError:
                                await ctx.respond("Illegal move!")
                                return await moves()

                            except chess.AmbiguousMoveError:
                                await ctx.respond("Please specify which piece youre going to move!\nThere are two or more pieces can reach that square!")
                                return await moves()

                    except IndexError:
                        gensvg()
                        file = discord.File(f"db/cache/puzzle{log}.png", filename=f"puzzle{log}.png")

                        localembed.set_image(url=f"attachment://puzzle{log}.png")
                        localembed.set_field_at(0, name=' '.join(setlist), value='')
                        localembed.add_field(name='Puzzle solved!', value='')

                        return await ctx.respond(embed=localembed, file=file)
                else:
                    return await moves() # ignore

        for i in pgn:
            try:
                await moves()
            except:
                return await moves()


@client.slash_command(
    name="game",
    description="Start a chess game with Stockfish or another user."
)
@option(name="black_player", description="Specify a player to play as Black... or you can play with Stockfish!", type=discord.User, default=None)
@option(name="fen", description="From position.", type=str, default="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
async def chessinmywayto2000(ctx: ApplicationContext, black_player: discord.User, fen: str):
    await ctx.defer(invisible=True)
    board = chess.Board(fen)

    gameid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))

    global finished, movelist, count
    finished = False
    movelist = []
    count = 0

    if black_player == None:
        localembed = discord.Embed(
            title=f"Game {gameid}",
            description=f"{ctx.author.name} VS Stockfish 15",
            color=discord.Color.random()
        )
        localembed.add_field(name='', value='', inline=False)
    elif ctx.author.id == black_player.id:
        localembed = discord.Embed(
            title=f"You cant play yourself!",
            description=f"I thought chess players are intelligent...",
            color=discord.Color.random()
        )
        return await ctx.respond(embed=localembed)
    else:
        localembed = discord.Embed(
            title=f"Game {gameid}",
            description=f"{ctx.author.name} VS {black_player.name}",
            color=discord.Color.random()
        )
        localembed.add_field(name='', value='', inline=False)

    def gensvg():
        if board.fen().split()[1] == "w":
            boardsvg = chess.svg.board(flipped=False, coordinates=True, board=board, size=350, colors={"square light": "#eeedd5", "square dark": "#7c945d", "square dark lastmove": "#bdc959", "square light lastmove": "#f6f595"})
        else:
            boardsvg = chess.svg.board(flipped=True, coordinates=True, board=board, size=350, colors={"square light": "#eeedd5", "square dark": "#7c945d", "square dark lastmove": "#bdc959", "square light lastmove": "#f6f595"})

        f = open("db/cache/game.svg", "w")
        f.write(boardsvg)
        f.close()

        doc = aw.Document()
        builder = aw.DocumentBuilder(doc)
        shape = builder.insert_image("db/cache/game.svg")

        global log
        log = ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))
        shape.get_shape_renderer().save(f"db/cache/game{log}.png", aw.saving.ImageSaveOptions(aw.SaveFormat.PNG))

    def get_best_move():
        stockfish.set_fen_position(board.fen())
        best = stockfish.get_best_move()
        return best

    def check_white(m):
        return m.channel == ctx.channel and m.author.id == ctx.author.id

    def check_black(m):
        return m.channel == ctx.channel and m.author.id == black_player.id

    def check_end():
        global finished, termin, res, movelist
        if board.is_checkmate():
            if board.fen().split()[1] == "w":
                termin = "Black won by checkmate"
                res = "0-1"
            else:
                termin = "White won by checkmate"
                res = "1-0"

            finished = True

        elif board.is_stalemate():
            termin = "Game drawn by stalemate"
            res = "1/2-1/2"
            finished = True
        elif board.is_repetition():
            termin = "Game drawn by repetition"
            res = "1/2-1/2"
            finished = True
        elif board.is_insufficient_material():
            termin = "Game drawn by insufficient material"
            res = "1/2-1/2"
            finished = True
        elif board.is_fifty_moves():
            termin = "Game drawn by 50-move rule"
            res = "1/2-1/2"
            finished = True
        else:
            termin = ""
            res = ""

        movelist.append(f"{res}")
        movelist = list(filter(None, movelist))

        with open(f"db/game_archive/{gameid}.pgn", "w") as f:
            if black_player == None:
                f.write(f"""
[Event "Live Chess"]
[Site "Played with Blue#4895 Discord Bot"]
[Date "{datetime.today().strftime('%Y.%m.%d')}"]
[Round "?"]
[White "{ctx.author.name}"]
[Black "Stockfish 15"]
[Result "{res}"]
[SetUp "1"]
[FEN "{board.fen()}"]
[WhiteElo "?"]
[BlackElo "?"]
[TimeControl "1/0"]
[EndDate "{datetime.today().strftime('%Y.%m.%d')}"]
[Termination "{termin}"]

{' '.join(movelist)}
                """)
            else:
                f.write(f"""
[Event "Live Chess"]
[Site "Played with Blue#4895 Discord Bot"]
[Date "{datetime.today().strftime('%Y.%m.%d')}"]
[Round "?"]
[White "{ctx.author.name}"]
[Black "{black_player.name}"]
[Result "{res}"]
[SetUp "1"]
[FEN "{board.fen()}"]
[WhiteElo "?"]
[BlackElo "?"]
[TimeControl "1/0"]
[EndDate "{datetime.today().strftime('%Y.%m.%d')}"]
[Termination "{termin}"]

{' '.join(movelist)}
                """)
            f.close()

        return finished

    async def wenginemoves():
        msg = await client.wait_for("message", check=check_white)

        try:
            r = re.match('[QKNBR]?[a-h]?[1-8]?x?[a-h][1-8](=[QNBR])?([+#])?|O-O|0-0|O-O-O|0-0-0', msg.content).group(0)
            m = msg.content.replace(r, '')

            if ' ' not in msg.content and m == '':
                try:
                    umove = board.push_san(msg.content) # your move

                    global count
                    count = count + 1

                    movelist.append(f"{count}.")
                    movelist.append(msg.content)

                    try:
                        move = get_best_move()
                        movelist.append(board.san(chess.Move.from_uci(move)))
                        board.push_san(move) # bots response

                    except TypeError: # white mated black (x. Bh5# NoneType)
                        pass

                    localembed.set_field_at(0, name=' '.join(movelist[-10:]), value='')

                    gensvg()
                    file = discord.File(f"db/cache/game{log}.png", filename=f"game{log}.png")

                    localembed.set_image(url=f"attachment://game{log}.png")

                    finished = check_end()
                    if finished:
                        localembed.set_field_at(0, name=' '.join(movelist[-10:]), value=f"{termin}")
                        await msg.delete()
                        await ctx.edit(embed=localembed, file=file)

                        globals()["stop"+str(ctx.author.id)] = False

                        return finished
                    else:
                        await msg.delete()
                        await ctx.edit(embed=localembed, file=file)
                        return await wenginemoves()

                except chess.InvalidMoveError:
                    c = await ctx.respond("Invalid move!")
                    await c.delete(delay=1)
                    await msg.delete(delay=1)
                    return await wenginemoves()

                except chess.IllegalMoveError:
                    c = await ctx.respond("Illegal move!")
                    await c.delete(delay=1)
                    await msg.delete(delay=1)
                    return await wenginemoves()

                except chess.AmbiguousMoveError:
                    c = await ctx.respond("Please specify which piece youre going to move!\nThere are two or more pieces can reach that square!")
                    await c.delete(delay=1)
                    await msg.delete(delay=1)
                    return await wenginemoves()
            else:
                return await wenginemoves()
        except:
            return await wenginemoves()

    async def blacksm():
        msg1 = await client.wait_for("message", check=check_black)

        try:
            r = re.match('[QKNBR]?[a-h]?[1-8]?x?[a-h][1-8](=[QNBR])?([+#])?|O-O|0-0|O-O-O|0-0-0', msg1.content).group(0)
            m = msg1.content.replace(r, '')

            if ' ' not in msg1.content and m == '':
                try:
                    umove = board.push_san(msg1.content) # blacks move
                    movelist.append(msg1.content)


                    localembed.set_field_at(0, name=' '.join(movelist[-10:]), value='')

                    gensvg()
                    file = discord.File(f"db/cache/game{log}.png", filename=f"game{log}.png")

                    localembed.set_image(url=f"attachment://game{log}.png")

                    finished = check_end()
                    if finished:
                        localembed.set_field_at(0, name=' '.join(movelist[-10:]), value=f"{termin}")
                        await msg1.delete()
                        await ctx.edit(embed=localembed, file=file)
                        return finished
                    else:
                        await msg1.delete()
                        await ctx.edit(embed=localembed, file=file)
                        return await wusermoves()

                except chess.InvalidMoveError:
                    b = await ctx.respond("Invalid move!")
                    await b.delete(delay=1)
                    await msg1.delete(delay=1)
                    return await blacksm()

                except chess.IllegalMoveError:
                    b = await ctx.respond("Illegal move!")
                    await b.delete(delay=1)
                    await msg1.delete(delay=1)
                    return await blacksm()

                except chess.AmbiguousMoveError:
                    b = await ctx.respond("Please specify which piece youre going to move!\nThere are two or more pieces can reach that square!")
                    await b.delete(delay=1)
                    await msg1.delete(delay=1)
                    return await blacksm()
            else:
                return await blacksm()
        except:
            return await blacksm()

    async def wusermoves():
        msg0 = await client.wait_for("message", check=check_white)

        try:
            r = re.match('[QKNBR]?[a-h]?[1-8]?x?[a-h][1-8](=[QNBR])?([+#])?|O-O|0-0|O-O-O|0-0-0', msg0.content).group(0)
            m = msg0.content.replace(r, '')

            if ' ' not in msg0.content and m == '':
                try:
                    umove = board.push_san(msg0.content) # whites move

                    global count
                    count = count + 1

                    movelist.append(f"{count}.")
                    movelist.append(msg0.content)

                    localembed.set_field_at(0, name=' '.join(movelist[-10:]), value='')

                    gensvg()
                    file = discord.File(f"db/cache/game{log}.png", filename=f"game{log}.png")

                    localembed.set_image(url=f"attachment://game{log}.png")

                    finished = check_end()
                    if finished:
                        localembed.set_field_at(0, name=' '.join(movelist[-10:]), value=f"{termin}")
                        await msg0.delete()
                        await ctx.edit(embed=localembed, file=file)

                        globals()["stop"+str(ctx.author.id)] = False
                        globals()["stop"+str(black_player.id)] = False

                        return finished
                    else:
                        await msg0.delete()
                        await ctx.edit(embed=localembed, file=file)
                        print(movelist)
                        return await blacksm()

                except chess.InvalidMoveError:
                    a = await ctx.respond("Invalid move!")
                    await a.delete(delay=1)
                    await msg0.delete(delay=1)
                    return await wusermoves()

                except chess.IllegalMoveError:
                    a = await ctx.respond("Illegal move!")
                    await a.delete(delay=1)
                    await msg0.delete(delay=1)
                    return await wusermoves()

                except chess.AmbiguousMoveError:
                    a = await ctx.respond("Please specify which piece youre going to move!\nThere are two or more pieces can reach that square!")
                    await a.delete(delay=1)
                    await msg0.delete(delay=1)
                    return await wusermoves()
            else:
                return await wusermoves()
        except:
            return await wusermoves()

    if black_player == client.user:
        localembed = discord.Embed(title="I am busy playing on Chess.com and Lichess! Maybe next time...")
        return await ctx.respond(embed=localembed)

    elif black_player == None: # playing with engine
        try:
            ustop = globals()["stop"+str(ctx.author.id)]
        except:
            ustop = False

        if ustop != True:
            globals()["stop"+str(ctx.author.id)] = True

            gensvg()
            file = discord.File(f"db/cache/game{log}.png", filename=f"game{log}.png")

            localembed.set_image(url=f"attachment://game{log}.png")
            localembed.set_footer(text=f"Game by {ctx.author.id}")

            await ctx.respond(embed=localembed, file=file)
            finished = await wenginemoves()

        else:
            return await ctx.respond(f"<@{ctx.author.id}>, please finish your previous game first before starting a new one!")

    else:
        try:
            ustop0 = globals()["stop"+str(ctx.author.id)]
        except:
            ustop0 = False
        try:
            ustop1 = globals()["stop"+str(black_player.id)]
        except:
            ustop1 = False

        if ustop0 != True and ustop1 != True: # both players are available
            globals()["stop"+str(ctx.author.id)] = True
            globals()["stop"+str(black_player.id)] = True

            gensvg()
            file = discord.File(f"db/cache/game{log}.png", filename=f"game{log}.png")

            localembed.set_image(url=f"attachment://game{log}.png")
            localembed.set_footer(text=f"Game by {ctx.author.id}")

            await ctx.respond(embed=localembed, file=file)
            finished = await wusermoves()

        else: # at least one of the players has an ongoing game
            if ustop0 == True:
                return await ctx.respond(f"<@{ctx.author.id}>, please finish your previous game first before starting a new one!")
            if ustop1 == True:
                return await ctx.respond(f"<@{black_player.id}> has an ongoing game! Please wait until their game is finished before starting a new one with them.")


@client.slash_command(
    name="game_no_perms",
    description="Start a chess game with Stockfish or another user. (no perms command)"
)
@option(name="black_player", description="Specify a player to play as Black... or you can play with Stockfish!", type=discord.User, default=None)
@option(name="fen", description="From position.", type=str, default="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
async def chessinmywayto1600(ctx: ApplicationContext, black_player: discord.User, fen: str):
    await ctx.defer(invisible=True)
    board = chess.Board(fen)

    gameid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))

    global finished, movelist, count
    finished = False
    movelist = []
    count = 0

    if black_player == None:
        localembed = discord.Embed(
            title=f"Game {gameid}",
            description=f"{ctx.author.name} VS Stockfish 15",
            color=discord.Color.random()
        )
        localembed.add_field(name='', value='', inline=False)
    elif ctx.author.id == black_player.id:
        localembed = discord.Embed(
            title=f"You cant play yourself!",
            description=f"I thought chess players are intelligent...",
            color=discord.Color.random()
        )
        return await ctx.respond(embed=localembed)
    else:
        localembed = discord.Embed(
            title=f"Game {gameid}",
            description=f"{ctx.author.name} VS {black_player.name}",
            color=discord.Color.random()
        )
        localembed.add_field(name='', value='', inline=False)

    def gensvg():
        if board.fen().split()[1] == "w":
            boardsvg = chess.svg.board(flipped=False, coordinates=True, board=board, size=350, colors={"square light": "#eeedd5", "square dark": "#7c945d", "square dark lastmove": "#bdc959", "square light lastmove": "#f6f595"})
        else:
            boardsvg = chess.svg.board(flipped=True, coordinates=True, board=board, size=350, colors={"square light": "#eeedd5", "square dark": "#7c945d", "square dark lastmove": "#bdc959", "square light lastmove": "#f6f595"})

        f = open("db/cache/game.svg", "w")
        f.write(boardsvg)
        f.close()

        doc = aw.Document()
        builder = aw.DocumentBuilder(doc)
        shape = builder.insert_image("db/cache/game.svg")

        global log
        log = ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))
        shape.get_shape_renderer().save(f"db/cache/game{log}.png", aw.saving.ImageSaveOptions(aw.SaveFormat.PNG))

    def get_best_move():
        stockfish.set_fen_position(board.fen())
        best = stockfish.get_best_move()
        return best

    def check_white(m):
        return m.channel == ctx.channel and m.author.id == ctx.author.id

    def check_black(m):
        return m.channel == ctx.channel and m.author.id == black_player.id

    def check_end():
        global finished, termin, res, movelist
        if board.is_checkmate():
            if board.fen().split()[1] == "w":
                termin = "Black won by checkmate"
                res = "0-1"
            else:
                termin = "White won by checkmate"
                res = "1-0"

            finished = True

        elif board.is_stalemate():
            termin = "Game drawn by stalemate"
            res = "1/2-1/2"
            finished = True
        elif board.is_repetition():
            termin = "Game drawn by repetition"
            res = "1/2-1/2"
            finished = True
        elif board.is_insufficient_material():
            termin = "Game drawn by insufficient material"
            res = "1/2-1/2"
            finished = True
        elif board.is_fifty_moves():
            termin = "Game drawn by 50-move rule"
            res = "1/2-1/2"
            finished = True
        else:
            termin = ""
            res = ""

        movelist.append(f"{res}")
        movelist = list(filter(None, movelist))

        with open(f"db/game_archive/{gameid}.pgn", "w") as f:
            if black_player == None:
                f.write(f"""
[Event "Live Chess"]
[Site "Played with Blue#4895 Discord Bot"]
[Date "{datetime.today().strftime('%Y.%m.%d')}"]
[Round "?"]
[White "{ctx.author.name}"]
[Black "Stockfish 15"]
[Result "{res}"]
[SetUp "1"]
[FEN "{board.fen()}"]
[WhiteElo "?"]
[BlackElo "?"]
[TimeControl "1/0"]
[EndDate "{datetime.today().strftime('%Y.%m.%d')}"]
[Termination "{termin}"]

{' '.join(movelist)}
                """)
            else:
                f.write(f"""
[Event "Live Chess"]
[Site "Played with Blue#4895 Discord Bot"]
[Date "{datetime.today().strftime('%Y.%m.%d')}"]
[Round "?"]
[White "{ctx.author.name}"]
[Black "{black_player.name}"]
[Result "{res}"]
[SetUp "1"]
[FEN "{board.fen()}"]
[WhiteElo "?"]
[BlackElo "?"]
[TimeControl "1/0"]
[EndDate "{datetime.today().strftime('%Y.%m.%d')}"]
[Termination "{termin}"]

{' '.join(movelist)}
                """)
            f.close()

        return finished

    async def wenginemoves():
        msg = await client.wait_for("message", check=check_white)

        try:
            r = re.match('[QKNBR]?[a-h]?[1-8]?x?[a-h][1-8](=[QNBR])?([+#])?|O-O|0-0|O-O-O|0-0-0', msg.content).group(0)
            m = msg.content.replace(r, '')

            if ' ' not in msg.content and m == '':
                try:
                    umove = board.push_san(msg.content) # your move

                    global count
                    count = count + 1

                    movelist.append(f"{count}.")
                    movelist.append(msg.content)

                    try:
                        move = get_best_move()
                        movelist.append(board.san(chess.Move.from_uci(move)))
                        board.push_san(move) # bots response

                    except TypeError: # white mated black (x. Bh5# NoneType)
                        pass

                    localembed.set_field_at(0, name=' '.join(movelist[-10:]), value='')

                    gensvg()
                    file = discord.File(f"db/cache/game{log}.png", filename=f"game{log}.png")

                    localembed.set_image(url=f"attachment://game{log}.png")

                    finished = check_end()
                    if finished:
                        localembed.set_field_at(0, name=' '.join(movelist[-10:]), value=f"{termin}")
                        await ctx.edit(embed=localembed, file=file)

                        globals()["stop"+str(ctx.author.id)] = False

                        return finished
                    else:
                        await ctx.edit(embed=localembed, file=file)
                        return await wenginemoves()

                except chess.InvalidMoveError:
                    c = await ctx.respond("Invalid move!")
                    await c.delete(delay=1)
                    return await wenginemoves()

                except chess.IllegalMoveError:
                    c = await ctx.respond("Illegal move!")
                    await c.delete(delay=1)
                    return await wenginemoves()

                except chess.AmbiguousMoveError:
                    c = await ctx.respond("Please specify which piece youre going to move!\nThere are two or more pieces can reach that square!")
                    await c.delete(delay=1)
                    return await wenginemoves()
            else:
                return await wenginemoves()
        except:
            return await wenginemoves()

    async def blacksm():
        msg1 = await client.wait_for("message", check=check_black)

        try:
            r = re.match('[QKNBR]?[a-h]?[1-8]?x?[a-h][1-8](=[QNBR])?([+#])?|O-O|0-0|O-O-O|0-0-0', msg1.content).group(0)
            m = msg1.content.replace(r, '')

            if ' ' not in msg1.content and m == '':
                try:
                    umove = board.push_san(msg1.content) # blacks move
                    movelist.append(msg1.content)

                    localembed.set_field_at(0, name=' '.join(movelist[-10:]), value='')

                    gensvg()
                    file = discord.File(f"db/cache/game{log}.png", filename=f"game{log}.png")

                    localembed.set_image(url=f"attachment://game{log}.png")

                    finished = check_end()
                    if finished:
                        localembed.set_field_at(0, name=' '.join(movelist[-10:]), value=f"{termin}")
                        await ctx.edit(embed=localembed, file=file)
                        return finished
                    else:
                        await ctx.edit(embed=localembed, file=file)
                        return await wusermoves()

                except chess.InvalidMoveError:
                    b = await ctx.respond("Invalid move!")
                    await b.delete(delay=1)
                    return await blacksm()

                except chess.IllegalMoveError:
                    b = await ctx.respond("Illegal move!")
                    await b.delete(delay=1)
                    return await blacksm()

                except chess.AmbiguousMoveError:
                    b = await ctx.respond("Please specify which piece youre going to move!\nThere are two or more pieces can reach that square!")
                    await b.delete(delay=1)
                    return await blacksm()
            else:
                return await blacksm()
        except:
            return await blacksm()

    async def wusermoves():
        msg0 = await client.wait_for("message", check=check_white)

        try:
            r = re.match('[QKNBR]?[a-h]?[1-8]?x?[a-h][1-8](=[QNBR])?([+#])?|O-O|0-0|O-O-O|0-0-0', msg0.content).group(0)
            m = msg0.content.replace(r, '')

            if ' ' not in msg0.content and m == '':
                try:
                    umove = board.push_san(msg0.content) # whites move

                    global count
                    count = count + 1

                    movelist.append(f"{count}.")
                    movelist.append(msg0.content)

                    localembed.set_field_at(0, name=' '.join(movelist[-10:]), value='')

                    gensvg()
                    file = discord.File(f"db/cache/game{log}.png", filename=f"game{log}.png")

                    localembed.set_image(url=f"attachment://game{log}.png")

                    finished = check_end()
                    if finished:
                        localembed.set_field_at(0, name=' '.join(movelist[-10:]), value=f"{termin}")
                        await ctx.edit(embed=localembed, file=file)

                        globals()["stop"+str(ctx.author.id)] = False
                        globals()["stop"+str(black_player.id)] = False

                        return finished
                    else:
                        await ctx.edit(embed=localembed, file=file)
                        print(movelist)
                        return await blacksm()

                except chess.InvalidMoveError:
                    a = await ctx.respond("Invalid move!")
                    await a.delete(delay=1)
                    return await wusermoves()

                except chess.IllegalMoveError:
                    a = await ctx.respond("Illegal move!")
                    await a.delete(delay=1)
                    return await wusermoves()

                except chess.AmbiguousMoveError:
                    a = await ctx.respond("Please specify which piece youre going to move!\nThere are two or more pieces can reach that square!")
                    await a.delete(delay=1)
                    return await wusermoves()
            else:
                return await wusermoves()
        except:
            return await wusermoves()

    if black_player == client.user:
        localembed = discord.Embed(title="I am busy playing on Chess.com and Lichess! Maybe next time...")
        return await ctx.respond(embed=localembed)

    elif black_player == None: # playing with engine
        try:
            ustop = globals()["stop"+str(ctx.author.id)]
        except:
            ustop = False

        if ustop != True:
            globals()["stop"+str(ctx.author.id)] = True

            gensvg()
            file = discord.File(f"db/cache/game{log}.png", filename=f"game{log}.png")

            localembed.set_image(url=f"attachment://game{log}.png")
            localembed.set_footer(text=f"Game by {ctx.author.id}")

            await ctx.respond(embed=localembed, file=file)
            finished = await wenginemoves()

        else:
            return await ctx.respond(f"<@{ctx.author.id}>, please finish your previous game first before starting a new one!")

    else:
        try:
            ustop0 = globals()["stop"+str(ctx.author.id)]
        except:
            ustop0 = False
        try:
            ustop1 = globals()["stop"+str(black_player.id)]
        except:
            ustop1 = False

        if ustop0 != True and ustop1 != True: # both players are available
            globals()["stop"+str(ctx.author.id)] = True
            globals()["stop"+str(black_player.id)] = True

            gensvg()
            file = discord.File(f"db/cache/game{log}.png", filename=f"game{log}.png")

            localembed.set_image(url=f"attachment://game{log}.png")
            localembed.set_footer(text=f"Game by {ctx.author.id}")

            await ctx.respond(embed=localembed, file=file)
            finished = await wusermoves()

        else: # at least one of the players has an ongoing game
            if ustop0 == True:
                return await ctx.respond(f"<@{ctx.author.id}>, please finish your previous game first before starting a new one!")
            if ustop1 == True:
                return await ctx.respond(f"<@{black_player.id}> has an ongoing game! Please wait until their game is finished before starting a new one with them.")






"""
# User Profile Customization Commands
# customization = discord.commands.SlashCommandGroup("customize", "Commands used to customize the user's /profile command.")  Disable because command doesn't sync with this

@client.slash_command(
    name="profile_banner",
    description="Set a banner to display on your /profile command! (url only)"
)
@option(name="image_url", description="The url of your new profile banner (leave blank to disable)", type=str, default=None)
async def banner(ctx: ApplicationContext, image_url: str = None):
    # Set a banner to display on your /profile command! (url only)
    if (image_url is not None) and ("https://" not in image_url):
        return await ctx.respond("Your custom banner url must contain `https://`!", ephemeral=True)
    profile_metadata[str(ctx.author.id)]["profile_banner_url"] = image_url
    if image_url is None: localembed = discord.Embed(description=":white_check_mark: Your custom profile banner has been successfully removed.", color=discord.Color.green())
    else: localembed = discord.Embed(description=":white_check_mark: Your custom profile banner has been successfully set! Check it out using `/profile`.", color=discord.Color.green())
    return await ctx.respond(embed=localembed)

# User Commands
@client.user_command(name="View Profile")
async def _profile(ctx: ApplicationContext, user: discord.User):
    localembed = discord.Embed(
        title=f"{user.display_name}'s profile",
        description=f"{user.name}",
        color=discord.Color.random()
    )
    localembed.set_thumbnail(url=user.display_avatar)
    localembed.add_field(name="Profile Picture URL", value=f"[Click to view]({user.display_avatar})")
    localembed.add_field(name="Joined Discord at", value=f"{user.created_at.strftime('%d %B, %Y')}")
    localembed.add_field(name="User id", value=user.id)
    localembed.add_field(name="Rating", value=f"{str(parse_rating(user.id))} stars")
    if profile_metadata[str(user.id)]["profile_banner_url"] is not None:
        localembed.set_image(url=profile_metadata[str(user.id)]["profile_banner_url"])
    await ctx.respond(embed=localembed)

@client.user_command(name="View Rating")
async def rating(ctx: ApplicationContext, user: discord.User):
    localembed = discord.Embed(
        description=f":star: {user.name} has been rated {str(parse_rating(user.id))} stars",
        color=color
    )
    await ctx.respond(embed=localembed)

"""

# Bot Initialization
try:
    if auth_config["deploy_mode"] == "replit":
        client.run(os.getenv["TOKEN"])

    if auth_config["deploy_mode"] == "local":
        if auth_config["TOKEN"] == "":
            print("Unable to deploy client: You have not added a bot token yet. Add one first in 'TOKEN' in 'config/auth.json'.")
            print("You can get a bot token from https://discord.com/developers by creating a new application.")
            raise SystemExit

        print("[main/startup] Initializing bot client...")
        client.run(auth_config["TOKEN"])

except KeyError:
    print("Unable to deploy client: Your configuration file is likely corrupted. Please reinstall the bot.")
    raise SystemExit

except Exception as error:
    print(f"An error occured when trying to deploy the client.\nError Info:\n   {type(error).__name__}\n   {error}")
    raise SystemExit

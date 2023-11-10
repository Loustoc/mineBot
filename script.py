import discord
import os
import subprocess
import time
from io import BytesIO
from socket import *
import pycurl
import json
import platform
from discord.ext import commands
from discord import app_commands

c = pycurl.Curl()
buffer = BytesIO()

c.setopt(c.URL, "http://localhost:4040/api/tunnels")
c.setopt(c.WRITEDATA, buffer)

_os = platform.system()

intents = discord.Intents.all()
intents.message_content = True


bot = commands.Bot(
    command_prefix="/", description="This is a discord bot", intents=intents
)


async def listenPort():
    time.sleep(5)
    s = socket(AF_INET, SOCK_STREAM)
    location = ("localhost", 5500)
    try:
        c.perform()
        c.close()
    except pycurl.error:
        print(". . .")
        listenPort()
    else:
        result = buffer.getvalue().decode("iso-8859-1")
        result = json.loads(result)
        obj = result["tunnels"][0]
        while "public_url" not in dict(obj):
            listenPort()
        return result["tunnels"][0]["public_url"]


async def status():
    output = os.popen("screen -ls").read()
    if ".minecraft" in output:
        print("Server is running.")
        return True
    else:
        print("Server is not running.")
        return False


@bot.tree.command(name="start_server", description="Start server")
async def start_server(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    await interaction.followup.send("Checking server status...")
    isRunning = await status()
    if not isRunning:
        await interaction.followup.send("No server instance found, starting...")
        startNgrok = subprocess.Popen("ngrok tcp 25565 >/dev/null", shell=True)
        address = await listenPort()
        await interaction.followup.send("Sending public server url")
        address = address[slice(6, len(address))]
        await interaction.channel.send(address)
        launchserv_cmd = 'cd {} && screen -dmS "minecraft" java -Xmx1024M -Xms1024M -jar server.jar nogui'.format(
            os.getenv("SERVER_PATH")
        )
        print("launching server")
        startServ = subprocess.Popen(launchserv_cmd, shell=True)
        return
    else:
        await interaction.followup.send("Server already running !")
        return


@bot.tree.command(
    name="sync_command_tree", description="Only the owner can use this command."
)
async def sync_command_tree(interaction: discord.Interaction):
    # if interaction.author.id == os.getenv("OWNER_ID"):
    #     await bot.tree.sync()
    #     print('Command tree synced.')
    return
    # else:
    # await interaction.response.send_message('You must be the owner to use this command!')
    # return


@bot.tree.command(name="stop_server", description="Stop server")
async def stop_server(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    await interaction.followup.send("Checking server status...")
    isRunning = await status()
    if not isRunning:
        await interaction.followup.send("Le serveur n'a pas été lancé !")
        return
    else:
        await interaction.followup.send("Stopping Server...")
        os.system("screen -S minecraft -p 0 -X stuff stop`echo '\015'`")
        return


@bot.tree.command(name="testtp", description="Testing /TP")
async def save_location(interaction: discord.Interaction):
    DEV = os.getenv("DEV_MINECRAFT_USERNAME")
    await interaction.response.defer(ephemeral=True)
    await interaction.channel.send("Fetching server status...")
    isRunning = await status()
    if not isRunning:
        await interaction.followup.send("Le serveur n'a pas été lancé !")
        return
    else:
        await interaction.channel.send("Teleporting {}...".format(DEV))
        os.system(
            "screen -S minecraft -p 0 -X stuff {}`echo '\015'`".format(
                "'/tp {} 100 100 100'".format(DEV)
            )
        )
        return


@bot.tree.command(name="save_location", description="Saving Location information")
async def save_location(interaction: discord.Interaction, raccourci_gps: str):
    return


guilds = []


class Guild:
    def __init__(self, name, id, members):
        self.name = name
        self.id = id
        self.members = {"name": members.name, "role": members.role}


@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))
    try:
        synced = await bot.tree.sync()
        print(synced)
    except Exception as e:
        print(e)
    else:
        # print(bot.guilds)
        for guild in bot.guilds:
            members = []
            _member = {"name": "", "role": ""}

            def isMineRole(role):
                bool = role.name.startswith("mine:")
                return bool

            for user in guild.members:
                print(user)
                print(user.roles)
                roles = list(filter(isMineRole, user.roles))
                print(roles)
            # _guild = Guild(guild, guild.id, members)
            # guilds.append(_guild)
            print("appended guild", guild)
        print(guilds)


@bot.event
async def on_message(message):
    member = message.author
    print(member)
    guild = message.guild
    for g in guilds:
        if g.name == guild:
            for user in guild.members:
                print(user, member)
                if member == user:
                    print("user found dans la class")
                    break


bot.run(os.getenv("TOKEN"))

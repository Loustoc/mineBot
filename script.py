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
    startNgrok = subprocess.Popen("ngrok tcp 25565 >/dev/null", shell=True)
    await interaction.channel.send("Fetching server information...")
    address = await listenPort()
    address = address[slice(6, len(address))]
    await interaction.channel.send(address)
    launchserv_cmd = 'cd {} && screen -dmS "minecraft" java -Xmx1024M -Xms1024M -jar server.jar nogui'.format(
        os.getenv("SERVER_PATH")
    )
    print("launching server")
    startServ = subprocess.Popen(launchserv_cmd, shell=True)
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
    await interaction.channel.send("Fetching server status...")
    isRunning = await status()
    if not isRunning:
        await interaction.channel.send("Le serveur n'a pas été lancé !")
        return
    else:
        await interaction.channel.send("Stopping server...")
        os.system("screen -S minecraft -p 0 -X stuff stop`echo '\015'`")
        return


@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))
    try:
        synced = await bot.tree.sync()
        print(synced)
    except Exception as e:
        print(e)


bot.run(os.getenv("TOKEN"))

# Work with Python 3.6
import discord
import subprocess
import validators
import sys
import requests
import os
import importlib.util
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

TOKEN = 'NTgwMjU2MTgwNzk5MTQzOTM2.XOOEaA.2wG1z7hrPFyfk8W-MzJ3JUd7qW0'

folder_path = "1B6onBdPfAIGUjj_eEir6xP3Knjz_cCJP"
client = discord.Client()


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!pip install'):
        module = message.content.replace('!pip install', '')
        result = subprocess.run([sys.executable, "-m", "pip", "install", module], stdout=subprocess.PIPE)
        msg = ('{0.author.mention}, pip install output:\n' + result.stdout.decode('utf-8')).format(message)
        for strs in msg.split("\n"):
            await client.send_message(message.channel, strs)
        return

    if message.content.startswith("!pip freeze"):
        result = subprocess.run([sys.executable, "-m", "pip", "freeze"], stdout=subprocess.PIPE)
        msg = ('{0.author.mention}\n' + result.stdout.decode('utf-8')).format(message)
        await client.send_message(message.channel, msg)
        return

    if message.content.startswith("!import "):
        script_name, url = message.content.replace("!import ", "").split(" ")
        if validators.url(url):
            r = requests.get(url)
            with open("scripts." + script_name + ".py", "w") as f:
                f.write(r.text)
                f.close()
            await client.send_message(message.channel, "{0.author.mention} Script imported.".format(message))
        else:
            msg = '{0.author.mention} URL provided is not valid!'.format(message)
            await client.send_message(message.channel, msg)
        return

    if message.content.startswith("!backup"):
        await client.send_message(message.channel, "{0.author.mention} Starting backup process...".format(message))
        await backup(message)
        await client.send_message(message.channel, "{0.author.mention} Completed.".format(message))
        return

    if message.content.startswith("!"):
        command_name = message.content.replace("!", "", 1).split(" ")[0]
        if os.path.isfile('scripts.' + command_name + ".py"):
            spec = importlib.util.spec_from_file_location(command_name, "scripts." + command_name + ".py")
            script = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(script)
            await script.message(client, message)
        else:
            await client.send_message(message.channel, "Script not found!")


@client.event
async def on_ready():
    await recover()
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


# wrapped functions
async def recover():
    file_list = drive.ListFile({'q': "'{}' in parents and trashed=false".format(folder_path)})
    for file_download in file_list:
        for file_res in file_download:
            file_res.GetContentFile(file_res['title'])
            if file['title'].startswith('scripts.'):
                print("Script {} recovered.".format(file_res['title']))
            else:
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", "import.requirements.txt"])
                print("External modules installed.")


async def backup(message=None):
    # clean all the backup files
    file_list = drive.ListFile({'q': "'{}' in parents and trashed=false".format(folder_path)})
    for file_del in file_list:
        for file_res in file_del:
            debug_output = "Old backup {} removed".format(file_res['title'])
            if message:
                await client.send_message(message.channel, debug_output)
            else:
                print(debug_output)
            file_res.Delete()

    # re-upload them, I don't care much about network traffic.
    for fn in os.listdir("/app/"):
        if fn.startswith("scripts.") and fn.endswith(".py"):
            debug_output = "New file {} uploaded".format(fn)
            if message:
                await client.send_message(message.channel, debug_output)
            else:
                print(debug_output)
            file = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": folder_path}]})
            file.SetContentFile(fn)
            file.Upload()

    # freeze pip for recovering
    result = subprocess.run([sys.executable, "-m", "pip", "freeze"], stdout=subprocess.PIPE)
    with open("import.requirements.txt", "w") as file:
        file.write(result.stdout.decode('utf-8'))
        file.close()
    file_list = drive.ListFile({'q': "name='import.requirements.txt' and trashed=false"}).GetList()
    for file in file_list:
        file.Delete()
    file = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": folder_path}]})
    file.SetContentFile("import.requirements.txt")
    file.Upload()


gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

client.run(TOKEN)

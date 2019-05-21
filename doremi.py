# Work with Python 3.6
import discord
import subprocess
import validators
import sys
import requests
import os
import importlib

TOKEN = 'NTgwMjU2MTgwNzk5MTQzOTM2.XOOEaA.2wG1z7hrPFyfk8W-MzJ3JUd7qW0'

client = discord.Client()


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)
        return

    if message.content.startswith('!pip install'):
        module = message.content.replace('!pip install', '')
        result = subprocess.run([sys.executable, "-m", "pip", "install", module], stdout=subprocess.PIPE)
        msg = ('{0.author.mention}, pip install output:\n' + result.stdout.decode('utf-8')).format(message)
        await client.send_message(message.channel, msg)
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
            with open("\scripts\\" + script_name + ".py", "w") as f:
                f.write(r.text)
                f.close()
            await client.send_message(message.channel, "{0.author.mention} Script imported.".format(message))
            await client.send_message(message.channel, os.path.abspath("\scripts\\" + script_name + ".py"))
        else:
            msg = '{0.author.mention} URL provided is not valid!'.format(message)
            await client.send_message(message.channel, msg)
        return

    if message.content.startswith("!"):
        command_name = message.content.replace("!", "", 1).split(" ")[0]
        if os.path.isfile('\scripts\\' + command_name + ".py"):
            script = importlib.import_module("scripts."+command_name)
            await script.message(client, message)
        else:
            await client.send_message(message.channel, "Script not found!")

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


client.run(TOKEN)

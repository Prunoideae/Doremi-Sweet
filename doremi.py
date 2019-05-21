# Work with Python 3.6
import discord
import subprocess
import sys

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
	
    if message.content.startswith('!pip install'):
        module = message.content.replace('!pip install', '')
        result = subprocess.run([sys.executable, "-m", "pip", "install", module], stdout = subprocess.PIPE)
        msg = ('{0.author.mention}, pip install output:\n' + result.stdout.decode('utf-8')).format(message)
        await client.send_message(message.channel, msg)

    if message.content.startswith("!pip freeze"):
        result = subprocess.run([sys.executable, "-m", "pip", "freeze"], stdout = subprocess.PIPE)
        msg = ('{0.author.mention}\n' + result.stdout.decode('utf-8')).format(message)
        await client.send_message(message.channel, msg)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)
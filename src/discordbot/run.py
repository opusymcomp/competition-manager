# coding: utf-8
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../slackbot'))
import discord
from slackbot_settings import *

client = discord.Client()

@client.event
async def on_ready():
    channel = client.get_channel(DISCORD_CHANNEL_ID)
    await channel.send(sys.argv[1])


@client.event
async def on_message(message):
    if message.author.bot:
        await client.close()


client.run(DISCORD_TOKEN)

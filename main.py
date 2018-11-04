import discord
import asyncio
import requests
#https://canary.discordapp.com/channels/472976639651872788/473077114208256010/505767687872577547
from const import *

client = discord.Client()

true, false = True, False

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    print(message.server, '/',  message.channel, '/', message.author, 'написал', message.content)    
    if message.content.startswith('+say'):
        try:
            json = eval(message.content[4:])
        except:
            json = requests.get(message.content[4:]).json()
            #await client.send_message(message.channel, '**АШИПКА**')
        embed = discord.Embed.from_data(json)
        if 'footer' in json:
            embed.set_footer(**json['footer'])
        if 'text' in json:
            await client.send_message(message.channel, json['text'], embed=embed)
        else:
            await client.send_message(message.channel, embed=embed)
        await client.delete_message(message)
    
    if message.content.startswith('+clean'):
        async for m in client.logs_from(message.channel, limit=int(message.content.split()[-1])):
            await client.delete_message(m)

client.run(token)
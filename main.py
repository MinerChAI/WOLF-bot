import discord
import asyncio
import requests
from datetime import datetime as dt
#https://canary.discordapp.com/channels/472976639651872788/473077114208256010/505767687872577547
from const import *

client = discord.Client()

data = {}

true, false = True, False

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    with open('data.json') as df:
        try:
            data = eval(df.read())
        except SyntaxError:
            data = {}

@client.event
async def on_message(message):
    print(message.server, '/',  message.channel, '/', message.author, 'написал', message.content)  
    mutedrole = [i for i in message.server.roles if i.name == 'muted'][0]
    for server in data:
        for member in data[server]['muted']:
            for m in client.get_server(server).members:
                if m.id == member:
                    break
            else:
                continue            
            if dt.utcnow().timestamp() >= data[server]['muted'][member]:
                await client.remove_roles(m, mutedrole)
            else:
                await client.add_roles(m, mutedrole)
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
    
    if message.content.startswith('+mute'):
        time = message.content.split()[2:]
        if message.server.id not in data:
            data[message.server.id] = {'muted':{message.mentions[0].id:time_to_timestamp(time)}}
        else:
            data[message.server.id]['muted'][message.mentions[0].id] = time_to_timestamp(time)
        await client.add_roles(message.mentions[0], mutedrole)

def time_to_timestamp(a):
    ts = dt.utcnow().timestamp()
    timechars = {'s':1, 'm':60, 'h':60*60, 'd':60 * 60 * 24, 'w': 60 * 60 * 24 * 7, 'M':60 * 60 * 24 * 30, 'y':60 * 60 * 24 * 30 * 365}
    for i in a:
        n = int(i[:-1])
        c = i[-1]
        ts += n * timechars[c]
    return ts
    
client.run(token)
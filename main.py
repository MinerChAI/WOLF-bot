import discord
import asyncio
import requests
from datetime import datetime as dt
import os
from traceback import format_exc
from PIL import Image
#https://canary.discordapp.com/channels/472976639651872788/473077114208256010/505767687872577547

from const import *
from definitions import *

client = discord.Client()

origin: Image.Image = Image.open('avatar.png')
w, h = origin.size

data = {}

true, false = True, False

def send_on():
    global send
    send = True

def stop():
    root.destroy()
    client.close()
    os.abort()
    

btnSend = tk.Button(inFrame, text='Отправить', command=send_on)
btnStop = tk.Button(toolbarFrame, text='Остановить', command=stop)

btnSend.pack(side = 'right', fill = 'x')
btnStop.pack(side = 'left')

send = False

print(1)

@client.event
async def on_ready():
    print('Ready')
    outFrame.write('Logged in as')
    outFrame.write(client.user.name)
    outFrame.write(client.user.id)
    outFrame.write('OAuth2:')
    outFrame.write(discord.utils.oauth_url(client.user.id))
    outFrame.write('------')
    with open('data.json') as df:
        try:
            data = eval(df.read())
        except SyntaxError:
            data = {}

@client.event
async def on_message(message):
    outFrame.write(message.server.name + ' / ' + message.channel.name + ' (' + message.channel.id + ') / ' + message.author.display_name + ' написал: ' + message.clean_content)  
    mutedrole = [i for i in message.server.roles if i.name == 'muted'][0]
    
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
    
    if message.content.startswith('+invite'):
        embed = discord.Embed(title='Invites')
        for i in client.servers:
            embed.add_field(name=i.name, value=(await client.create_invite([j for j in i.channels if j.type == discord.ChannelType.text][0])).url)
        await client.send_message(message.channel, embed=embed)
            
    if message.content.startswith('+mute'):
        time = message.content.split()[2:]
        if message.server.id not in data:
            data[message.server.id] = {'muted':{message.mentions[0].id:time_to_timestamp(time)}}
        else:
            data[message.server.id]['muted'][message.mentions[0].id] = time_to_timestamp(time)
        await client.add_roles(message.mentions[0], mutedrole)
        await client.send_message(message.channel, message.mentions[0].mention + ' замучен до ' + datetime.strftime(dt.utcfromtimestamp(time_to_timestamp(time)), "%d.%m.%Y %H:%M:%S") + '(UTC)')
    
    if message.content.startswith('+unmute'):
        data[message.server.id]['muted'].pop(message.mentions[0].id)
        await client.send_message(message.channel, message.mentions[0].mention + ' отмучен досрочно')
    
    if message.content.startswith('+color'):
        try:
            with open(message.content.split()[1] + '.png', 'r') as f:
                await client.send_file(message.channel, f)
        except FileNotFoundError:
            color: tuple = discord.Color(int(message.content.split()[1][1:], 16)).to_tuple()
            if len(message.content.split()) == 3: transparency = int(message.content.split()[2])
            temp: Image.Image = origin.copy()
            pix = temp.load()   
            for i in range(w):
                for j in range(h):
                    print(pix[i, j])
                    r, g, b, a = pix[i, j]
                    r = (r + color[0]) / 2
                    g = (g + color[1]) / 2
                    b = (b + color[2]) / 2  
                    pix[i, j] = r, g, b, a
            await client.send_file(message.channel, temp.fp, filename = message.content.split()[1])
            temp.save(message.content.split()[1] + '.png')
            

def time_to_timestamp(a):
    ts = dt.utcnow().timestamp()
    timechars = {'s':1, 'm':60, 'h':60*60, 'd':60 * 60 * 24, 'w': 60 * 60 * 24 * 7, 'M':60 * 60 * 24 * 30, 'y':60 * 60 * 24 * 365}
    for i in a:
        n = int(i[:-1])
        c = i[-1]
        ts += n * timechars[c]
    return ts

async def bg_task():
    global send
    await client.wait_until_ready()  
    #channel = discord.Object(id='508692560873521165')
    while not client.is_closed:
        for server in data:
            mutedrole = [i for i in client.get_server(server).roles if i.name == 'muted'][0]
            for member in data[server]['muted']:
                m = client.get_server(server).get_member(member)
                if m is None:
                    continue
                if dt.utcnow().timestamp() >= data[server]['muted'][member]:
                    await client.remove_roles(m, mutedrole)
                else:
                    await client.add_roles(m, mutedrole)        
        if send:
            try:
                await client.send_message(discord.Object(id=txtBoxChnl.get()), txtBoxMsg.get())
            except discord.errors.HTTPException:
                await on_error(None)
            send = False
        try:
            root.update()
        except tk._tkinter.TclError:
            root.quit()
            break
        await asyncio.sleep(0.01)
    #    m = input()
    #    await client.send_message(channel, m)

@client.event
async def on_error(event, *args, **kwargs):
    errFrame.write(''.join(format_exc()) + '\n')
    #print(''.join(traceback.format_stack()))
client.loop.create_task(bg_task())
client.run("NTA4MzQwODQwNzc5ODc0MzA0.Dr91Gg.tPuSkVNjYmFBoA2zBr7gQs-Yeok", bot=False)
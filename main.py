import discord
import asyncio
import requests
from datetime import datetime as dt
from os import abort
from traceback import format_exc
#https://canary.discordapp.com/channels/472976639651872788/473077114208256010/505767687872577547

from const import *
#from definitions import *

client = discord.Client()

true, false = True, False

#def send_on():
    #global send
    #send = True

#def stop_on():
    #global stop
    #stop = True
    #root.destroy()
    #client.close()
    ##abort()

#async def update_data():
    ##with open('data.json', 'w') as df:
    ##    df.write(str(data))    
    ##dataFrame.clear()
    ##dataFrame.write(str(data))
    #pass



#send = False
#stop = False

data = {}

  
#btnSend = tk.Button(inFrame, text='Отправить', command=send_on)
#btnStop = tk.Button(toolbarFrame, text='Остановить', command=stop_on)

#btnSend.pack(side = 'right', fill = 'x') 
#btnStop.pack(side = 'left', fill='x')   

@client.event
async def on_ready():
    #print(2)
    global data, start
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('OAuth2:')
    print(discord.utils.oauth_url(client.user.id))
    print('------')
    #print(2.5)
    with open('data.json') as df:
        try:
            data = eval(df.read())
        except SyntaxError:
            data = {}
    #await update_data()
    client.loop.create_task(bg_task())
    

@client.event
async def on_message(message):
    global data
    print(message.server.name + ' / ' + message.channel.name + ' (' + message.channel.id + ') / ' + message.author.display_name + ' написал: ' + message.clean_content)  
    mutedrole = discord.utils.get(message.server.roles, name='muted')
    
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
        #await client.add_roles(message.mentions[0], mutedrole)
        #await update_data()
        await client.send_message(message.channel, message.mentions[0].mention + ' замучен до ' + dt.strftime(dt.fromtimestamp(time_to_timestamp(time)), "%d.%m.%Y %H:%M:%S") + '(UTC)')
    
    if message.content.startswith('+unmute'):
        data[message.server.id]['muted'].pop(message.mentions[0].id)
        #await update_data()
        await client.remove_roles(message.mentions[0], mutedrole)
        await client.send_message(message.channel, message.mentions[0].mention + ' отмучен досрочно')

def time_to_timestamp(a):
    ts = dt.utcnow().timestamp()
    timechars = {'s':1, 'm':60, 'h':60*60, 'd':60 * 60 * 24, 'w': 60 * 60 * 24 * 7, 'M':60 * 60 * 24 * 30, 'y':60 * 60 * 24 * 30 * 12}
    for i in a:
        n = int(i[:-1])
        c = i[-1]
        ts += n * timechars[c]
    return ts

async def bg_task():
    #print('started loop')
    global data
    while not client.is_closed:
        #print('in loop')
        for server in data.copy():
            mutedrole = discord.utils.get(client.get_server(server).roles, name='muted')
            for member in data[server]['muted'].copy():
                m = client.get_server(server).get_member(member)
                if m is None:
                    continue
                if dt.utcnow().timestamp() >= data[server]['muted'][member]:
                    await client.remove_roles(m, mutedrole)
                    try:
                        data.pop(member)
                    except:
                        pass
                else:
                    await client.add_roles(m, mutedrole)    
            #print('p1')
            #await update_data()
            with open('data.json', 'w') as df:
                df.write(str(data))
            #dataFrame.clear()
            #dataFrame.write(str(data))
        #print('p2')
        #if send:
            #try:
                #await client.send_message(discord.Object(id=txtBoxChnl.get()), txtBoxMsg.get())
                #txtBoxMsg.delete(0, 'end')
                #txtBoxMsg.foc_out()
            #except discord.errors.HTTPException:
                #await on_error(None)
            #send = False
        #try:
            ##print('update')
            #root.update()
        #except tk._tkinter.TclError:
            #stop_on()
        await asyncio.sleep(.01)
    #print('stopped loop')
    #    m = input()
    #    await client.send_message(channel, m)

#@client.event
#async def on_error(event, *args, **kwargs):
    ##print(''.join(format_exc()))
    #errFrame.write(''.join(format_exc()) + '\n')
client.run(token)
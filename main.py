import discord
import asyncio
import requests
from datetime import datetime as dt
import tkinter as tk
#https://canary.discordapp.com/channels/472976639651872788/473077114208256010/505767687872577547

from const import *

def send_on():
    global send
    send = True
    
class Report(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent)

        scrollbar = tk.Scrollbar(self)
        scrollbar.pack(side='right', fill='y')
        self._text = tk.Text(self, state=tk.DISABLED, *args, **kwargs)
        self._text.pack(side='left', fill='both', expand=1)

        scrollbar['command'] = self._text.yview
        self._text['yscrollcommand'] = scrollbar.set

    def write(self, text, end='\n'):
        self._text.configure(state=tk.NORMAL)
        l = list(text + end)
        for i in range(len(l)):
            if len(l[i].encode()) >= 4:
                l[i] = '\u2370'
        self._text.insert(tk.END, ''.join(l))
        self._text.configure(state=tk.DISABLED)
        self._text.yview_moveto('1.0')  # Прокрутка до конца вниз после вывода

    def clear(self):
        self._text.configure(state=tk.NORMAL)
        self._text.delete(0.0, tk.END)
        self._text.configure(state=tk.DISABLED)

    def flush(self):
        # Метод нужен для полного видимого соответствия классу StringIO в части вывода
        pass

class EntryWithPlaceholder(tk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey', **kwa):
        super().__init__(master, **kwa)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()
            
client = discord.Client()

data = {}

true, false = True, False

send = False

root = tk.Tk()
root.title('WOLF bot')

outFrame = Report(root, height = 30)
inFrame = tk.Frame(root, height = 10)

txtBox = EntryWithPlaceholder(inFrame, placeholder='Введите текст сообщения...', font = 'Arial 14', width = 70)
txtBoxChnl = EntryWithPlaceholder(inFrame, placeholder='Введите ID канала', font = 'Arial 14')
btnSend = tk.Button(inFrame, text='Отправить', command=send_on)

outFrame.pack(side = 'top', fill = 'x')
inFrame.pack(side = 'bottom', fill = 'both')
txtBox.pack(side = 'left', fill = 'x')
txtBoxChnl.pack(side = 'left', fill = 'x')
btnSend.pack(side = 'right', fill = 'x')

@client.event
async def on_ready():
    outFrame.write('Logged in as')
    outFrame.write(client.user.name)
    outFrame.write(client.user.id)
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
    for server in data:
        for member in data[server]['muted']:
            m = client.get_server(server).get_member(member)
            if m is None:
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

async def bg_task():
    global send
    await client.wait_until_ready()  
    #channel = discord.Object(id='508692560873521165')
    while not client.is_closed:
        if send:
            await client.send_message(discord.Object(id=txtBoxChnl.get()), txtBox.get())
            send = False
        try:
            root.update()
        except tk._tkinter.TclError:
            root.quit()
            break
        await asyncio.sleep(0.01)
    #    m = input()
    #    await client.send_message(channel, m)


#async def
client.loop.create_task(bg_task())
client.run(token)
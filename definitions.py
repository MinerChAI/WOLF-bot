import tkinter as tk
from os import abort
    
class Report(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent)

        scrollbar = tk.Scrollbar(self)
        scrollbar.pack(side='left', fill='y')
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

root = tk.Tk()
root.title('WOLF bot')
root.iconbitmap('WOLF.ico')
    
toolbarFrame = tk.Frame(root, height=10)
outFrame = Report(root, height = 30, fg='green')
errFrame = Report(outFrame, width = 40, fg='red')
#dataFrame = Report(outFrame, width = 40, fg='orange')
inFrame = tk.Frame(root, height = 10)
                
txtBoxMsg = EntryWithPlaceholder(inFrame, placeholder='Введите текст сообщения...', font = 'Arial 14', width = 110)
txtBoxChnl = EntryWithPlaceholder(inFrame, placeholder='Введите ID канала', font = 'Arial 14')
    
    
toolbarFrame.pack(side='top', fill='x')            
outFrame.pack(side = 'top', fill = 'x')
errFrame.pack(side='right', fill='y')
#dataFrame.pack(side='right', fill='y')
inFrame.pack(side = 'bottom', fill = 'both')
txtBoxMsg.pack(side = 'left', fill = 'x')
txtBoxChnl.pack(side = 'left', fill = 'x')  
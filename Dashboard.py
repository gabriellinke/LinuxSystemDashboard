from tkinter import *
import threading
import time
from datetime import datetime
from ReadFile import read_key
TOP_BG_COLOR = '#1b2838'
BODY_BG_COLOR='#2a475e'
TEXT_COLOR='#FFFFFF'

print(datetime.now().strftime('%A, %d %B %Y\n'))
print("LOADING, PLEASE WAIT...\n")

# CREATE WINDOW - RESIZE FALSE - SIZE - TITLE CARD
root = Tk()
root.resizable(False, False)
root.geometry('1280x720')
root.title("Dashboard")
root.configure(bg='#c7d5e0')

uptime = StringVar()
uptime.set('0')

# DRAW TOP BLUE BAR - DRAW TITLE - DRAW DATETIME
top_bg = Canvas(root, bg=TOP_BG_COLOR, highlightthickness=0).place(x=0, y=0, width=1280, height=60)
Label(top_bg, text='Dashboard', font='Montserrat 25', bg=TOP_BG_COLOR, fg='white').place(x=15, y=3)
Label(top_bg, text=datetime.now().strftime('%A, %d %B %Y'), font='Montserrat 20', bg=TOP_BG_COLOR, fg='white').place(
    x=820, y=8)

# Sistema (hardware e SO)
system_box = Canvas(root, width=400, height=600, bg=BODY_BG_COLOR, highlightthickness=0).place(x=20, y=100)
system_box_top = Canvas(root, width=400, height=20, bg=TOP_BG_COLOR, highlightthickness=0).place(x=20, y=80)
Label(system_box, textvariable=uptime, font='Montserrat 25', bg=TOP_BG_COLOR, fg='white').place(x=25, y=105)
Label(system_box_top, text='Sistema (hardware e SO)', font='Montserrat 7 bold', bg=TOP_BG_COLOR,
         fg=TEXT_COLOR).place(x=25, y=82)

# Processos/Threads
process_box = Canvas(root, width=400, height=280, bg=BODY_BG_COLOR, highlightthickness=0).place(x=440, y=100)
process_box_top = Canvas(root, width=400, height=20, bg=TOP_BG_COLOR, highlightthickness=0).place(x=440, y=80)
Label(process_box_top, text='Processos/Threads', font='Montserrat 7 bold', bg=TOP_BG_COLOR,
         fg=TEXT_COLOR).place(x=445, y=82)

# Sistema de Arquivo
filesystem_box = Canvas(root, width=400, height=280, bg=BODY_BG_COLOR, highlightthickness=0).place(x=440, y=420)
filesystem_box_top = Canvas(root, width=400, height=20, bg=TOP_BG_COLOR, highlightthickness=0).place(x=440, y=400)
Label(filesystem_box_top, text='Sistema de Arquivo', font='Montserrat 7 bold', bg=TOP_BG_COLOR,
         fg=TEXT_COLOR).place(x=445, y=402)

# Memória
memory_box = Canvas(root, width=400, height=280, bg=BODY_BG_COLOR, highlightthickness=0).place(x=860, y=100)
memory_box_top = Canvas(root, width=400, height=20, bg=TOP_BG_COLOR, highlightthickness=0).place(x=860, y=80)
Label(memory_box_top, text='Memória', font='Montserrat 7 bold', bg=TOP_BG_COLOR,
         fg=TEXT_COLOR).place(x=865, y=82)

# Terminal
terminal_box = Canvas(root, width=400, height=280, bg=BODY_BG_COLOR, highlightthickness=0).place(x=860, y=420)
terminal_box_top = Canvas(root, width=400, height=20, bg=TOP_BG_COLOR, highlightthickness=0).place(x=860, y=400)
Label(terminal_box_top, text='Terminal', font='Montserrat 7 bold', bg=TOP_BG_COLOR,
         fg=TEXT_COLOR).place(x=865, y=402)

print('\nDRAWING DASHBOARD')
# MAINLOOP

while(1):
    # time.sleep(1)
    uptime.set(read_key())
    root.update_idletasks()

# Documentações úteis:
# https://dash.plotly.com/live-updates
# https://dash.plotly.com/external-resources
import datetime

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly
import threading
import time
import os

uptime = ""
meminfo = ""
command = ""

def update_uptime():
    while(1):
        global uptime
        with open('/proc/uptime' , 'r') as live_key_file_loc:
            live_token = live_key_file_loc.read()
        uptime = (live_token.split(' ')[0])
        time.sleep(1)

def update_memory_info():
    while(1):
        global meminfo
        with open('/proc/meminfo' , 'r') as live_key_file_loc:
            live_token = live_key_file_loc.read()
        meminfo = live_token
        time.sleep(1)

def run_command():
    while(1):
        global command
        command = os.popen('ls /proc').read()
        time.sleep(1)

uptimeThread = threading.Thread(target=update_uptime)
uptimeThread.start()
meminfoThread = threading.Thread(target=update_memory_info)
meminfoThread.start()
commandThread = threading.Thread(target=run_command)
commandThread.start()

app = dash.Dash(__name__)
app.layout = html.Div(
    html.Div([
        html.H1('Dashboard', id='title'),
        html.Tbody(id='main-container'),
        dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        )
    ])
)

@app.callback(Output('main-container', 'children'),
              Input('interval-component', 'n_intervals'))
def update_metrics(n):
    return [
        html.Div([
            html.Div('Uptime: '+uptime, className='info-container'),
            html.Div('Uptime: '+uptime, className='info-container')
        ]),
        html.Div([
            html.Div('Meminfo: '+meminfo, className='info-container'),
            html.Div('Meminfo: '+meminfo, className='info-container')
        ]),
        html.Div([
            html.Div('Comando: '+command, className='info-container'),
            html.Div('Comando: '+command, className='info-container')
        ])
    ]

if __name__ == '__main__':
    app.run_server(debug=True)
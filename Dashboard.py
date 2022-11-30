# Documentações úteis:
# https://dash.plotly.com/live-updates
# https://dash.plotly.com/external-resources
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly
import threading
import time
import os
import plotly.express as px
import plotly.graph_objects as go

meminfo = ""
command = ""
memory = {}

def update_memory_info():
    global meminfo
    global memory
    while(1):
        with open('/proc/meminfo' , 'r') as live_key_file_loc:
            live_token = live_key_file_loc.read()
        meminfo = live_token
        memory["total"] = int(os.popen('free -m  | grep ^Mem | tr -s \' \' | cut -d \' \' -f2').read())
        memory["used"] = int(os.popen('free -m  | grep ^Mem | tr -s \' \' | cut -d \' \' -f3').read())
        memory["free"] = int(os.popen('free -m  | grep ^Mem | tr -s \' \' | cut -d \' \' -f4').read())
        memory["cache"] = int(os.popen('free -m  | grep ^Mem | tr -s \' \' | cut -d \' \' -f6').read())
        time.sleep(1)

def run_command():
    global command
    while(1):
        command = os.popen('ls /proc').read()
        time.sleep(1)

meminfoThread = threading.Thread(target=update_memory_info)
meminfoThread.start()
commandThread = threading.Thread(target=run_command)
commandThread.start()

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.layout = html.Div(
    html.Div([
        html.H1('Dashboard', id='title'),
        html.Tbody(id='main-container'),
        dcc.Interval(
            id='interval-component',
            interval=1*3000, # in milliseconds
            n_intervals=0
        )
    ])
)

def get_memory_info_container():
    return html.Div([
        html.Div(f'Memória total: {memory["total"]:.1f} MB'),
        html.Div(f'Memória livre: {memory["free"]:.1f} MB'),
        html.Div(f'Memória utilizada: {memory["used"]:.1f} MB'),
        html.Div(f'Memória cache/buffer: {memory["cache"]:.1f} MB'),
        dcc.Graph(id="graph"),
    ], className='info-container')

@app.callback(Output('main-container', 'children'),
              Input('interval-component', 'n_intervals'))
def update_info(n):
    return [
        html.Div([
            html.Div('Processos:', className='info-container-long')
        ]),
        html.Div([
            html.Div(command, className='info-container'),
            html.Div('Meminfo: '+meminfo, className='info-container')
        ]),
        html.Div([
            get_memory_info_container(),
            html.Div('Informações de hardware e sistema', className='info-container')
        ])
    ]


@app.callback(Output('graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def generate_chart(n):
    labels = ['Memória livre','Memória utilizada', 'Memória cache/buffer']
    values = [memory["free"], memory["used"], memory['cache']]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig.update_layout(
        autosize=False,
        height=300,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=50,
            pad=0
        ),
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
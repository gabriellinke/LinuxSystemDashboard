# Documentações úteis:
# https://dash.plotly.com/live-updates
# https://dash.plotly.com/external-resources
# https://www.tecmint.com/commands-to-collect-system-and-hardware-information-in-linux/#:~:text=How%20to%20View%20Linux%20System,kernel%20name%20of%20your%20system.&text=To%20view%20your%20network%20hostname,the%20uname%20command%20as%20shown.
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
top = ""
hardware_info = {}
system_info = {}
memory = {}
swap = {}

# date
# lsusb
# sysinfo - uptime e loadavg - acho que já temos essas infos do top
# Uso de disco - df -> fazer gŕafico com percentual usado de cada disco - qual o disco, se é HD ou SSD

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
        swap["total"] = int(os.popen('free -m  | grep ^Swap | tr -s \' \' | cut -d \' \' -f2').read())
        swap["used"] = int(os.popen('free -m  | grep ^Swap | tr -s \' \' | cut -d \' \' -f3').read())
        swap["free"] = int(os.popen('free -m  | grep ^Swap | tr -s \' \' | cut -d \' \' -f4').read())
        time.sleep(1)

def run_command():
    global command
    while(1):
        command = os.popen('ls /proc').read()
        time.sleep(1)

def run_top():
    global top
    while(1):
        top = os.popen('top -b -n 1 > top_out.txt && cat top_out.txt').read()
        time.sleep(1.5)
        # sed '2q;d' top_out.txt - pega a linha 2 do top

def get_hardware_info():
    global hardware_info
    hardware_info["memory"] = os.popen('lshw -short | grep memory | tr -s \' \' | cut -d \' \' -f3- | sed \'1q;d\'').read()
    hardware_info["processor"] = os.popen('lshw -short | grep processor | tr -s \' \' | cut -d \' \' -f3- | sed \'1q;d\'').read()
    hardware_info["graphic"] = os.popen('lshw -short | grep display | tr -s \' \' | cut -d \' \' -f3- | sed \'1q;d\'').read()

def get_system_info():
    global system_info
    system_info["kernel-name"] = os.popen('uname -s').read()
    system_info["nodename"] = os.popen('uname -n').read()
    system_info["kernel-release"] = os.popen('uname -r').read()
    system_info["kernel-version"] = os.popen('uname -v').read()
    system_info["machine"] = os.popen('uname -m').read()
    system_info["processor"] = os.popen('uname -p').read()
    system_info["hardware-platform"] = os.popen('uname -i').read()
    system_info["operating-system"] = os.popen('uname -o').read()

meminfoThread = threading.Thread(target=update_memory_info)
meminfoThread.start()
commandThread = threading.Thread(target=run_command)
commandThread.start()
topThread = threading.Thread(target=run_top)
topThread.start()
get_hardware_info()
get_system_info()

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.layout = html.Div(
    html.Div([
        html.H1('Dashboard', id='title'),
        html.Tbody(id='main-container'),
        dcc.Interval(
            id='interval-component',
            interval=3*1000, # in milliseconds
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
        html.Div(f'Swap total: {swap["total"]:.1f} MB'),
        html.Div(f'Swap livre: {swap["free"]:.1f} MB'),
        html.Div(f'Swap utilizado: {swap["used"]:.1f} MB'),
        dcc.Graph(id="graph"),
    ], className='info-container')

def get_hardware_and_system_info_container():
    return html.Div([
        html.H3('Informações de hardware e sistema', className='info-container-title'),
        html.H4('Hardware', className='info-container-subtitle'),
        html.Div(f'Memória RAM: {hardware_info["memory"]}'),
        html.Div(f'Processador: {hardware_info["processor"]}'),
        html.Div(f'Placa de vídeo: {hardware_info["graphic"]}'),
        html.H4('Sistema', className='info-container-subtitle', style={'marginTop': '12px'}),
        html.Div(f'Nome do kernel: {system_info["kernel-name"]}'),
        html.Div(f'Nome do nó da máquina na rede: {system_info["nodename"]}'),
        html.Div(f'Versão de lançamento do Kernel: {system_info["kernel-release"]}'),
        html.Div(f'Data de criação do Kernel: {system_info["kernel-version"]}'),
        html.Div(f'Sistema operacional: {system_info["operating-system"]}'),
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
            html.Div(top, className='info-container')
        ]),
        html.Div([
            get_memory_info_container(),
            get_hardware_and_system_info_container(),
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
            t=30,
            pad=0
        ),
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
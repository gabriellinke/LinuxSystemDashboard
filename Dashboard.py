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
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

ps_aux = ""
hardware_info = {}
disk_info = []
partitions = []
system_info = {}
memory = {}
swap = {}
connected_usbs = []

# date
# lsusb
# sysinfo - uptime e loadavg - acho que já temos essas infos do top
# Uso de disco - df -> fazer gŕafico com percentual usado de cada disco - qual o disco, se é HD ou SSD
# Para saber se é SSD ou HD: 'cat /sys/block/sda/queue/rotational' ou 'lsblk -d -o name,rota'
# lsblk -d -o name,rota | grep -v loop
# df -h | grep sda
# df -h | grep `lsblk -d -o name | grep -v loop | sed '2q;d'`

def update_memory_info():
    global memory
    global swap
    while(1):
        memory["total"] = int(os.popen('free -m  | grep ^Mem | tr -s \' \' | cut -d \' \' -f2').read())
        memory["used"] = int(os.popen('free -m  | grep ^Mem | tr -s \' \' | cut -d \' \' -f3').read())
        memory["free"] = int(os.popen('free -m  | grep ^Mem | tr -s \' \' | cut -d \' \' -f4').read())
        memory["cache"] = int(os.popen('free -m  | grep ^Mem | tr -s \' \' | cut -d \' \' -f6').read())
        swap["total"] = int(os.popen('free -m  | grep ^Swap | tr -s \' \' | cut -d \' \' -f2').read())
        swap["used"] = int(os.popen('free -m  | grep ^Swap | tr -s \' \' | cut -d \' \' -f3').read())
        swap["free"] = int(os.popen('free -m  | grep ^Swap | tr -s \' \' | cut -d \' \' -f4').read())
        time.sleep(1)

def update_usb_info():
    global connected_usbs
    while(1):
        connected_usbs = os.popen('lsusb').read().split('\n')
        connected_usbs.pop(len(connected_usbs)-1)
        time.sleep(1)

def run_ps_aux():
    global ps_aux
    while(1):
        ps_aux = os.popen('ps aux --sort=-pcpu').read()
        time.sleep(1)

def get_hardware_info():
    global hardware_info
    hardware_info["memory"] = os.popen('lshw -short | grep memory | tr -s \' \' | cut -d \' \' -f3- | sed \'1q;d\'').read()
    hardware_info["processor"] = os.popen('lshw -short | grep processor | tr -s \' \' | cut -d \' \' -f3- | sed \'1q;d\'').read()
    hardware_info["graphic"] = os.popen('lshw -short | grep display | tr -s \' \' | cut -d \' \' -f3- | sed \'1q;d\'').read()

def get_partition_info_human_readable(partition):
    part_size = partition["size"]
    if(int(part_size) > 1024*1024):
        partition["size_h"] = f'{int(part_size)/(1024*1024):.1f}G'
    elif(int(part_size) > 1024):
        partition["size_h"] = f'{int(part_size)/(1024):.1f}M'
    else:
        partition["size_h"] = f'{int(part_size):.1f}K'

    part_used = partition["used"]
    if(int(part_used) > 1024*1024):
        partition["used_h"] = f'{int(part_used)/(1024*1024):.1f}G'
    elif(int(part_used) > 1024):
        partition["used_h"] = f'{int(part_used)/(1024):.1f}M'
    else:
        partition["used_h"] = f'{int(part_used):.1f}K'

    part_available = partition["available"]
    if(int(part_available) > 1024*1024):
        partition["available_h"] = f'{int(part_available)/(1024*1024):.1f}G'
    elif(int(part_available) > 1024):
        partition["available_h"] = f'{int(part_available)/(1024):.1f}M'
    else:
        partition["available_h"] = f'{int(part_available):.1f}K'

def get_disk_info():
    global disk_info
    global partitions
    disks = os.popen('lsblk -d -o name,rota,size | grep -v loop').read().split('\n')
    disks.pop(0)
    disks.pop(len(disks)-1)
    for disk in disks:
        name = re.sub('\s+',' ', disk).split(' ')[0]
        if(re.sub('\s+',' ', disk).split(' ')[1] == '1'):
            disk_type = 'HD'
        else:
            disk_type = 'SSD'
        disk_size = re.sub('\s+',' ', disk).split(' ')[2]
        aux_disk = {}
        aux_disk["name"] = name
        aux_disk["type"] = disk_type
        aux_disk["size"] = disk_size
        aux_disk["partitions"] = []

        diskInfo = os.popen(f'df | grep {name}').read().split('\n')
        diskInfo.pop(len(diskInfo)-1)
        for part in diskInfo:
            part_name = re.sub('\s+',' ', part).split(' ')[0]
            part_size = re.sub('\s+',' ', part).split(' ')[1]
            part_used = re.sub('\s+',' ', part).split(' ')[2]
            part_available = re.sub('\s+',' ', part).split(' ')[3]
            part_percentage = re.sub('\s+',' ', part).split(' ')[4]
            part_mount_point = re.sub('\s+',' ', part).split(' ')[5]
            partition = {}
            
            partition["name"] = part_name
            partition["size"] = part_size
            partition["used"] = part_used
            partition["available"] = part_available
            partition["percentage"] = part_percentage
            partition["mount_point"] = part_mount_point
            get_partition_info_human_readable(partition)

            aux_disk["partitions"].append(partition)
            partitions.append(partition)
        disk_info.append(aux_disk)

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
usbThread = threading.Thread(target=update_usb_info)
usbThread.start()
ps_auxThread = threading.Thread(target=run_ps_aux)
ps_auxThread.start()
get_hardware_info()
get_system_info()
get_disk_info()

def get_proccess_container():
    global ps_aux
    proccesses = ps_aux.split('\n')
    proccesses_list = []
    for proc in proccesses:
        text = re.sub('\s+',' ', proc).split(' ')
        if(len(text) > 1):
            proccesses_list.append(html.Div([
                html.Div(f'{text[0]}', className='proccess-container'),
                html.Div(f'{text[1]}', className='proccess-container'),
                html.Div(f'{text[2]}', className='proccess-container'),
                html.Div(f'{text[3]}', className='proccess-container'),
                html.Div(f'{text[7]}', className='proccess-container'),
                html.Div(f'{text[8]}', className='proccess-container'),
                html.Div(f'{text[9]}', className='proccess-container'),
            ], className='proccess-container-row'))
    return [
        html.Div(proccesses_list),
    ]

def get_memory_info_container():
    return [
        html.Div(f'Memória total: {memory["total"]:.1f} MB'),
        html.Div(f'Memória livre: {memory["free"]:.1f} MB'),
        html.Div(f'Memória utilizada: {memory["used"]:.1f} MB'),
        html.Div(f'Memória cache/buffer: {memory["cache"]:.1f} MB'),
        html.Div(f'Swap total: {swap["total"]:.1f} MB'),
        html.Div(f'Swap livre: {swap["free"]:.1f} MB'),
        html.Div(f'Swap utilizado: {swap["used"]:.1f} MB'),
    ]

def get_disk_info_container():
    global disk_info
    disk_list = []
    for disk in disk_info:
        disk_partitions = []
        for partition in disk["partitions"]:
            disk_partitions.append(html.Div([
                html.Div([
                    html.Div('Partição', className='partition-container-title'),
                    html.Div(f'{partition["name"]}', className='partition-container-value'),
                ], className='partition-container'),
                html.Div([
                    html.Div('Tamanho', className='partition-container-title'),
                    html.Div(f'{partition["size_h"]}', className='partition-container-value'),
                ], className='partition-container'),
                html.Div([
                    html.Div('Usado', className='partition-container-title'),
                    html.Div(f'{partition["used_h"]}', className='partition-container-value'),
                ], className='partition-container'),
                html.Div([
                    html.Div('Disponível', className='partition-container-title'),
                    html.Div(f'{partition["available_h"]}', className='partition-container-value'),
                ], className='partition-container'),
                html.Div([
                    html.Div('Uso', className='partition-container-title'),
                    html.Div(f'{partition["percentage"]}', className='partition-container-value'),
                ], className='partition-container'),
                html.Div([
                    html.Div('Montado em', className='partition-container-title'),
                    html.Div(f'{partition["mount_point"]}', className='partition-container-value'),
                ], className='partition-container'),
            ], className='partition-container-row'))
        disk_list.append(html.Div([
            html.H3(f'Disco {disk["name"]} ({disk["type"]}) - {disk["size"]}'),
            html.Div(disk_partitions),
        ]))

        # Pega os dados para o gráfico
        names = []
        types = []
        percentages = []
        for partition in partitions:
            names.append(partition["name"])
            names.append(partition["name"])
            types.append('usado')
            types.append('disponível')
            percentage = re.match(r'\d+', partition["percentage"])
            percentages.append(int(percentage[0]))
            percentages.append(100 - int(percentage[0]))

        # Cria o gráfico
        d = {'Partição': names, 'Tipo': types, 'Porcentagem': percentages}
        df = pd.DataFrame(data=d)
        fig = px.bar(df, x="Porcentagem", y="Partição", color="Tipo", title="Uso das partições")
        fig.update_xaxes(nticks=50, range=(0, 100),)
        fig.update_layout(
            autosize=False,
            height=200,
            margin=dict(
                l=0,
                r=0,
                b=0,
                t=25,
                pad=0
            ),
        )

    return html.Div([
        html.Div(disk_list),
        dcc.Graph(id="disk-graph", figure=fig),
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

def get_usb_info_container():
    usbs_list = []
    for usb in connected_usbs:
        usbs_list.append(html.Div(f'{usb}'))
    return [
        html.H3('Dispositivos conectados nos barramentos USB', className='info-container-title'),
        html.Div(usbs_list)
    ]

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.layout = html.Div(
    html.Div([
        html.H1('Dashboard', id='title'),
        html.Tbody([
            html.Div([
                html.Div([
                    html.H3('Processos', className='info-container-title'),
                    html.Div(id='proccess-container')
                ], className='info-container-long')
            ]),
            html.Div([
                get_disk_info_container(),
                html.Div(className='info-container', id='usb-container')
            ]),
            html.Div([
                html.Div([
                    html.Div(id='memory-info-container'),
                    dcc.Graph(id="graph"),
                ], className='info-container'),
                get_hardware_and_system_info_container(),
            ]),
            html.Div([html.Button('>_', id='terminal-button', n_clicks=0)], className='floating_button')
        ], id='main-container'),
        dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        ),
        html.Div(id='hidden-div', style={'display':'none'}),
    ])
)


@app.callback(Output('usb-container', 'children'),
              Input('interval-component', 'n_intervals'))
def update_info(n):
    return get_usb_info_container()

@app.callback(Output('memory-info-container', 'children'),
              Input('interval-component', 'n_intervals'))
def update_info(n):
    return get_memory_info_container()

@app.callback(Output('proccess-container', 'children'),
              Input('interval-component', 'n_intervals'))
def update_info(n):
    return get_proccess_container()

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

@app.callback(
    Output('hidden-div', 'children'),
    Input('terminal-button', 'n_clicks'))
def openTerminal(btn1):
    if(btn1 > 0):
        os.popen('cd && gnome-terminal')
    return None

app.run_server(debug=False)
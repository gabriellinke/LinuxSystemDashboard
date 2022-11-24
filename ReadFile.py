import schedule
import time

def read_key():
    with open('/proc/uptime' , 'r') as live_key_file_loc:
        live_token = live_key_file_loc.read()
    
    print(live_token.split(' ')[0])
    return (live_token.split(' ')[0])
    # time.sleep(5)
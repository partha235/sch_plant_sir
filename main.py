import network
import machine
import utime
from utime import sleep_ms,sleep
import time
from dht import DHT11
from machine import ADC,Pin
import socket
import onewire
import ds18x20

import esp
esp.osdebug(None)

import gc
gc.collect()

# WiFi settings
WIFI_SSID = "plant_dr"
WIFI_PASSWORD = "plant123"

# Pin connections
ds_pin = machine.Pin(15)
dhp=Pin(16)

x=Pin(33,Pin.IN,Pin.PULL_UP)
xa=ADC(x)
dht_sensor=DHT11(dhp)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

roms = ds_sensor.scan()
print('Found DS devices: ', roms)


ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=WIFI_SSID, password=WIFI_PASSWORD)
while ap.active() == False:
    pass

print('Connection successful')
print(ap.ifconfig())

def web_page():
    html = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="refresh" content="0.1">
    <h1>Plant Monitor</h1>
    <p>Temperature:  C</p><span class="sensor">""" + str(dt)  + """  c</span></td></tr>
    <p>Humidity:  </p><span class="sensor">""" + str(dh)  + """%</span></td></tr>
    <p>Water Level in plant: </p><span class="sensor">""" + str(wl)  + """%</span></td></tr>
    <p>Soil Temperature: </p><span class="sensor">""" + str(st)  + """c</span></td></tr>
    </body></html>"""
    return html

s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)



while True:
    if gc.mem_free() < 102000:
        gc.collect()
    global dt,dh,st,wl
    # print("wl=  ",water_level_sensor.read())
    w=xa.read_u16()
    wl=((65535-w)/65535)*100
    try:
        sleep(2)
        dht_sensor.measure()
        dt=dht_sensor.temperature()
        dh=dht_sensor.humidity()
    except OSError as e:
        dt=34
        dh=0
    ds_sensor.convert_temp()
    time.sleep_ms(750)
    for rom in roms:
        print(ds_sensor.read_temp(rom))
        # return ds_sensor.read_temp(rom)
    st=ds_sensor.read_temp(rom)


    conn, addr = s.accept()
    conn.settimeout(3.0)
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    conn.settimeout(None)
    request = str(request)
    print('Content = %s' % request)
    print("HI")
    sleep_ms(200)
    response = web_page()
    conn.send('HTTPS/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()

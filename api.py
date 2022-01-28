import asyncio
import logging
import time
import paho.mqtt.client as mqtt

import sanic

__author__ = 'Hankier'
__version__ = '0.0.1'
__codename__ = 'Pilot Pirate'



HOST = '0.0.0.0'
PORT = 8997

MQTT_HOST = '192.168.50.5'
MQTT_PORT = 1996

APP = sanic.Sanic('hqrm')
MQTT = mqtt.Client(client_id="API_HQR")
MQTT.connect(MQTT_HOST, MQTT_PORT, 60)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))



START_TIME = time.time()

logging.basicConfig(
            format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s',
                level=logging.DEBUG
                )

LOGGER = logging.getLogger('mb')


def get_display_time(seconds, granularity=2):
    """ Return pretty printed time delta given in seconds. """
    intervals = (
        ('weeks', 604800),  # 60 * 60 * 24 * 7
        ('days', 86400),    # 60 * 60 * 24
        ('hours', 3600),    # 60 * 60
        ('minutes', 60),
        ('seconds', 1),
    )
    result = []
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i+lv//3], 16) for i in range(0, lv, lv//3))

def setOff():
    print('Publish topic to MQTT')
    msg = '{"color_mode":"rgbw","state":"OFF","brightness":0,"color_brightness":0,"color":{"r":0,"g":0,"b":0,"w":0},"white_value":0}'
    topic = 'led01/light/led_bed/command'
    pub = MQTT.publish(topic, msg)
    print(f'Got: {pub.rc}')

def setWhite(bright: int):
    print('Publish topic to MQTT')
    msg = '{"color_mode":"rgbw","state":"ON","brightness":' + str(bright) + ',"color_brightness":100,"color":{"r":0,"g":0,"b":0,"w":0},"white_value":200}'
    topic = 'led01/light/led_bed/command'
    pub = MQTT.publish(topic, msg)
    print(f'Got: {pub.rc}')

@APP.route('/white/<bright:int>')
async def setWhiteLevel(request: sanic.request.Request, 
                        bright: int) -> sanic.response.HTTPResponse:
    print(f'White lvl set to {bright}')
    setWhite(bright)
    return sanic.response.text(f'White lvl set to {bright}')

@APP.route('/rgb')
async def setRGB(request: sanic.request.Request) -> sanic.response.HTTPResponse:
   print(f'Request on /rgb')
   color = request.args.get('color')
   brightness = request.args.get('brightness')
   return sanic.response.text(f'Color set to {color} / {brightness}')

@APP.route('/off')
async def setLedOff(request: sanic.request.Request) -> sanic.response.HTTPResponse:
   print('Leds off')
   setOff()
   return sanic.response.text('Leds off.')

@APP.route('/')
async def home(request: sanic.request.Request) -> sanic.response.HTTPResponse:
    """ Return some cool text info about an app. """
    return sanic.response.text('\n'.join([
'  __________      '        + '',
' / ___  ___ \\    '        + '',
'/ / @ \\/ @ \\ \\   '        + f'  HeadquarterManager v{__version__} [{__codename__}]',
'\\ \\___/\\___/ /\\  '        + '',
' \\____\\/____/||   '        + '',
' /     /\\\\\\\\\\//   '        + f'  > Author:  {__author__}',
'|     |\\\\\\\\\\\\     '        + '',
' \\      \\\\\\\\\\\\    '        + '',
'   \\______/\\\\\\\\   '        + '',
'    _||_||_           '    + f'  Uptime: {get_display_time(time.time() - START_TIME, 6)}',
''
]))

@APP.listener('before_server_start')
async def setup(app, loop):
    """ Initialzie sanic APP before server start. """
    print('Setup MQTT')
    print('Setup MQTT - DONE')


def main(host: str, port: int) -> None:
    """ MacroBalancer entrypoint. """
    APP.run(host=host, port=port, backlog=8192)

if __name__ == '__main__':
    main(host=HOST, port=PORT)

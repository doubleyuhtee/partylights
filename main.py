import time
from flask import Flask, send_file
import threading
import random
import requests
import json
import argparse


app = Flask(__name__)


class LightRunner(threading.Thread):
    def __init__(self, key, *args, **kwargs):
        super(LightRunner, self).__init__(*args, **kwargs)
        print(key)
        self.api_key = key
        self._stop = threading.Event()
        self.speed = 3

    def unstop(self):
        self._stop.clear()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def speed_up(self):
        self.speed = self.speed - .5
        if self.speed < 1:
            self.speed = 1

    def speed_down(self):
        self.speed = self.speed + .5
        if self.speed > 30:
            self.speed = 30

    def _update_lights(self, group, hue, sat, bri):
        body = {"on": True, "sat": sat, "bri": bri, "hue": hue}
        x = requests.put(
            f"http://192.168.1.155/api/{self.api_key}/groups/{group}/action",
            data=json.dumps(body))

    def run(self):
        print("What the cheezus is going on?")
        current = 3
        while True:
            if self.stopped():
                print("Party's over")
                self._update_lights(current, 7676, 199, 144)
                return
            self._update_lights(current, random.randint(0, 65535), random.randint(0, 255), random.randint(0, 255))
            time.sleep(self.speed)


light_thread = None


@app.route('/')
def get_index():
    return send_file('web/index.html')


@app.route('/start')
def start_lights():
    light_thread.unstop()
    light_thread.run()
    return ""


@app.route('/stop')
def stop_lights():
    print("stopping lights!")
    light_thread.stop()
    return ""


@app.route('/fast')
def speed_up():
    light_thread.speed_up()
    return ""

@app.route('/slow')
def speed_down():
    light_thread.speed_down()
    return ""


argument_parser = argparse.ArgumentParser(description="Bring the party to your lights")
argument_parser.add_argument("--key", "-k", action='store',
                             help="Api Key", required=True)


if __name__ == '__main__':
    print(argument_parser.parse_args())
    light_thread = LightRunner(argument_parser.parse_args().key)
    light_thread.stop()
    app.run(host='0.0.0.0')

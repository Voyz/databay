import json
import os
from datetime import timedelta
from typing import List

from databay import Record, Link
from databay.outlets import PrintOutlet
from databay.planners import APSPlanner

from databay.inlet import Inlet
import urllib.request


class WeatherInlet(Inlet):
    def __init__(self, api_key:str, city_name:str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.api_key = api_key
        self.city_name = city_name

    def pull(self, update) -> List[Record]:
        url = f'https://api.openweathermap.org/data/2.5/weather?' \
              f'q={self.city_name}&' \
              f'appid={self.api_key}'

        contents = urllib.request.urlopen(url).read().decode('utf8')

        formatted = json.loads(contents)
        return formatted['weather'][0]['description']


api_key = os.environ.get('OPEN_WEATHER_MAP_API_KEY')
weather_inlet = WeatherInlet(api_key, 'Bangkok')

link = Link(weather_inlet, PrintOutlet(only_payload=True),
            interval=timedelta(seconds=2), name='bangkok_weather')

planner = APSPlanner()
planner.add_link(link)
planner.start()
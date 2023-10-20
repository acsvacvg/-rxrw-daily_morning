from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random
import json
from requests.packages import urllib3


today = datetime.now()
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_id = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]

from datetime import date, datetime

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)

def get_weather():
  url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city
  res = requests.get(url).json()
  weather = res['data']['list'][0]
  return weather['weather'], math.floor(weather['low'])

def get_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

def get_birthday():
  next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days

def get_words():
  words = requests.get("https://api.shadiao.pro/chp")
  if words.status_code != 200:
    return get_words()
  return words.json()['data']['text']

def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)

// 获取星座
def get_lucky():
  url = "http://web.juhe.cn:8080/constellation/getAll?consName=金牛座&type=today&key=4a11bbcbf089edaf14c2d9bdb80c2ec4"
  res = requests.get(url).json()
  return res['color'],res['summary']

// 新闻
def get_info():
  url = "http://v.juhe.cn/toutiao/index?type=yule&key=d268884b9b07c0eb9d6093dc54116018"
  res = requests.get(url).json()['result']
  info = res['data'][0]['title']
  return info

// 获取历史上的今天
def get_history():
  url = "https://api.oick.cn/lishi/api.php"
  res= requests.get(url).json()
  history = res['result'][0]
  return history['date'],history['title']

client = WeChatClient(app_id, app_secret)
today_date = json.dumps(date.today(), cls=ComplexEncoder)

wm = WeChatMessage(client)
wea, temperature = get_weather()
color,summary = get_lucky()
date,title = get_history()
info = get_info()

data = {"city":{"value":city}, "date":{"value":today_date, "color":get_random_color()}, "weather":{"value":wea, "color":get_random_color()},
        "temperature":{"value":(str(temperature) + "℃"), "color":get_random_color()},
        "love_days":{"value":get_count(), "color":get_random_color()},"birthday_left":{"value":get_birthday(), "color":get_random_color()},
        "words":{"value":get_words(), "color":get_random_color()}, "color": {"value": color, "color": get_random_color()}, "date1": {"value": date, "color": get_random_color()},
        "title": {"value": title, "color": get_random_color()}, "summary": {"value": summary, "color": get_random_color()}, 
        "info": {"value": info, "color": get_random_color()}}
res = wm.send_template(user_id, template_id, data)
print(res)

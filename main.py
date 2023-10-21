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

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)
            
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, bytes):
            return str(obj, encoding='jbk')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, int):
            return int(obj)
        elif isinstance(obj, float):
            return float(obj)
        else:
            return super(MyEncoder, self).default(obj)

# def get_weather():
#   url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city
#   res = requests.get(url).json()
#   weather = res['data']['list'][0]
#   return weather['weather'], math.floor(weather['low'])

def getInfo(location):
    """
    Get More Weather Information.
    Arguments:
        location {String} -- location html

    Returns:
        String -- Information
    """
    response = requests.get(html)
    content = response.content.decode("utf-8")
    aim = re.findall(
        r'<input type="hidden" id="hidden_title" value="(.*?)月(.*?)日(.*?)时(.*?) (.*?)  (.*?)  (.*?)"', content)
    airdata = re.findall(
        r'<li class="li6">\n<i></i>\n<span>(.*?)</span>\n<em>(.*?)</em>\n<p>(.*?)</p>', content)
    ult_index = re.findall(
        r'<li class="li1">\n<i></i>\n<span>(.*?)</span>\n<em>(.*?)</em>\n<p>(.*?)</p>\n</li>', content)
    cloth_index = re.findall(
        r'<i></i>\n<span>(.*?)</span>\n<em>(.*?)</em>\n<p>(.*?)</p>\n</a>\n</li>\n<li class="li4">', content)
    # wash_index = re.findall(r'<li class="li4">\n<i></i>\n<span>(.*?)</span>\n<em>(.*?)</em>\n<p>(.*?)</p>', content)
    lose_index = re.findall(
        r'</span>\n<em>(.*?)</em>\n<p>(.*?)</p>\n</a>\n</li>\n<li class="li5">', content)
    # print(lose_index)
    txt1 = '@天气预报:'+'\n'
    txt2 = '天气情况: '+aim[0][5]+'\n'+'温度情况: '+aim[0][6]+'\n'
    txt3 = '穿衣指数: '+cloth_index[0][0]+', '+cloth_index[0][2]+'\n'
    txt4 = '减肥指数：' + lose_index[0][1]+'\n'
    txt5 = '空气指数: '+airdata[0][0]+', '+airdata[0][2]+'\n'
    txt6 = '紫外线指数: '+ult_index[0][0]+', '+ult_index[0][2]+'\n'

    more_information = '\n'+txt1+txt2+txt3+txt4+txt5+txt6
    return more_information


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

def get_lucky():
  url = "http://web.juhe.cn:8080/constellation/getAll?consName=金牛座&type=today&key=4a11bbcbf089edaf14c2d9bdb80c2ec4"
  res = requests.get(url).json()
  return res['color'],res['QFriend'],res['number']

def get_info():
  url = "http://v.juhe.cn/toutiao/index?type=yule&key=d268884b9b07c0eb9d6093dc54116018"
  res = requests.get(url).json()['result']
  info = res['data'][0]['title']
  return info

def get_history():
  url = "https://api.oick.cn/lishi/api.php"
  res= requests.get(url).json()
  history = res['result'][0]
  return history['date'][:4],history['title']

client = WeChatClient(app_id, app_secret)
wm = WeChatMessage(client)
# wea, temperature = get_weather()
color_1,summary,number = get_lucky()
date1,title = get_history()
info = get_info()
date_1 = json.dumps(date1,cls=MyEncoder,indent=4)
today_date = json.dumps(date.today(), cls=ComplexEncoder)
more_information = getInfo("大同")

data = {"city":{"value":city}, "date":{"value":today_date}, "weather":{"value":more_information},
        # "temperature":{"value": temperature},
        "love_days":{"value":get_count()},"birthday_left":{"value":get_birthday()},
        "words":{"value":get_words()}, "color_1": {"value": color_1}, "date_1": {"value": date_1},
        "title": {"value": title}, "summary": {"value": summary}, 
        "info": {"value": info}, "number": {"value": number}}
res = wm.send_template(user_id, template_id, data)
print(res)

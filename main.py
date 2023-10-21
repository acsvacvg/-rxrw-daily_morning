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

def get_weather():
    city_name = '大同'
 
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': 'HttpOnly; userNewsPort0=1; Hm_lvt_080dabacb001ad3dc8b9b9049b36d43b=1660634957; f_city=%E9%87%91%E5%8D%8E%7C101210901%7C; defaultCty=101210901; defaultCtyName=%u91D1%u534E; Hm_lpvt_080dabacb001ad3dc8b9b9049b36d43b=1660639816',
        'Host': 'www.weather.com.cn',
        'Referer': 'http://www.weather.com.cn/weather1d/101100201.shtml',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.54'
 
    }
    url = "http://www.weather.com.cn/weather/101100201.shtml"
    response = get(url=url, headers=headers)
 
    text = response.content.decode('utf-8')
    soup = bs4.BeautifulSoup(text, 'html.parser')
    # 存放日期
    list_day = []
    i = 0
    day_list = soup.find_all('h1')
    for each in day_list:
        if i <= 1:  # 今明两天的数据
            list_day.append(each.text.strip())
            i += 1
 
    # 天气情况
    list_weather = []
    weather_list = soup.find_all('p', class_='wea')  # 之前报错是因为写了class 改为class_就好了
    for i in weather_list:
        list_weather.append(i.text)
    list_weather = list_weather[0:2]  # 只取今明两天
 
    # 存放当前温度，和明天的最高温度和最低温度
    tem_list = soup.find_all('p', class_='tem')
 
    i = 0
    list_tem = []
    for each in tem_list:
        if i >= 0 and i < 2:
            list_tem.append([each.span.text, each.i.text])  # 记录明天的最高温度和最低温度
            i += 1
 
    # 风力
    list_wind = []
    wind_list = soup.find_all('p', class_='win')
    for each in wind_list:
        list_wind.append(each.i.text.strip())
    list_wind = list_wind[0:2]  # 同只取今明两天
 
    today_date = list_day[0]
    today_weather = list_weather[0]
    today_max = list_tem[0][0] + '℃'
    today_min = list_tem[0][1]
 
    today_wind = list_wind[0]
    tomorrow = list_day[1]
    tomorrow_weather = list_weather[1]
    tomorrow_max = list_tem[1][0] + '℃'
    tomorrow_min = list_tem[1][1]
    tomorrow_wind = list_wind[1]
 
    return city_name, today_date, today_weather, today_min, today_max, today_wind, tomorrow, tomorrow_weather, tomorrow_min, tomorrow_max, tomorrow_wind

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
city_name, today_date, today_weather, today_min, today_max, today_wind, tomorrow, tomorrow_weather, tomorrow_min, tomorrow_max, tomorrow_wind = get_weather()

data = {"city":{"value":city}, "date":{"value":today_date}, "weather":{"value":today_weather},
        "temperature":{"value": today_min},
        "love_days":{"value":get_count()},"birthday_left":{"value":get_birthday()},
        "words":{"value":get_words()}, "color_1": {"value": color_1}, "date_1": {"value": date_1},
        "title": {"value": title}, "summary": {"value": summary}, 
        "info": {"value": info}, "number": {"value": number}}
res = wm.send_template(user_id, template_id, data)
print(res)

from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random
import json
from requests.packages import urllib3
import os
import random
from bs4 import BeautifulSoup


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
    url = 'http://www.weather.com.cn/weather/101100201.shtml'
    sysdate = datetime.today()
    r = requests.get(url)  # 用requests抓取网页信息
    r.raise_for_status()  # 可以让程序产生异常时停止程序
    r.encoding = r.apparent_encoding #编码格式
    html=r.text

    final_list = []
    soup = BeautifulSoup(html, 'html.parser')  # 用BeautifulSoup库解析网页 #soup里有对当前天气的建议
    body = soup.body #从soup里截取body的一部分
    data = body.find('div', {'id': '7d'})
    ul = data.find('ul')
    lis = ul.find_all('li')

    for day in lis:
        temp_list = []

        date = day.find('h1').string  # 找到日期
        if date.string.split('日')[0]==str(sysdate.day):
            temp_list = []

            date = day.find('h1').string  # 找到日期
            temp_list.append(date)

            info = day.find_all('p')  # 找到所有的p标签
            temp_list.append(info[0].string)

            if info[1].find('span') is None:  # 找到p标签中的第二个值'span'标签——最高温度
                temperature_highest = ' '  # 用一个判断是否有最高温度
            else:
                temperature_highest = info[1].find('span').string
                temperature_highest = temperature_highest.replace('℃', ' ')

            if info[1].find('i') is None:  # 找到p标签中的第二个值'i'标签——最高温度
                temperature_lowest = ' '  # 用一个判断是否有最低温度
            else:
                temperature_lowest = info[1].find('i').string
                temperature_lowest = temperature_lowest.replace('℃', ' ')

            temp_list.append(temperature_highest)  # 将最高气温添加到temp_list中
            temp_list.append(temperature_lowest)  # 将最低气温添加到temp_list中

            final_list.append(temp_list)  # 将temp_list列表添加到final_list列表中
            text_weather = '天气情况是' + final_list[0][1] + ',温度是' + final_list[0][3].strip() + '~' + final_list[0][2].strip() + '摄氏度'
            return text_weather

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
wea = get_weather()
color_1,summary,number = get_lucky()
date1,title = get_history()
info = get_info()
date_1 = json.dumps(date1,cls=MyEncoder,indent=4)
today_date = json.dumps(date.today(), cls=ComplexEncoder)

data = {"city":{"value":city}, "date":{"value":today_date}, "weather":{"value":wea},
        # "temperature":{"value": temperature},
        "love_days":{"value":get_count()},"birthday_left":{"value":get_birthday()},
        "words":{"value":get_words()}, "color_1": {"value": color_1}, "date_1": {"value": date_1},
        "title": {"value": title}, "summary": {"value": summary}, 
        "info": {"value": info}, "number": {"value": number}}
res = wm.send_template(user_id, template_id, data)
print(res)

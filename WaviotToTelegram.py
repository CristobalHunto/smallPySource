import requests
import datetime
import os
import pandas as pd
from openpyxl import load_workbook
import json

#from bs4 import BeautifulSoup

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0', 'Accept': '*/*'}
URL_AUTHO = 'https://auth.waviot.ru/?action=user-login&true_api=1'
URL_START = 'https://lk.waviot.ru/?device=summary'


def date_varible():
 t = datetime.datetime.now()
 #if t.hour > 20:
  #t = datetime.datetime.fromordinal(t.toordinal() + 1)
 d_plus = 1 * 24 * 60 * 60

 t_to = int(t.replace(t.year, t.month, t.day, 0, 0, 0, 0).timestamp() - d_plus)
 if t.month > 1:
  t_from = int(t.replace(t.year, t.month - 1, t.day, 0, 0, 0, 0).timestamp() - d_plus)
 else:
  t_from = int(t.replace(t.year - 1, 12, t.day, 0, 0, 0, 0).timestamp() - d_plus)


 s = str(t.strftime('%Y_%m_%d')+'_Electric.xlsx')
 return s, t_from ,t_to

def network_sesion(file_n, t_from, t_to):

 datas = {
  'login' : '********',
  'password' : '*******'
 }

 URL_SCRIPT = f'https://lk.waviot.ru/api/report/?template=recursive_report_electro&class=&from={t_from}&to={t_to}&id=13678'
 URL_SCRIPT.replace(' ','')
 #print(URL_SCRIPT)


 #Заходим на сервер
 s = requests.Session()
 try:
  loging = s.post(URL_AUTHO, data = datas, headers = HEADERS)
  print("Аутентификация ", loging)
 except Exception as e:
  print("Ошибка Аутентификации ", e)
  return False


 #Скачиваем архив
 try:
  print(URL_SCRIPT)
  htm = s.get(URL_SCRIPT, headers = HEADERS)
  print("Запрас на скачивание ", htm)
 except Exception as e:
  print("Скачевание архива не возможно ", e)
  return False

 #сохранием фаил
 try:
  f = open(file_n,'wb')
  f.write(htm.content)
  f.close()
  print("Фаил готов")
 except Exception as e:
  print("Ошибка записи фаила на диск ", e)
  return False

 return True

#извлекаем первую букву из нозвания улицы и дописывем 
#номер участка 'пер. Тихий 12' -> 'Т12'
def getPrefix(s):
 ss = s.split(" ")
 num_ar = ss[len(ss)-1]
 for a in s:
  if a >= 'А' and a <= 'Я':
   return str(a+num_ar)
 return 'Nan'

TOKEN = "------------"
URL = "https://api.telegram.org/bot-------------/{method}"
OFFSET = 0

def get_updates(offset):
 tg_request = requests.get(URL.format(method=f"getUpdates?offset={offset}"))
 #print(tg_request.text)
 try:
  tg_reg_data = json.loads(tg_request.text)
  return tg_reg_data
 except Exception as e:
  print(e)

def send_message(chat_id,text):
 data = {
  "chat_id": chat_id,
  "text": text
 }
 print(text)
 try:
  requests.post(URL.format(method="sendMessage"), data=data)
 except Exception as e:
  print(e)

#==================================================

#Проверяем наличее файла
file_name, t_from, t_to = date_varible()
if os.path.exists(file_name):
 print("Файл уже скачен")
else:
 if not network_sesion(file_name, t_from, t_to):
  print("Ошибка получение данных")
  exit(1)

print("Разбор XLSX ", file_name)

# Разбор Excel
#0N 1Addr 8Name 12date 20Vol
mCol = [0, 1, 8, 12, 20]

xl = pd.read_excel(file_name, engine='openpyxl', skiprows=8, usecols=mCol)

try:
 mPrefix = []
 idItem = 0
 while type(xl.loc()[idItem][0]) is int:
  pr = getPrefix(xl.loc()[idItem][1])
  #print(pr)
  mPrefix.append(pr)
  idItem += 1
except Exception as e:
 print('error', e)
 exit(1)

flag = 2
while flag > 0:
 data = get_updates(OFFSET)
 #print(data)
 try:
  result = data["result"]
  for res in result:
   OFFSET = res["update_id"] + 1
   print(res["message"]["text"], end=' -> ')
   if res["message"]["text"] == "Привет":
    flag = 1
    send_message(chat_id=res["message"]["chat"]["id"], text="Hello!")
   elif res["message"]["text"] == "Пока":
    send_message(chat_id=res["message"]["chat"]["id"], text="By!")
    if flag == 1 :
     flag = 0
   else:
    flag = 1
    try:
     idItem = mPrefix.index(res["message"]["text"])
     sendText = ' Запись N{0}\nАдрес - {1}\nАбанент - {2}\nРасход - {4}КВт/ч. на - {3}'\
      .format(*[xl.loc()[idItem][i] for i in range(5)])
    except:
     sendText = 'No found!'
    send_message(chat_id=res["message"]["chat"]["id"], text=sendText)
 except:
  continue

exit(0)

# -*- coding: UTF-8 -*-

import telebot
from telebot import types
import requests
import pandas as pd
from datetime import date, timedelta, datetime
import time
from html2image import Html2Image
import reg_data
import os
from bs4 import BeautifulSoup
import traceback



bot = telebot.TeleBot("API")

hti = Html2Image(custom_flags=["--no-sandbox"])

admin_key = "ADMINKEY"

r = requests.post("https://raspis.rggu.ru/rasp/3.php/post", data={
     "formob": "%D0%94",
     "kyrs": "4",
     "srok": "interval",
     "caf": "426",
     "cafzn": "%D0%98%D0%9B%D0%B8%D0%BD%D0%B3_%D0%9F%D0%B8%D0%9F_%D0%9B%D0%9E%D0%9C%D0%9E_%D1%81+(%D0%93%D1%80%D1%83%D0%BF%D0%BF%D0%B0%3A+1)",
     "sdate_year": "2023",
     "sdate_month": "02",
     "sdate_day": "02",
     "fdate_year": "2023",
     "fdate_month": "06",
     "fdate_day": "31"

})
table_MN = pd.read_html(r.text)
df = table_MN[0]

r = requests.post("https://raspis.rggu.ru/rasp/3.php/post", data={
     "formob": "%D0%94",
     "kyrs": "4",
     "srok": "interval",
     "caf": "427",
     "cafzn": "%D0%98%D0%9B%D0%B8%D0%BD%D0%B3_%D0%9F%D0%B8%D0%9F_%D0%9B%D0%9E%D0%9C%D0%9E_%D1%81+(%D0%93%D1%80%D1%83%D0%BF%D0%BF%D0%B0%3A+2)",
     "sdate_year": "2023",
     "sdate_month": "02",
     "sdate_day": "02",
     "fdate_year": "2023",
     "fdate_month": "06",
     "fdate_day": "31"

})
table_MN = pd.read_html(r.text)
df_1 = table_MN[0]

df.columns = df.iloc[0]
df = df[1:]
df_1.columns = df_1.iloc[0]
df_1 = df_1[1:]

first_yaz = df.loc[df["П\гр"] == "1"]
second_yaz = df.loc[df["П\гр"] == "2"]
third_yaz = df.loc[df["П\гр"] == "3"]
lections = df.loc[df["Тип"] == "лек"]
first_seminar = df.loc[df["Группа"] == "1"]
second_seminar = df_1.loc[df_1["Группа"] == "2"]
relig_yap = pd.concat([first_seminar.loc[first_seminar["Предмет"] == "Религия Японии"],
                       second_seminar.loc[second_seminar["Предмет"] == "Религия Японии"],
                       lections.loc[lections["Предмет"] == "Религия Японии"]])
chin_phil = pd.concat([first_seminar.loc[first_seminar["Предмет"] == "Философия Древнего Китая"],
                       second_seminar.loc[second_seminar["Предмет"] == "Философия Древнего Китая"],
                       lections.loc[lections["Предмет"] == "Философия Древнего Китая"]])
first_seminar = first_seminar.loc[first_seminar["Предмет"] != "Религия Японии"]
second_seminar = second_seminar.loc[second_seminar["Предмет"] != "Религия Японии"]
first_seminar = first_seminar.loc[first_seminar["Предмет"] != "Философия Древнего Китая"]
second_seminar = second_seminar.loc[second_seminar["Предмет"] != "Философия Древнего Китая"]
lections = lections.loc[lections["Предмет"] != "Философия Древнего Китая"]
lections = lections.loc[lections["Предмет"] != "Религия Японии"]
registered_users = {}
registered_users["DATA"] = {}
registered_users = reg_data.registration_data
users_online = {}


@bot.message_handler(commands=["start"])
def start(message):
     try:
          print(str(message.chat.id))
          users_online[str(message.chat.id)] = {}
          if str(message.chat.id) not in registered_users.keys():
               bot.send_message(message.chat.id,
                                text="Привет! Похоже мы с тобой еще не знакомы... Давай исправим это! Как тебя зовут?")
               users_online[str(message.chat.id)]["state"] = "registration_start"
               registered_users[str(message.chat.id)] = {}
               registered_users[str(message.chat.id)]["groups"] = []
          else:
               markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
               btn1 = types.KeyboardButton("Расписание")
               btn2 = types.KeyboardButton("Где пара?")
               btn4 = types.KeyboardButton("Важная информация")
               btn3 = types.KeyboardButton("Выйти")
               markup.add(btn1, btn2, btn4, btn3)
               users_online[str(message.chat.id)]["state"] = "menu_start"
               if "Name" in registered_users[str(message.chat.id)].keys():
                    bot.send_message(message.chat.id, text=f"""Привет, {registered_users[str(message.chat.id)]["Name"]}! Чем могу помочь??""", reply_markup=markup)
                    users_online[str(message.chat.id)]["schedule"] = lections
                    for curr_group in registered_users[str(message.chat.id)]["groups"]:
                         if curr_group == "first_seminar":
                              users_online[str(message.chat.id)]["schedule"] = pd.concat(
                                   [users_online[str(message.chat.id)]["schedule"], first_seminar])
                         if curr_group == "second_seminar":
                              users_online[str(message.chat.id)]["schedule"] = pd.concat(
                                   [users_online[str(message.chat.id)]["schedule"], second_seminar])
                         if curr_group == "first_yaz":
                              users_online[str(message.chat.id)]["schedule"] = pd.concat(
                                   [users_online[str(message.chat.id)]["schedule"], first_yaz])
                         if curr_group == "second_yaz":
                              users_online[str(message.chat.id)]["schedule"] = pd.concat(
                                   [users_online[str(message.chat.id)]["schedule"], second_yaz])
                         if curr_group == "third_yaz":
                              users_online[str(message.chat.id)]["schedule"] = pd.concat(
                                   [users_online[str(message.chat.id)]["schedule"], third_yaz])
                         if curr_group == "relig_yap":
                              users_online[str(message.chat.id)]["schedule"] = pd.concat(
                                   [users_online[str(message.chat.id)]["schedule"], relig_yap])
                         if curr_group == "chin_phil":
                              users_online[str(message.chat.id)]["schedule"] = pd.concat(
                                   [users_online[str(message.chat.id)]["schedule"], chin_phil])
                    users_online[str(message.chat.id)]["schedule"] = users_online[str(message.chat.id)]["schedule"].sort_index()
               else:
                    del users_online[str(message.chat.id)]
                    bot.send_message(message.chat.id,
                                     text="Привет! Похоже мы с тобой еще не знакомы... Давай исправим это! Как тебя зовут?")
                    users_online[str(message.chat.id)]["state"] = "registration_start"
                    registered_users[str(message.chat.id)] = {}
                    registered_users[str(message.chat.id)]["groups"] = []
     except Exception:
          bot.send_message(message.chat.id,
                           text="Произошла непредвиденная ошибка, прошу снова отправить команду /start")
          bot.send_message(879730812, text=f"Ошибка у {message.chat.id}")
          traceback.print_exc()


@bot.message_handler(content_types=['text'])
def actual_bot(message):
     try:
          if users_online[str(message.chat.id)]["state"] == "registration_start":
               users_online[str(message.chat.id)]["state"] = "registration_group"
               if message.text.isalnum():
                    registered_users[str(message.chat.id)]["Name"] = message.text
                    bot.send_message(message.chat.id,
                                     text=f"""Прекрасно, приятно познакомиться, {registered_users[str(message.chat.id)]["Name"]}""")
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    btn1 = types.KeyboardButton("Первая языковая")
                    btn2 = types.KeyboardButton("Вторая языковая")
                    btn3 = types.KeyboardButton("Третья языковая")
                    markup.add(btn1, btn2, btn3)
                    bot.send_message(message.chat.id, text="А в какой ты языковой группе?", reply_markup=markup)
               else:
                    bot.send_message(message.chat.id, text="Так нельзя, в имени не может быть таких букв((")
                    users_online[str(message.chat.id)]["state"] = "registration_start"

          if users_online[str(message.chat.id)]["state"] == "registration_group" and (
                  message.text == "Первая языковая" or message.text == "Вторая языковая" or message.text == "Третья языковая"):
               if message.text == "Первая языковая":
                    registered_users[str(message.chat.id)]["groups"].append("first_yaz")
               if message.text == "Вторая языковая":
                    registered_users[str(message.chat.id)]["groups"].append("second_yaz")
               if message.text == "Третья языковая":
                    registered_users[str(message.chat.id)]["groups"].append("third_yaz")
               markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
               btn1 = types.KeyboardButton("Первая семинарская")
               btn2 = types.KeyboardButton("Вторая семинарская")
               markup.add(btn1, btn2)
               bot.send_message(message.chat.id, text="А в какой семинарской?", reply_markup=markup)
               users_online[str(message.chat.id)]["state"] = "registration_sem_group"

          if users_online[str(message.chat.id)]["state"] == "registration_sem_group" and (
                  message.text == "Первая семинарская" or message.text == "Вторая семинарская"):
               users_online[str(message.chat.id)]["state"] = "registration_po_vybory"
               if message.text == "Первая семинарская":
                    registered_users[str(message.chat.id)]["groups"].append("first_seminar")
               if message.text == "Вторая семинарская":
                    registered_users[str(message.chat.id)]["groups"].append("second_seminar")
               markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
               btn1 = types.KeyboardButton("Религия Японии")
               btn2 = types.KeyboardButton("Философия Китая")
               markup.add(btn1, btn2)
               bot.send_message(message.chat.id, text="А какой курс по выбору?", reply_markup=markup)
               print(registered_users[str(message.chat.id)]["groups"])

          if users_online[str(message.chat.id)]["state"] == "registration_po_vybory" and (
                  message.text == "Религия Японии" or message.text == "Философия Китая"):
               users_online[str(message.chat.id)]["state"] = "main_menu"
               bot.send_message(message.chat.id, text="Готово!")
               if message.text == "Религия Японии":
                    registered_users[str(message.chat.id)]["groups"].append("relig_yap")
               if message.text == "Философия Китая":
                    registered_users[str(message.chat.id)]["groups"].append("chin_phil")
                    open('reg_data.py', 'w').close()
                    a = str(registered_users)
                    f = open("reg_data.py", "w", encoding="utf-8")
                    f.write(f"registration_data = {a}")
                    f.close()

          if users_online[str(message.chat.id)]["state"] == "main_menu":
               markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
               btn1 = types.KeyboardButton("Расписание")
               btn2 = types.KeyboardButton("Где пара?")
               btn4 = types.KeyboardButton("Важная информация")
               btn3 = types.KeyboardButton("Выйти")
               markup.add(btn1, btn2, btn4, btn3)
               users_online[str(message.chat.id)]["state"] = "menu_start"
               bot.send_message(message.chat.id, text=f"Чем могу помочь??", reply_markup=markup)

          if users_online[str(message.chat.id)]["state"] == "menu_start" and message.text == "Важная информация":
               for i in registered_users["DATA"].keys():
                    bot.send_message(message.chat.id, text=f"""{i}: <code>{registered_users["DATA"][i]}</code>""",
                                     parse_mode="HTML")

          if users_online[str(message.chat.id)]["state"] == "menu_start" and message.text == "Расписание":
               users_online[str(message.chat.id)]["schedule"] = lections
               for curr_group in registered_users[str(message.chat.id)]["groups"]:
                    if curr_group == "first_seminar":
                         users_online[str(message.chat.id)]["schedule"] = pd.concat(
                              [users_online[str(message.chat.id)]["schedule"], first_seminar])
                    if curr_group == "second_seminar":
                         users_online[str(message.chat.id)]["schedule"] = pd.concat(
                              [users_online[str(message.chat.id)]["schedule"], second_seminar])
                    if curr_group == "first_yaz":
                         users_online[str(message.chat.id)]["schedule"] = pd.concat(
                              [users_online[str(message.chat.id)]["schedule"], first_yaz])
                    if curr_group == "second_yaz":
                         users_online[str(message.chat.id)]["schedule"] = pd.concat(
                              [users_online[str(message.chat.id)]["schedule"], second_yaz])
                    if curr_group == "third_yaz":
                         users_online[str(message.chat.id)]["schedule"] = pd.concat(
                              [users_online[str(message.chat.id)]["schedule"], third_yaz])
                    if curr_group == "relig_yap":
                         users_online[str(message.chat.id)]["schedule"] = pd.concat(
                              [users_online[str(message.chat.id)]["schedule"], relig_yap])
                    if curr_group == "chin_phil":
                         users_online[str(message.chat.id)]["schedule"] = pd.concat(
                              [users_online[str(message.chat.id)]["schedule"], chin_phil])
               users_online[str(message.chat.id)]["schedule"] = users_online[str(message.chat.id)]["schedule"].sort_index()
               markup = types.InlineKeyboardMarkup()
               markup.add(types.InlineKeyboardButton(text='ПН', callback_data="0"))
               markup.add(types.InlineKeyboardButton(text='ВТ', callback_data="1"))
               markup.add(types.InlineKeyboardButton(text='СР', callback_data="2"))
               markup.add(types.InlineKeyboardButton(text='ЧТ', callback_data="3"))
               markup.add(types.InlineKeyboardButton(text='ПТ', callback_data="4"))
               markup.add(types.InlineKeyboardButton(text='СБ', callback_data="5"))
               bot.send_message(message.chat.id, text=f"Выбери день:", reply_markup=markup)

          if users_online[str(message.chat.id)]["state"] == "menu_start" and message.text == "😂":
               URL = "https://www.anekdot.ru/random/anekdot/"
               users_online[str(message.chat.id)]["anecdote_page"] = requests.get(URL)
               users_online[str(message.chat.id)]["anecdote_soup"] = BeautifulSoup(users_online[str(message.chat.id)]["anecdote_page"].content, "html.parser")
               users_online[str(message.chat.id)]["anecdote_temp"] = users_online[str(message.chat.id)][
                    "anecdote_soup"].find_all("div", class_="content content-min")
               users_online[str(message.chat.id)]["anecdote_temp1"] = \
               users_online[str(message.chat.id)]["anecdote_temp"][0].findNext("div", class_="text")
               users_online[str(message.chat.id)]["anecdote_temp1"] = str(
                    users_online[str(message.chat.id)]["anecdote_temp1"])
               users_online[str(message.chat.id)]["anecdote_temp1"] = users_online[str(message.chat.id)][
                    "anecdote_temp1"].replace("""<div class="text">""", "")
               users_online[str(message.chat.id)]["anecdote_temp1"] = users_online[str(message.chat.id)][
                    "anecdote_temp1"].replace("""</div>""", "")
               users_online[str(message.chat.id)]["anecdote_temp1"] = users_online[str(message.chat.id)][
                    "anecdote_temp1"].replace("""<br/>""", "\n")
               users_online[str(message.chat.id)]["anecdote_temp1"] += """\n\n\n<i>Анекдот с сайта anekdot.ru</i>"""
               bot.send_message(message.chat.id, text=users_online[str(message.chat.id)]["anecdote_temp1"],
                                parse_mode="HTML")

          if users_online[str(message.chat.id)]["state"] == "menu_start" and message.text == "Где пара?":
               days_in_week = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС", ]
               today = date.today()
               d2 = today.strftime("%d.%m.%Y")
               t = time.localtime()
               current_time = time.strftime("%H:%M:%S", t)
               current_time = datetime.strptime(current_time, "%H:%M:%S")
               print(current_time)
               pary = ["!!!!!!!8:45 - 10:05343422", "!!!!!!!10:15 - 11:35343422", "!!!!!!!12:10 - 13:30343422", "!!!!!!!13:40 - 15:00343422", "!!!!!!!15:35 - 16:55343422", "!!!!!!!17:05 - 18:25343422"]
               pary_for_checkup = ["00:00:00", "10:05:00", "11:35:00", "13:30:00", "15:00:00", "16:55:00", "18:25:00"]
               pary_for_checkup_times = []
               for i in pary_for_checkup:
                    s = datetime.strptime(i, "%H:%M:%S")
                    pary_for_checkup_times.append(s)
               print(pary_for_checkup_times)
               x = today.weekday()
               print(x)
               users_online[str(message.chat.id)]["audit"] = []
               users_online[str(message.chat.id)]["dlyapar"] = users_online[str(message.chat.id)]["schedule"].loc[
                    users_online[str(message.chat.id)]["schedule"]["Дата"] == f"{d2} {days_in_week[x]}"].copy()
               if x == 6:
                    bot.send_message(message.chat.id, text=f"""Воскресенье же, отдыхай""")
               else:
                    if pary_for_checkup_times[0] <= current_time <= pary_for_checkup_times[1]:
                         users_online[str(message.chat.id)]["audit"] = \
                         users_online[str(message.chat.id)]["dlyapar"].loc[
                              users_online[str(message.chat.id)]["dlyapar"]["Пара"] == "1", "Аудит"]
                    elif pary_for_checkup_times[1] <= current_time <= pary_for_checkup_times[2]:
                         users_online[str(message.chat.id)]["audit"] = \
                         users_online[str(message.chat.id)]["dlyapar"].loc[
                              users_online[str(message.chat.id)]["dlyapar"]["Пара"] == "2", "Аудит"]
                    elif pary_for_checkup_times[2] <= current_time <= pary_for_checkup_times[3]:
                         users_online[str(message.chat.id)]["audit"] = \
                         users_online[str(message.chat.id)]["dlyapar"].loc[
                              users_online[str(message.chat.id)]["dlyapar"]["Пара"] == "3", "Аудит"]
                    elif pary_for_checkup_times[3] <= current_time <= pary_for_checkup_times[4]:
                         users_online[str(message.chat.id)]["audit"] = \
                         users_online[str(message.chat.id)]["dlyapar"].loc[
                              users_online[str(message.chat.id)]["dlyapar"]["Пара"] == "4", "Аудит"]
                    elif pary_for_checkup_times[4] <= current_time <= pary_for_checkup_times[5]:
                         users_online[str(message.chat.id)]["audit"] = \
                         users_online[str(message.chat.id)]["dlyapar"].loc[
                              users_online[str(message.chat.id)]["dlyapar"]["Пара"] == "5", "Аудит"]
                    elif pary_for_checkup_times[5] <= current_time <= pary_for_checkup_times[6]:
                         users_online[str(message.chat.id)]["audit"] = \
                         users_online[str(message.chat.id)]["dlyapar"].loc[
                              users_online[str(message.chat.id)]["dlyapar"]["Пара"] == "6", "Аудит"]
                    if len(list(users_online[str(message.chat.id)]["audit"])) == 0:
                         if current_time < pary_for_checkup_times[1] and \
                                 users_online[str(message.chat.id)]["dlyapar"]["Пара"].iloc[0] == "1":
                              users_online[str(message.chat.id)]["audit"] = \
                              users_online[str(message.chat.id)]["dlyapar"].loc[
                                   users_online[str(message.chat.id)]["dlyapar"]["Пара"] == "1", "Аудит"]
                         elif current_time <= pary_for_checkup_times[2] and \
                                 users_online[str(message.chat.id)]["dlyapar"]["Пара"].iloc[0] == "2":
                              users_online[str(message.chat.id)]["audit"] = \
                              users_online[str(message.chat.id)]["dlyapar"].loc[
                                   users_online[str(message.chat.id)]["dlyapar"]["Пара"] == "2", "Аудит"]
                         elif current_time <= pary_for_checkup_times[3] and \
                                 users_online[str(message.chat.id)]["dlyapar"]["Пара"].iloc[0] == "3":
                              users_online[str(message.chat.id)]["audit"] = \
                              users_online[str(message.chat.id)]["dlyapar"].loc[
                                   users_online[str(message.chat.id)]["dlyapar"]["Пара"] == "3", "Аудит"]
                         elif current_time <= pary_for_checkup_times[4] and \
                                 users_online[str(message.chat.id)]["dlyapar"]["Пара"].iloc[0] == "4":
                              users_online[str(message.chat.id)]["audit"] = \
                              users_online[str(message.chat.id)]["dlyapar"].loc[
                                   users_online[str(message.chat.id)]["dlyapar"]["Пара"] == "4", "Аудит"]
                         elif current_time <= pary_for_checkup_times[5] and \
                                 users_online[str(message.chat.id)]["dlyapar"]["Пара"].iloc[0] == "5":
                              users_online[str(message.chat.id)]["audit"] = \
                              users_online[str(message.chat.id)]["dlyapar"].loc[
                                   users_online[str(message.chat.id)]["dlyapar"]["Пара"] == "5", "Аудит"]
                         elif current_time <= pary_for_checkup_times[6] and \
                                 users_online[str(message.chat.id)]["dlyapar"]["Пара"].iloc[0] == "6":
                              users_online[str(message.chat.id)]["audit"] = \
                              users_online[str(message.chat.id)]["dlyapar"].loc[
                                   users_online[str(message.chat.id)]["dlyapar"]["Пара"] == "6", "Аудит"]
                    if len(list(users_online[str(message.chat.id)]["audit"])) == 0:
                         bot.send_message(message.chat.id, text=f"Похоже на сегодня все")
                    else:
                         bot.send_message(message.chat.id,
                                          text=f"""{list(users_online[str(message.chat.id)]["audit"])[0]}""")

          if users_online[str(message.chat.id)]["state"] == "menu_start" and message.text == "Выйти":
               markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
               btn1 = types.KeyboardButton("/start")
               markup.add(btn1)
               users_online[str(message.chat.id)]["state"] = ""
               bot.send_message(message.chat.id, text=f"Пока", reply_markup=markup)

          if message.text == admin_key:
               markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
               btn1 = types.KeyboardButton("Добавить")
               btn2 = types.KeyboardButton("Редактировать")
               btn3 = types.KeyboardButton("Удалить")
               markup.add(btn1, btn2, btn3)
               users_online[str(message.chat.id)]["state"] = "admin_start"
               bot.send_message(message.chat.id,
                                text=f"Эта часть бота предназначена для редактирования важной информации. Вы могли получить сюда доступ только при наличии специального ключа администратора. Если это не так прошу вас покинуть эту часть. Несанкционированные действия могут привезти к ошибке в боте. Для выхода используйте промпт /start",
                                reply_markup=markup)

          if users_online[str(message.chat.id)]["state"] == "add_data_2":
               global curr_redacting
               registered_users["DATA"][curr_redacting] = f"{message.text}"
               bot.send_message(message.chat.id, text=f"{curr_redacting}: {message.text}")
               markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
               btn1 = types.KeyboardButton("Добавить")
               btn2 = types.KeyboardButton("Редактировать")
               btn3 = types.KeyboardButton("Удалить")
               markup.add(btn1, btn2, btn3)
               users_online[str(message.chat.id)]["state"] = "admin_start"
               bot.send_message(message.chat.id, text=f"Что-нибудь еще? /start для выхода", reply_markup=markup)
               open('reg_data.py', 'w').close()
               a = str(registered_users)
               f = open("reg_data.py", "w", encoding="utf-8")
               f.write(f"registration_data = {a}")
               f.close()

          if users_online[str(message.chat.id)]["state"] == "del_start":
               del registered_users["DATA"][message.text]
               bot.send_message(message.chat.id, text=f"Готово")
               markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
               btn1 = types.KeyboardButton("Добавить")
               btn2 = types.KeyboardButton("Редактировать")
               btn3 = types.KeyboardButton("Удалить")
               markup.add(btn1, btn2, btn3)
               users_online[str(message.chat.id)]["state"] = "admin_start"
               bot.send_message(message.chat.id, text=f"Что-нибудь еще? /start для выхода", reply_markup=markup)
               open('reg_data.py', 'w').close()
               a = str(registered_users)
               f = open("reg_data.py", "w", encoding="utf-8")
               f.write(f"registration_data = {a}")
               f.close()

          if users_online[str(message.chat.id)]["state"] == "admin_start" and message.text == "Удалить":
               markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
               for i in registered_users["DATA"].keys():
                    markup.add(types.KeyboardButton(i))
               users_online[str(message.chat.id)]["state"] = "del_start"
               bot.send_message(message.chat.id, text=f"Что именно", reply_markup=markup)

          if users_online[str(message.chat.id)]["state"] == "admin_start" and message.text == "Редактировать":
               markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
               for i in registered_users["DATA"].keys():
                    markup.add(types.KeyboardButton(i))
               users_online[str(message.chat.id)]["state"] = "redact_start"
               bot.send_message(message.chat.id, text=f"Что именно", reply_markup=markup)

          if users_online[str(message.chat.id)]["state"] == "redact_cont":
               registered_users["DATA"][curr_redacting] = f"{message.text}"
               bot.send_message(message.chat.id, text=f"{curr_redacting}: {message.text}")
               markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
               btn1 = types.KeyboardButton("Добавить")
               btn2 = types.KeyboardButton("Редактировать")
               btn3 = types.KeyboardButton("Удалить")
               markup.add(btn1, btn2, btn3)
               users_online[str(message.chat.id)]["state"] = "admin_start"
               bot.send_message(message.chat.id, text=f"Что-нибудь еще? /start для выхода", reply_markup=markup)
               open('reg_data.py', 'w').close()
               a = str(registered_users)
               f = open("reg_data.py", "w", encoding="utf-8")
               f.write(f"registration_data = {a}")
               f.close()

          if users_online[str(message.chat.id)]["state"] == "redact_start" and message.text in registered_users[
               "DATA"].keys():
               curr_redacting = message.text
               bot.send_message(message.chat.id, text=f"Новый {message.text}:")
               users_online[str(message.chat.id)]["state"] = "redact_cont"

          if users_online[str(message.chat.id)]["state"] == "add_data":
               curr_redacting = message.text
               registered_users["DATA"][curr_redacting] = ""

               bot.send_message(message.chat.id, text=f"{curr_redacting}")
               users_online[str(message.chat.id)]["state"] = "add_data_2"

          if users_online[str(message.chat.id)]["state"] == "admin_start" and message.text == "Добавить":
               bot.send_message(message.chat.id, text=f"Что добавить?")
               users_online[str(message.chat.id)]["state"] = "add_data"





     except Exception:
          bot.send_message(message.chat.id,
                           text="Произошла непредвиденная ошибка, прошу снова отправить команду /start")
          bot.send_message(879730812, text=f"Ошибка у {message.chat.id}")
          traceback.print_exc()


@bot.callback_query_handler(func=lambda call: True)
def step2(call):
     try:
          days_in_week = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС", ]
          today = date.today()
          d2 = today.strftime("%d.%m.%Y")
          t = time.localtime()
          current_time = time.strftime("%H:%M:%S", t)
          current_time = datetime.strptime(current_time, "%H:%M:%S")
          print(current_time)
          pary = ["!!!!!!!8:45 10:05343422", "!!!!!!!10:15 11:35343422", "!!!!!!!12:10 13:30343422",
                 "!!!!!!!13:40 15:00343422", "!!!!!!!15:35 16:55343422", "!!!!!!!17:05 18:25343422"]
          pary_for_checkup = ["00:00:00", "10:05:00", "11:35:00", "13:30:00", "15:00:00", "16:55:00", "18:25:00"]
          pary_for_checkup_times = []
          for i in pary_for_checkup:
               s = datetime.strptime(i, "%H:%M:%S")
               pary_for_checkup_times.append(s)
          print(pary_for_checkup_times)
          x = today.weekday()
          if x != 6:
               users_online[str(call.message.chat.id)]["day"] = today - timedelta(days=x - int(call.data))
          else:
               users_online[str(call.message.chat.id)]["day"] = today - timedelta(days=x - int(call.data) - 7)
          users_online[str(call.message.chat.id)]["dayweek"] = users_online[str(call.message.chat.id)]["day"].weekday()
          users_online[str(call.message.chat.id)]["day"] = users_online[str(call.message.chat.id)]["day"].strftime(
               "%d.%m.%Y")
          users_online[str(call.message.chat.id)]["schedule_for_day"] = \
          users_online[str(call.message.chat.id)]["schedule"].loc[users_online[str(call.message.chat.id)]["schedule"][
                                                                       "Дата"] == f"""{users_online[str(call.message.chat.id)]["day"]} {days_in_week[users_online[str(call.message.chat.id)]["dayweek"]]}"""].copy()
          print(users_online[str(call.message.chat.id)]["schedule_for_day"])
          users_online[str(call.message.chat.id)]["schedule_for_day"]["Предмет"] = \
          users_online[str(call.message.chat.id)]["schedule_for_day"]["Предмет"] + "!!!!!!!" + \
          users_online[str(call.message.chat.id)]["schedule_for_day"]["Тип"] + "343422"

          users_online[str(call.message.chat.id)]["schedule_for_day"] = users_online[str(call.message.chat.id)][
               "schedule_for_day"].drop(columns=["Дата"])
          users_online[str(call.message.chat.id)]["schedule_for_day"] = users_online[str(call.message.chat.id)][
               "schedule_for_day"].drop(columns=["Группа"])
          users_online[str(call.message.chat.id)]["schedule_for_day"] = users_online[str(call.message.chat.id)][
               "schedule_for_day"].drop(columns=["П\гр"])
          users_online[str(call.message.chat.id)]["schedule_for_day"] = users_online[str(call.message.chat.id)][
               "schedule_for_day"].drop(columns=["Тип"])
          users_online[str(call.message.chat.id)]["schedule_for_day"] = users_online[str(call.message.chat.id)]["schedule_for_day"].sort_values(by=['Пара'])
          users_online[str(call.message.chat.id)]["height_mod"] = len(
               users_online[str(call.message.chat.id)]["schedule_for_day"].index)
          users_online[str(call.message.chat.id)]["pary_for_display"] = []
          users_online[str(call.message.chat.id)]["pary"] = users_online[str(call.message.chat.id)]["schedule_for_day"]["Пара"].values.tolist()
          users_online[str(call.message.chat.id)]["pary"] = [int(inter) for inter in users_online[str(call.message.chat.id)]["pary"]]
          for users_online[str(call.message.chat.id)]["para"] in users_online[str(call.message.chat.id)]["pary"]:
               users_online[str(call.message.chat.id)]["pary_for_display"].append(pary[users_online[str(call.message.chat.id)]["para"] - 1])
          users_online[str(call.message.chat.id)]["schedule_for_day"].insert(1, "Время", users_online[str(call.message.chat.id)]["pary_for_display"])
          users_online[str(call.message.chat.id)]["schedule_for_day"]["Пара"] = "hfdhfdh" + users_online[str(call.message.chat.id)]["schedule_for_day"]["Пара"]+ "sassasas" + users_online[str(call.message.chat.id)]["schedule_for_day"]["Время"]
          users_online[str(call.message.chat.id)]["schedule_for_day"] = users_online[str(call.message.chat.id)]["schedule_for_day"].drop(columns=["Время"])
          if users_online[str(call.message.chat.id)]["height_mod"] != 0:
               style = """<style>
            table {
            table-layout: auto;
              border-collapse: collapse;
              line-height: normal;;
            }

            th {
              text-align: center;
              padding: 8px;
            }

            td {
              text-align: left;
              font-family: serif;
              font-size: 20px;
              padding: 10px;
            }

            td:nth-child(even){background-color: #FFD5D5}

            th {
              background-color: #0000FF;
              color: white;
            }
            </style>"""
               users_online[str(call.message.chat.id)]["schedule_for_day"] = users_online[str(call.message.chat.id)][
                    "schedule_for_day"].to_html(header=False, index=False)
               users_online[str(call.message.chat.id)]["schedule_for_day"] = users_online[str(call.message.chat.id)][
                    "schedule_for_day"].replace("!!!!!!!", """<br><i><font size="-1">""")
               users_online[str(call.message.chat.id)]["schedule_for_day"] = users_online[str(call.message.chat.id)][
                    "schedule_for_day"].replace("343422", "</font></i>")
               users_online[str(call.message.chat.id)]["schedule_for_day"] = users_online[str(call.message.chat.id)]["schedule_for_day"].replace("hfdhfdh", """<strong><font size="+2">""")
               users_online[str(call.message.chat.id)]["schedule_for_day"] = users_online[str(call.message.chat.id)][
                    "schedule_for_day"].replace("sassasas", """</font></strong>""")
               users_online[str(call.message.chat.id)]["schedule_for_day"] = users_online[str(call.message.chat.id)][
                                                                                  "schedule_for_day"] + style
               hti.size = (600, 120 * users_online[str(call.message.chat.id)]["height_mod"])
               hti.screenshot(html_str=users_online[str(call.message.chat.id)]["schedule_for_day"],
                              save_as=f"""page{call.message.chat.id}.png""")
               users_online[str(call.message.chat.id)]["schedule_img"] = open(f"""page{call.message.chat.id}.png""",
                                                                              'rb')
               bot.send_photo(call.message.chat.id, users_online[str(call.message.chat.id)]["schedule_img"],
                              caption=f"""{days_in_week[users_online[str(call.message.chat.id)]["dayweek"]]}""")
               users_online[str(call.message.chat.id)]["schedule_img"] = ""
               print(users_online[str(call.message.chat.id)]["schedule_for_day"])
          else:
               bot.send_message(call.message.chat.id, text="В этот день нет пар")
     except Exception:
          bot.send_message(call.message.chat.id,
                           text="Произошла непредвиденная ошибка, прошу снова отправить команду /start")
          bot.send_message(879730812, text=f"Ошибка в расписании у {call.message.chat.id}")
          traceback.print_exc()


bot.polling(none_stop=True)
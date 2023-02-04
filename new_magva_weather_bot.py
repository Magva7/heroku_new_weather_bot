import telebot
import requests  # для запроса адреса по координатам через яндекс и погоды через openweather
from telebot import types
import datetime
from datetime import datetime, timedelta  # для перевода времени с UTC на человеческий
# os.system('cls||clear')  # очистка консоли перед запуском

bot = telebot.TeleBot('1706338684:AAGojuK3Xw50cqr1osXwC6uvTRql0gQ-5cw')  # Создаем бота
ya_token = 'a080eb21-a250-4036-8bee-7b2c7e97f34a'
open_wea_api_key = '2745926c9f2ffb7903aec82510e1bc65'

# ======= Блок приветствие ===================
@bot.message_handler(commands=["start"]) # прослушивание команды start и действия при ее получении
def send_hi_and_button(message): # функция, внутрь которой передаем объект message, у которого
    # есть мноооожество свойств, свойства объекта message- это текст сообщения и данные того
    # человека, который отправил боту команду start, т.е. id телеги этого человека, его ник и т.д.

    # ===Создаем клавиатуру с кнопкой запроса локации=======================
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)     # Оснастка для кнопок
    button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)  # сама кнопка
    markup.add(button_geo)  # добавляем кнопку в оснастку
    # =======================================================================

    # Бот отправляет приветствие и отрисованную кнопку
    bot.send_message(message.chat.id, "Добрый день, нажмите на кнопку ниже, чтобы отправить ваши "
                                      "координаты", reply_markup=markup)

    print('Бот получил от юзверя', message.from_user.username, 'команду start, отправил ему '
                                                               'приветствие, и отрисованную кнопку.')
    print(message)  # для интереса содержимое объекта message, т.е. все данные по тому человеку, который написал

# =================================================================================================

@bot.message_handler(commands=['ping'])  # прослушивание команды /ping
def send_welcome(message):  # действия
    bot.reply_to(message, f'pong')
    print('Получена команда ping, отправлен ответ')
    

@bot.message_handler(content_types=["text"])  # Получение сообщений от юзера
def handle_text(message):
    if message.text == 'ping':
        bot.send_message(message.chat.id, 'pong')
        print('Получен текст: ', message.text, ', отправлен ответ pong')
    else:
        bot.send_message(message.chat.id, 'Вы написали: ' + message.text)
        print('Получен текст: ', message.text, ', отправлен ответ')

# Блок получения координат и ответа об этом пользователю
@bot.message_handler(content_types=['location'])  # прослушивание, что боту передали координаты
def location(message):
    if message.location is not None:  # если передали не пустые данные
        koordinaty = message.location  # полные координаты

        latitude = str(koordinaty.latitude)  # 43.209693
        longitude = str(koordinaty.longitude) # 76.869619

        # ==== Яндекс - адрес по координатам ==================================
        base_url_ya = 'https://geocode-maps.yandex.ru/1.x?format=json&lang=ru_RU&kind=house&geocode='
        final_url_ya = base_url_ya + longitude + ',' + latitude + '&apikey=' + ya_token
        address_data = requests.get(final_url_ya).json()

        # вытаскиваем из всего пришедшего json именно строку с полным адресом.
        address_str = address_data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"][
                    "metaDataProperty"]["GeocoderMetaData"]["AddressDetails"]["Country"][
                    "AddressLine"]
        # =====================================================================

        # ==== Openweather - получение текущей погоды и почасового прогноза погодыпо координатам ==========
        # final_url_current_wea_manual = 'http://api.openweathermap.org/data/2.5/weather?appid=2745926c9f2ffb7903aec82510e1bc65&lat=43.209693&lon=76.869619&units=metric&lang=RU' # полный url для проверки в браузере
        # final_url_forecast_wea_manual = 'https://api.openweathermap.org/data/2.5/onecall?appid=2745926c9f2ffb7903aec82510e1bc65&lat=43.209693&lon=76.869619&units=metric&lang=RU'

        base_url_open_weat = "http://api.openweathermap.org/data/2.5/onecall?"
        final_url_current_wea = base_url_open_weat + "appid=" + open_wea_api_key + "&lat=" + latitude + "&lon=" + longitude + '&units=metric&lang=RU'

        forecast_wea_data = requests.get(final_url_current_wea).json()  # запрашиваем погоду

        # распарсиваем результат
        timezone_offset = forecast_wea_data['timezone_offset']  # смещение часового пояса в секундах

        # проверяем температуру, если больше нуля, то добавляем +
        temp_for_check = round(forecast_wea_data['current']['temp'])
        if temp_for_check > 0:
            temp_for_check = '+' + str(temp_for_check)
        # print(temp_for_check)

        current_temp = '\nСейчас:  ' + '' + str(temp_for_check) + ' по цельсию'
        current_wind = 'Ветер:  ' + str(round(forecast_wea_data['current']['wind_speed'])) + ' м/с'
        current_rain = forecast_wea_data['current']['weather'][0]['description']  # осадки

        current_weather = current_temp + '\n' + current_wind + ', ' + current_rain  # погода на текущий момент

        # почасовой прогноз на ближайшие 4 часа, первый результат пропускаем, т.к. в нем текущая погода, мы её уже показали
        all_forecast = ''  # все прогнозы
        i = 1
        while i < 5:
            my_this_forecast = forecast_wea_data['hourly'][i]  # погода в первом прогнозе
            my_this_forecast_time_unix = my_this_forecast['dt']  # время в первом прогнозе в unix формате
            # my_this_forecast_time_human = datetime.utcfromtimestamp(my_this_forecast_time_unix).strftime('%H:%M')  # время
            # без смещения
            my_this_forecast_time_human = (datetime.utcfromtimestamp(my_this_forecast_time_unix) + timedelta(hours=(
                    timezone_offset / 3600))).strftime('%H:%M')  # смещение времени


            # проверяем температуру в каждом прогнозе, если больше 0, добавляем +
            check_my_this_forecast_temp = round(my_this_forecast['temp'])
            if check_my_this_forecast_temp > 0:
                check_my_this_forecast_temp = '+' + str(check_my_this_forecast_temp)
            my_this_forecast_temp = str(check_my_this_forecast_temp)  # температура в первом прогнозе

            # проверяем температуру, которая ощущается в каждом прогнозе, если больше 0, добавляем +
            check_my_this_forecast_feels_like = round(my_this_forecast['feels_like'])
            if check_my_this_forecast_feels_like > 0:
                check_my_this_forecast_feels_like = '+' + str(check_my_this_forecast_feels_like)
            my_this_forecast_feels_like = ' ощущается как ' + str(check_my_this_forecast_feels_like)  # температура, как ощущается


            # my_this_forecast_wind_speed = 'Ветер:  ' + str(
            #     round(my_this_forecast['wind_speed'])) + ' м/с'  # скорость ветра
            my_this_forecast_rain = my_this_forecast['weather'][0]['description']  # осадки

            my_this_forecast_sum = my_this_forecast_time_human + '  ' + \
                                   my_this_forecast_temp + \
                                   ',' + my_this_forecast_feels_like + ', ' + my_this_forecast_rain

            all_forecast += my_this_forecast_sum + '\n'

            # print(my_this_forecast_sum)
            i = i + 1
        final_forecast = '\n\nПогода на ближайшие часы:\n' + all_forecast

        # === Отправка сообщения ботом пользователю =============
        bot.send_message(message.chat.id, "Координаты приняты, Ваш адрес:\n" + address_str +
        current_weather + final_forecast)

        # === Записываем координаты, которые получили от юзверя в текстовый файл
        message_for_txt_and_console = 'В такое-то время ' + 'получены координаты от юзверя с ником ' + message.from_user.username + ', id' + str(message.from_user.id) +', он находится тут: ' + address_str
        with open('location_log.txt', 'a') as f:
            f.write(str(message_for_txt_and_console))
            f.write('\n')

        # выводим то же самое в консоль
        print(message_for_txt_and_console)

bot.polling(none_stop=True)
input()

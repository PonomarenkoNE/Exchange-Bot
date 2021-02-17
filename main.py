import telebot
import requests
import model
from datetime import timedelta
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt


bot = telebot.TeleBot('1522630803:AAFMDzlyFXv7MQdrnnLigtFlMoUtPbURQNc')


@bot.message_handler(commands=['start'])
def start_bot(message):
    bot.send_message(message.chat.id, 'Hello, this is ExchangeBot\n\nYou can control me by sending these commands:'
                                      '\n\n\n/list - returns list of all available rates'
                                      '\n/exchange "num" "first_currency" to "second_currency" '
                                      '- converting "num" from "first_currency" to "second_currency"\n'
                                      'Example: /exchange 10 USD to CAD\n'
                                      '/history "first currency"/"second currency" - showing graph of exchange rate in'
                                      'last 7 days between "first currency" and "second currency"')


@bot.message_handler(commands=['list'])
def list_of_currency(message):
    try:
        obj = model.LastRequest.select()[0]
    except Exception:
        data = requests.get('https://api.exchangeratesapi.io/latest?base=USD').json()
        res = list()
        for el in data['rates']:
            rate = '{:.2f}'.format(float(data['rates'][el]))
            res.append(f'{el}: {rate}')
        model.create_db('\n'.join([str(elem) for elem in res]), datetime.now())
        bot.send_message(message.chat.id, '\n'.join([str(elem) for elem in res]))
        return
    if obj.time > datetime.now() - timedelta(minutes=10):
        bot.send_message(message.chat.id, obj.data)
        print(obj.time - timedelta(minutes=10))
    else:
        data = requests.get('https://api.exchangeratesapi.io/latest?base=USD').json()
        res = list()
        for el in data['rates']:
            rate = '{:.2f}'.format(float(data['rates'][el]))
            res.append(f'{el}: {rate}')
        model.update_db('\n'.join([str(elem) for elem in res]), datetime.now())
        print(2)
        bot.send_message(message.chat.id, '\n'.join([str(elem) for elem in res]))


@bot.message_handler(commands=['exchange'])
def exchange(message):
    parsing = message.text.split(' ')
    if len(parsing) != 5:
        bot.send_message(message.chat.id, 'Sorry, i dont understand')
        return
    if parsing[3] != 'to':
        bot.send_message(message.chat.id, 'Sorry, i dont understand')
        return
    try:
        float(parsing[1])
    except Exception:
        bot.send_message(message.chat.id, 'Sorry, i dont understand')
        return
    obj = requests.get(f'https://api.exchangeratesapi.io/latest?symbols={parsing[2]},{parsing[4]}').json()
    if 'error' in obj:
        bot.send_message(message.chat.id, 'Such currency dont exists')
        return
    res = float(parsing[1]) * (float(obj['rates'][parsing[4]]) / float(obj['rates'][parsing[2]]))
    bot.send_message(message.chat.id, str('{:.2f}'.format(res)) + ' ' + parsing[4])


@bot.message_handler(commands=['history'])
def history(message):
    parsing = message.text.split(' ')
    if len(parsing) != 2:
        bot.send_message(message.chat.id, 'Sorry, i dont understand')
        return
    cur_name = parsing[1][4:]
    obj = requests.get(f'https://api.exchangeratesapi.io/history?start_at={str(datetime.now() - timedelta(days=9))[:10]}'
                       f'&end_at={str(datetime.now())[:10]}'
                       f'&base={parsing[1][:3]}&symbols={cur_name}').json()
    if 'error' in obj:
        bot.send_message(message.chat.id, 'Some trouble in given currency')
        return
    rates = list()
    dates = list()
    for el in obj['rates']:
        dates.append(el)
        rates.append(float(obj['rates'][el][cur_name]))
    x = np.array([0, 1, 2, 3, 4, 5, 6])
    plt.xticks(x, dates)
    plt.xlabel('Dates')
    plt.ylabel('Rates')
    plt.title(f'{parsing[1]}')
    plt.plot(x, rates)
    plt.savefig('1.png')
    bot.send_photo(message.chat.id, photo=open('1.png', 'rb'))
    plt.close()


bot.polling()

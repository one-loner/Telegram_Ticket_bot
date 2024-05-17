import telebot
from telebot import types
import os, signal, pickle, sys, random, datetime

bot = telebot.TeleBot('Сюда вводим токен от бота')
global info
def extract_str(text, target_word):
    lines = text.split('\n')
    for line in lines:
        if line.strip().startswith(target_word):
            return line.strip()
    return f"No line starting with '{target_word}' found in the text."


@bot.message_handler(commands=['start'])
def user(message):
    try:
        oclf = open('/etc/telebot-ticket/'+str(message.chat.id),'r')
        ocl=oclf.read()
        arch = open('/etc/telebot-ticket/'+str(message.chat.id)+'.archive','a')
        arch.write('-------------------\n'+ocl)
        arch.close()
        namec = extract_str(ocl, 'Имя заказчика: ')
        cityc = extract_str(ocl, 'Город: ')
        phonec = extract_str(ocl, 'Телефон: ')
        idc = extract_str(ocl, 'ID пользователя: ')
        tgc = extract_str(ocl, 'Telegram: ')
        oclf.close()
        nr=namec+'\n'+cityc+'\nUsluganew\n'+phonec+'\n'+idc+'\n'+tgc
        nrec=open('/etc/telebot-ticket/'+str(message.chat.id),'w')
        nrec.write(nr)
        nrec.close()
        print(nr)
        sent = bot.send_message(message.chat.id, "Здравствуйте. Опишите возникшую у вас техническую проблему.")
        bot.register_next_step_handler(sent, addservices)
    except:
        sent = bot.send_message(message.chat.id, "Здравствуйте, данный бот предназначен для отправки заявок частному компьютерному мастеру. Как я могу к вам обращаться?")
        bot.register_next_step_handler(sent, city)
        doc1 = open('/etc/telebot-ticket/'+str(message.chat.id),'w')
        doc1.write('')

@bot.message_handler(content_types=['text'])
def city(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    user_markup.row('Москва', 'Подмосковье')
    cityname = bot.send_message(message.from_user.id, "Выберете ваш город.", reply_markup=user_markup)
    bot.register_next_step_handler(cityname, services)
    doc1 = open('/etc/telebot-ticket/'+str(message.chat.id), 'a')
    doc1.write("Имя заказчика: {name}\n".format(name=message.text))

@bot.message_handler(content_types=['text'])
def services(message):
    uslugi = bot.send_message(message.from_user.id, "Какие технические проблемы наблюдаются на вашем устройстве? Постарайтесь описать максимально подробно, чтобы наши специалисты смогли точнее определить проблему.") #, reply_markup=user_markup)
    bot.register_next_step_handler(uslugi, telephone)
    doc1 = open('/etc/telebot-ticket/'+str(message.chat.id), 'a')
    doc1.write("Город: #{city}\n".format(city=message.text))

def telephone(message):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    reg_button = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
    keyboard.add(reg_button)
    nomer = bot.send_message(message.chat.id, 'Оставьте ваш контактный номер чтобы наш специалист смог связаться с вами.', reply_markup=keyboard)
    bot.register_next_step_handler(nomer, save)
    doc1 = open('/etc/telebot-ticket/'+str(message.chat.id), 'a')
    doc1.write("Заявка: {service}\n".format(service=message.text))


def save(message):
    try:
        nz = random.randint(1000000, 9999999)
        user_info = bot.get_chat_member(message.chat.id, message.from_user.id)
        usn = user_info.user.username
        usid = user_info.user.id
        now_datetime = datetime.datetime.now()
        current_datetime = now_datetime.strftime("%H:%M %d.%m.%Y")
        doc1 = open('/etc/telebot-ticket/'+str(message.chat.id), 'a')
        doc1.write("Телефон: {telephon}\n".format(telephon=message.contact.phone_number))
        doc1.write("ID пользователя: {uid}\n".format(uid=usid))
        doc1.write("Telegram: @{un}\n".format(un=usn))
        doc1.close()
        doc2 = open('/etc/telebot-ticket/'+str(message.chat.id), 'r')
        t="Номер заявки: {ticket}\n".format(ticket='#'+str(nz))+"Создана: {now}\n".format(now=current_datetime) + doc2.read()
        doc2.close()
        doc3 = open('/etc/telebot-ticket/'+str(message.chat.id), 'w')
        doc3.write(t)
        doc3.close()
        bot.send_message('<Сюда вводим id чата, в который будут поступать заявки>', t)
        user_markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        user_markup.row('/start')
        newticket = bot.send_message(message.chat.id, 'Спасибо за обращение. Номер вашей заявки '+str(nz)+'. Мы свяжемся с вами в ближайшее время. Если вы хотите оставить ещё одну заявку нажмите /start', reply_markup=user_markup)
        bot.register_next_step_handler(newticket, user)
    except:
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        reg_button = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
        keyboard.add(reg_button)
        nomer = bot.send_message(message.chat.id, 'Оставьте ваш контактный номер чтобы наш специалист смог связаться с вами. Нажмите на кнопку Отправить номер телефона, а затем поделиться.', reply_markup=keyboard)  
        bot.register_next_step_handler(nomer, save)


def rest(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    user_markup.row('/start')
    sent= bot.send_message(message.from_user.id, "Нажмите или введите /start для добавления новой заявки.", reply_markup=user_markup)

    if message.text=='/start':
       bot.register_next_step_handler(sent, user)
    else:
       bot.register_next_step_handler(sent, rest)

def addservices(message):
     oclf = open('/etc/telebot-ticket/'+str(message.chat.id),'r')
     ocl=oclf.read()
     oclf.close()
     ocl=ocl.replace('Usluganew',"Заявка: {service}".format(service=message.text))
     now_datetime = datetime.datetime.now()
     current_datetime = now_datetime.strftime("%H:%M %d.%m.%Y")
     nzn = random.randint(1000000, 9999999)
     nz = 'Номер заявки: #'+str(nzn)+'\nСоздана - '+str(current_datetime)+'\n'+ocl
     print(nz)
     bot.send_message('<Сюда вводим id чата, в который будут поступать заявки>', nz)
     nzw=open('/etc/telebot-ticket/'+str(message.chat.id),'w')
     nzw.write(nz)
     nzw.close()
     user_markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
     user_markup.row('/start')
     newticket = bot.send_message(message.chat.id, 'Спасибо за обращение. Номер вашей заявки '+str(nzn)+'. Мы свяжемся с вами в ближайшее время. Если вы хотите оставить ещё одну заявку, нажмите /start', reply_markup=user_markup)
     bot.register_next_step_handler(newticket, user)



if __name__ == '__main__':
     bot.infinity_polling(none_stop=True)


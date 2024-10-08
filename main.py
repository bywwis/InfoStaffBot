import telebot
import sqlite3 as sl
from telebot import types
import datetime
from datetime import datetime

bot = telebot.TeleBot('7420367939:AAEvcAYcINdSu5wPSWJuhOJ_rWIfYr2OIkU')
con = sl.connect('database.db')

with con:
    data = con.execute("SELECT COUNT(*) FROM sqlite_master WHERE TYPE='table' AND NAME='staff'")
    for row in data:
        if row[0] == 0:
            with con:
                con.execute("""
                                    CREATE TABLE staff (
                                        staffid VARCHAR(200) PRIMARY KEY,
                                        surname VARCHAR(200),
                                        name VARCHAR(200),
                                        patronymic VARCHAR(200),
                                        post VARCHAR(200),
                                        project VARCHAR(200),
                                        datearrival VARCHAR(20)
                                    );
                                """)


@bot.message_handler(commands=['add'])
def add_surname(message):
    msg = bot.send_message(message.chat.id, 'Введите фамилию сотрудника')
    bot.register_next_step_handler(msg, save_surname)


def save_surname(message):
    global surname
    surname = message.text
    if surname.isdigit():
        msg = bot.send_message(message.chat.id, "Буквами, пожалуйста")
        bot.register_next_step_handler(msg, save_surname)
    elif surname == '-':
        msg = bot.send_message(message.chat.id, "Это поле обязательно для заполнения. Введите фамилию.")
        bot.register_next_step_handler(msg, save_surname)
    else:
        add_name(message)


def add_name(message):
    msg = bot.send_message(message.chat.id, 'Введите имя сотрудника')
    bot.register_next_step_handler(msg, save_name)


def save_name(message):
    global name
    name = message.text
    if name.isdigit():
        msg = bot.send_message(message.chat.id, "Буквами, пожалуйста")
        bot.register_next_step_handler(msg, save_name)
    elif name == '-':
        msg = bot.send_message(message.chat.id, "Это поле обязательно для заполнения. Введите имя.")
        bot.register_next_step_handler(msg, save_name)
    else:
        add_patronymic(message)


def add_patronymic(message):
    msg = bot.send_message(message.chat.id, 'Введите отчество сотрудника (если нет, поставьте -)')
    bot.register_next_step_handler(msg, save_patronymic)


def save_patronymic(message):
    global patronymic
    patronymic = message.text
    if patronymic.isdigit():
        msg = bot.send_message(message.chat.id, "Буквами, пожалуйста")
        bot.register_next_step_handler(msg, save_patronymic)
    else:
        add_post(message)


def add_post(message):
    msg = bot.send_message(message.chat.id, 'Введите должность сотрудника')
    bot.register_next_step_handler(msg, save_post)


def save_post(message):
    global post
    post = message.text
    if post == '-':
        msg = bot.send_message(message.chat.id, "Это поле обязательно для заполнения. Введите должность.")
        bot.register_next_step_handler(msg, save_post)
    else:
        add_project(message)


def add_project(message):
    msg = bot.send_message(message.chat.id, 'Введите проект сотрудника')
    bot.register_next_step_handler(msg, save_project)


def save_project(message):
    global project
    project = message.text
    if project == '-':
        msg = bot.send_message(message.chat.id, "Это поле обязательно для заполнения. Введите проект.")
        bot.register_next_step_handler(msg, save_project)
    else:
        add_date_arrival(message)


def add_date_arrival(message):
    msg = bot.send_message(message.chat.id, 'Введите дату прихода сотрудника в формате ДД.ММ.ГГГГ (если нет, поставьте -)')
    bot.register_next_step_handler(msg, save_date_arrival)


def save_date_arrival(message):
    global datearrival
    datearrival = message.text
    if datearrival != '-':
        try:
            datearrival = datetime.datetime.strptime(message.text, "%d.%m.%Y").date()
            add_staffid(message)
        except ValueError:
            msg = bot.send_message(message.chat.id, "Неверный формат даты. Введите дату в формате DD.MM.YYYY:")
            bot.register_next_step_handler(msg, save_date_arrival)
    else:
        add_staffid(message)


def add_staffid(message):
    msg = bot.send_message(message.chat.id, 'Введите id сотрудника')
    bot.register_next_step_handler(msg, save_staffid)


def save_staffid(message):
    global staffid
    staffid = message.text
    con = sl.connect('database.db')
    with con:
        data = con.execute("SELECT staffid FROM staff WHERE staffid = ?", (staffid,)).fetchone()
        if data:
            msg = bot.send_message(message.chat.id, "Сотрудник с таким ID уже есть. Повторите попытку.")
            bot.register_next_step_handler(msg, save_staffid)
            return
    if not staffid.isdigit():
        msg = bot.send_message(message.chat.id, "Цифрами, пожалуйста.")
        bot.register_next_step_handler(msg, save_staffid)
    elif len(staffid) > 5:
        msg = bot.send_message(message.chat.id, "ID не должен превышать 5 цифр.")
        bot.register_next_step_handler(msg, save_staffid)
    else:
        func(message, surname, name, patronymic, post, project, datearrival, staffid)


def func(message, surname, name, patronymic, post, project, datearrival, staffid):
    con = sl.connect('database.db')
    with con:
        con.execute("INSERT INTO staff (staffid, surname, name, patronymic, post, project, datearrival) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (staffid, surname, name, patronymic, post, project, datearrival))
    bot.send_message(message.from_user.id, 'Принято, спасибо!', parse_mode='Markdown')


@bot.message_handler(commands=['delete'])
def delete_staff(message):
    con = sl.connect('database.db')
    with con:
        data = con.execute("SELECT staffid, surname, name, patronymic, post, project, datearrival FROM staff")
        staff_list = []
        for row in data:
            staff_list.append(f"ID сотрудника - {row[0]}\nФИО - {row[1]} {row[2]} {row[3]}\nдолжность - {row[4]}\nпроект - {row[5]}\nдата прихода сотрудника - {row[6]}\n")
        if staff_list == []:
            bot.send_message(message.chat.id, "Нет доступных сотрудников для удаления. Добавьте сотрудника с помощью команды /add.")
        else:
            msg = bot.send_message(message.chat.id, "Введите ID сотрудника, котрого нужно удалить:\n" + "\n".join(staff_list))
            bot.register_next_step_handler(msg, confirm_delete)


def confirm_delete(message):
    staffid = message.text
    con = sl.connect('database.db')
    with con:
        data = con.execute("SELECT staffid FROM staff WHERE staffid = ?", (staffid,)).fetchone()
        if data:
            with con:
                con.execute("DELETE FROM staff WHERE staffid = ?", (staffid,))
            bot.send_message(message.chat.id, "Сотрудник удален.")
        else:
            bot.send_message(message.chat.id, "Неверный выбор. Введите команду снова.")


@bot.message_handler(commands=['edit'])
def edit_staff(message):
    con = sl.connect('database.db')
    with con:
        data = con.execute("SELECT staffid, surname, name, patronymic, post, project, datearrival FROM staff")
        staff_list = []
        for row in data:
            staff_list.append(
                f"ID сотрудника - {row[0]}\nФИО - {row[1]} {row[2]} {row[3]}\nдолжность - {row[4]}\nпроект - {row[5]}\nдата прихода сотрудника - {row[6]}\n")
        if not staff_list:
            bot.send_message(message.chat.id, "Нет доступных сотрудников для редактирования. Добавьте сотрудника с помощью команды /add.")
        else:
            msg = bot.send_message(message.chat.id, "Введите ID сотрудника, которого нужно отредактировать:\n" + "\n".join(staff_list))
            bot.register_next_step_handler(msg, edit_surname)


def edit_surname(message):
    global staff_id
    staff_id = message.text.strip()
    con = sl.connect('database.db')
    with con:
        data = con.execute("SELECT staffid FROM staff WHERE staffid = ?", (staff_id,)).fetchone()
        if data:
            msg = bot.send_message(message.chat.id, "Введите новую фамилию сотрудника.")
            bot.register_next_step_handler(msg, edit_name)
        else:
            bot.send_message(message.chat.id, "Неверный выбор. Введите команду снова.")


def edit_name(message):
    global surname
    surname = message.text
    if surname.isdigit():
        msg = bot.send_message(message.chat.id, "Буквами, пожалуйста.")
        bot.register_next_step_handler(msg, edit_name)
    elif surname == '-':
        msg = bot.send_message(message.chat.id, "Это поле обязательно для заполнения. Введите фамилию.")
        bot.register_next_step_handler(msg, edit_name)
    else:
        msg = bot.send_message(message.chat.id, "Введите новое имя сотрудника.")
        bot.register_next_step_handler(msg, edit_patronymic)


def edit_patronymic(message):
    global name
    name = message.text
    if name.isdigit():
        msg = bot.send_message(message.chat.id, "Буквами, пожалуйста")
        bot.register_next_step_handler(msg, edit_patronymic)
    elif name == '-':
        msg = bot.send_message(message.chat.id, "Это поле обязательно для заполнения. Введите имя.")
        bot.register_next_step_handler(msg, edit_patronymic)
    else:
        msg = bot.send_message(message.chat.id, "Введите новое отчество сотрудника (если нет, поставьте -).")
        bot.register_next_step_handler(msg, edit_post)


def edit_post(message):
    global patronymic
    patronymic = message.text
    if patronymic.isdigit():
        msg = bot.send_message(message.chat.id, "Буквами, пожалуйста.")
        bot.register_next_step_handler(msg, edit_post)
    else:
        msg = bot.send_message(message.chat.id, "Введите новую должность сотрудника.")
        bot.register_next_step_handler(msg, edit_project)


def edit_project(message):
    global post
    post = message.text
    if post == '-':
        msg = bot.send_message(message.chat.id, "Это поле обязательно для заполнения. Введите должность.")
        bot.register_next_step_handler(msg, edit_project)
    else:
        msg = bot.send_message(message.chat.id, "Введите новый проект сотрудника.")
        bot.register_next_step_handler(msg, edit_date_arrival)


def edit_date_arrival(message):
    global project
    project = message.text
    if project == '-':
        msg = bot.send_message(message.chat.id, "Это поле обязательно для заполнения. Введите проект.")
        bot.register_next_step_handler(msg, edit_date_arrival)
    else:
        msg = bot.send_message(message.chat.id, "Введите новую дату прихода сотрудника (если нет, поставьте -)")
        bot.register_next_step_handler(msg, save_edit)


def save_edit(message):
    global datearrival
    datearrival = message.text
    if datearrival != '-':
        try:
            datearrival = datetime.datetime.strptime(message.text, "%d.%m.%Y").date()
            update(message, surname, name, patronymic, post, project, datearrival)
        except ValueError:
            msg = bot.send_message(message.chat.id, "Неверный формат даты. Введите дату в формате DD.MM.YYYY:")
            bot.register_next_step_handler(msg, save_edit)
    else:
        update(message, surname, name, patronymic, post, project, datearrival)


def update(message, surname, name, patronymic, post, project, datearrival):
    con = sl.connect('database.db')
    with con:
        con.execute("UPDATE staff SET surname = ?, name = ?, patronymic = ?, post = ?, project = ?, datearrival = ? WHERE staffid = ?",
                    (surname, name, patronymic, post, project, datearrival, staff_id))
    bot.send_message(message.chat.id, "Данные сотрудника обновлены.")


@bot.message_handler(commands=['search'])
def search_staff(message):
    msg = bot.send_message(message.chat.id, "Введите ФИО или ID сотрудника для поиска.")
    bot.register_next_step_handler(msg, handle_search)


def handle_search(message):
    search_query = message.text.strip()
    con = sl.connect('database.db')
    with con:
        if search_query.isdigit():
            data = con.execute("SELECT staffid, surname, name, patronymic, post, project, datearrival FROM staff WHERE staffid = ?", (search_query,)).fetchone()
            if data:
                staff_info = f"ID сотрудника - {data[0]}\nФИО - {data[1]} {data[2]} {data[3]}\nдолжность - {data[4]}\nпроект - {data[5]}\nдата прихода сотрудника - {data[6]}"
                bot.send_message(message.chat.id, staff_info)
            else:
                bot.send_message(message.chat.id, "Сотрудник не найден. Проверьте введенные данные.")
        else:
            search_query_parts = search_query.split()
            if len(search_query_parts) == 3:
                data = con.execute("SELECT staffid, surname, name, patronymic, post, project, datearrival FROM staff WHERE surname = ? AND name = ? AND patronymic = ?", search_query_parts).fetchall()
            elif len(search_query_parts) == 2:
                data = con.execute("SELECT staffid, surname, name, patronymic, post, project, datearrival FROM staff WHERE surname = ? AND name = ?", search_query_parts).fetchall()
            else:
                data = con.execute("SELECT staffid, surname, name, patronymic, post, project, datearrival FROM staff WHERE surname = ?", (search_query,)).fetchall()

            if data:
                for row in data:
                    staff_info = f"ID сотрудника - {row[0]}\nФИО - {row[1]} {row[2]} {row[3]}\nдолжность - {row[4]}\nпроект - {row[5]}\nдата прихода сотрудника - {row[6]}"
                    bot.send_message(message.chat.id, staff_info)
            else:
                bot.send_message(message.chat.id, "Сотрудник не найден. Проверьте введенные данные.")



@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Добавить сотрудника")
    btn2 = types.KeyboardButton("Удалить сотрудника")
    btn3 = types.KeyboardButton("Редактировать сотрудника")
    btn4 = types.KeyboardButton("Найти сотрудника")
    markup.add(btn1, btn2, btn3, btn4)

    bot.send_message(message.chat.id, 'Вас приветствует Info Staff Bot! Чтобы ознакомиться со списком доступных команд введите команду /help.', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def button_start(message):
    if message.text == "Добавить сотрудника":
        add_surname(message)
    elif message.text == "Удалить сотрудника":
        delete_staff(message)
    elif message.text == "Редактировать сотрудника":
        edit_staff(message)
    elif message.text == "Найти сотрудника":
        search_staff(message)
    else:
        bot.send_message(message.chat.id, text="На такую команду я не запрограммирован...")


@bot.message_handler(commands=['help'])
def helps(message):
    bot.send_message(message.chat.id, 'Сведения о доступных командах: \n'
                                    '/add - добавить сотрудника \n'
                                    '/help - список доступных команд \n'
                                    '/delete - удалить данные о сотруднике \n'
                                    '/edit - редактировать данные о сотруднике \n'
                                    '/search - поиск сотрудника')


if __name__ == '__main__':
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        print('Непредвиденная ошибка. Попробуйте повторить запрос позже.')
import telebot
import sqlite3 as sl

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


def errors(message):
    bot.send_message(message.chat.id, 'Непредвиденная ошибка. Попробуйте повторить запрос позже.')


@bot.message_handler(commands=['add'])
def add_surname(message):
    msg = bot.send_message(message.chat.id, 'Введите фамилию сотрудника')
    bot.register_next_step_handler(msg, save_surname)


def save_surname(message):
    global surname
    surname = message.text
    add_name(message)


def add_name(message):
    msg = bot.send_message(message.chat.id, 'Введите имя сотрудника')
    bot.register_next_step_handler(msg, save_name)


def save_name(message):
    global name
    name = message.text
    add_patronymic(message)


def add_patronymic(message):
    msg = bot.send_message(message.chat.id, 'Введите отчество сотрудника (если нет, поставьте -)')
    bot.register_next_step_handler(msg, save_patronymic)


def save_patronymic(message):
    global patronymic
    patronymic = message.text
    add_post(message)


def add_post(message):
    msg = bot.send_message(message.chat.id, 'Введите должность сотрудника')
    bot.register_next_step_handler(msg, save_post)


def save_post(message):
    global post
    post = message.text
    add_project(message)


def add_project(message):
    msg = bot.send_message(message.chat.id, 'Введите проект сотрудника')
    bot.register_next_step_handler(msg, save_project)


def save_project(message):
    global project
    project = message.text
    add_date_arrival(message)


def add_date_arrival(message):
    msg = bot.send_message(message.chat.id, 'Введите дату прихода сотрудника')
    bot.register_next_step_handler(msg, save_date_arrival)


def save_date_arrival(message):
    global datearrival
    datearrival = message.text
    add_staffid(message)


def add_staffid(message):
    msg = bot.send_message(message.chat.id, 'Введите id сотрудника')
    bot.register_next_step_handler(msg, save_staffid)


def save_staffid(message):
    global staffid
    staffid = message.text
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
    staff_id = message.text.strip()
    con = sl.connect('database.db')
    with con:
        data = con.execute("SELECT staffid FROM staff WHERE staffid = ?", (staff_id,)).fetchone()
        if data:
            with con:
                con.execute("DELETE FROM staff WHERE staffid = ?", (staff_id,))
            bot.send_message(message.chat.id, "Сотрудник удален.")
        else:
            bot.send_message(message.chat.id, "Неверный выбор. Введите команду снова.")


# надо чтобы пользователь выбрал что изменить
@bot.message_handler(commands=['edit'])
def edit_staff(message):
    con = sl.connect('database.db')
    with con:
        data = con.execute("SELECT staffid, surname, name, patronymic, post, project, datearrival FROM staff")
        staff_list = []
        for row in data:
            staff_list.append(
                f"ID сотрудника | {row[0]} | ФИО | {row[1]} {row[2]} {row[3]} | должность | {row[4]} | проект | {row[5]} | дата прихода сотрудника | {row[6]}\n")
        if staff_list == []:
            bot.send_message(message.chat.id, "Нет доступных сотрудников для редактирования. Добавьте сотрудника с помощью команды /add.")
        else:
            msg = bot.send_message(message.chat.id,
                                "Введите ID сотрудника, которого нужно отредактировать:\n" + "\n".join(staff_list))
            bot.register_next_step_handler(msg, confirm_edit)


def add_new_staff(message):
    add_surname(message)
    save_surname(message)
    add_name(message)
    save_name(message)
    add_patronymic(message)
    save_patronymic(message)
    add_post(message)
    save_post(message)
    add_project(message)
    save_project(message)
    add_date_arrival(message)
    save_date_arrival(message)
    add_staffid(message)
    save_staffid(message)
    new_data(message, surname, name, patronymic, post, project, datearrival, staffid)


def confirm_edit(message):
    staff_id = message.text.strip()
    con = sl.connect('database.db')
    with con:
        data = con.execute("SELECT staffid FROM staff WHERE staffid = ?", (staff_id,)).fetchone()

        if data:
            msg = bot.send_message(message.chat.id, "Введите новые данные для сотрудника.")
            bot.register_next_step_handler(msg, add_new_staff)
        else:
            bot.send_message(message.chat.id, "Неверный выбор. Введите команду снова.")


def new_data(message, surname, name, patronymic, post, project, datearrival, staffid):
    con = sl.connect('database.db')
    with con:
        con.execute("UPDATE staff SET surname = ?, name = ?, patronymic = ?, post = ?, project = ?, datearrival = ? WHERE staffid = ?",
                    (surname, name, patronymic, post, project, datearrival, staffid))
    bot.send_message(message.chat.id, "Данные сотрудника обновлены.")


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Вас приветствует Info Staff Bot! Чтобы ознакомиться со списком доступных команд введите команду /help.')


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
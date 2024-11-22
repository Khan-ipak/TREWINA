import telebot
import buttons, database


# Создаем объект бота
bot = telebot.TeleBot('7625220401:AAFWIJqVqcFkkEgyu7-rQrMBi-7WbAa6_eA')


# Обработки команды /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if database.check_user(user_id):
        bot.send_message(user_id, f'Добро пожаловать, @{message.from_user.username}!',
                         reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.send_message(user_id, 'Выберите пункт меню:',
                         reply_markup=buttons.main_menu(database.get_pr_buttons()))
    else:
        bot.send_message(user_id, 'Привет! Давай начнем регистрацию! \nНапиши свое имя',
                         reply_markup=telebot.types.ReplyKeyboardRemove())
        # Переход на этап получения имени
        bot.register_next_step_handler(message, get_name)


# Получение имени
def get_name(message):
    user_id = message.from_user.id
    user_name = message.text
    bot.send_message(user_id, 'Отлично! Теперь отправь свой номер!',
                     reply_markup=buttons.num_button())
    # Переход на этап получения номера
    bot.register_next_step_handler(message, get_num, user_name)


# Получение номера
def get_num(message, user_name):
    user_id = message.from_user.id
    # Если отправил номер в виде номера
    if message.contact:
        user_num = message.contact.phone_number
        # Заносим пользователя в БД
        database.register(user_id, user_name, user_num)
        bot.send_message(user_id, 'Регистрация прошла успешно!',
                         reply_markup=telebot.types.ReplyKeyboardRemove())
    # Если пользователь написал в виде текста
    else:
        bot.send_message(user_id, 'Отправьте контакт по кнопке или отправьте контакт через скрепку!')
        # Возврат на этап получения номера
        bot.register_next_step_handler(message, get_num, user_name)


@bot.callback_query_handler(lambda call: int(call.data) in [i[0] for i in database.get_all_pr()])
def choose_pr_count(call):
    # Определяем id пользователя
    user_id = call.message.chat.id
    # Достаем всю информацию о выбранном товаре
    pr_info = database.get_exact_pr(int(call.data))
    # Удаляем сообщение с выбором в меню
    bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
    # Отправляем фото товара и его описание
    bot.send_photo(user_id, photo=pr_info[-1], caption=f'{pr_info[1]}\n\n'
                   f'Описание: {pr_info[2]}\n'
                   f'Количество: {pr_info[4]}\n'
                   f'Цена: {pr_info[3]}сум')


# Обработчик команды /admin
@bot.message_handler(commands=['admin'])
def admin(message):
    if message.from_user.id == 762087553:
        admin_id = message.from_user.id
        bot.send_message(admin_id, 'Добро пожаловать в админ панели!', reply_markup=buttons.admin_menu())
        # Переход на этап выбора
        bot.register_next_step_handler(message, choice)
    else:
        bot.send_message(message.from_user.id, 'Вы не администратор!')


# Этап выбора
def choice(message):
    admin_id = message.from_user.id
    if message.text == 'Добавить продукт':
        bot.send_message(admin_id, 'Напишите данные о продукте в следующем виде:\n\n'
                        'Название, Описание, Цена, Количество, Ссылка на фото \n\n'
                        'Фотограции можно загрузить на сайте https://postimages.org/,'
                        'скопировав прямую ссылку!', reply_markup=telebot.types.ReplyKeyboardRemove())
        # Переход на этап получения товара
        bot.register_next_step_handler(message, add_product)


# Добавление товара
def add_product(message):
    admin_id = message.from_user.id
    pr_attrs = message.text.split(', ')
    database.pr_to_db(pr_attrs[0], pr_attrs[1], pr_attrs[2], pr_attrs[3], pr_attrs[4])
    bot.send_message(admin_id, 'Готово!')



bot.polling(non_stop=True)
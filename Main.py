import telebot
from Info import setting
from telebot import types
import sqlite3

#* Это файл с основной логикой бота.
#* Здесь мы будем обрабатывать все запросы от нашего клиента
#* Наш клиент будет ООП объектом, с которым мы будем общаться через методы его класса




class Client:
    #инициализация класса
    def __init__(self, id=''):
        self.id = id
        self.conn = sqlite3.connect('BASE.db', check_same_thread=False)
        self.cur = self.conn.cursor()


    def add_into_base(self, sqlite_insert_query, test=False):
        self.cur.execute(sqlite_insert_query)
        if not test:
            self.conn.commit()

    # выдаём количество Coins
    def get_budget(self):
        self.cur.execute(f"SELECT budget FROM users WHERE userid = ?", (self.id, ))
        one_result = self.cur.fetchone()
        #print(one_result)
        return one_result[0]

    def change_team(self, names_teams): #["team1", "team2"]
        #print(teams_spisok, 'gay2')
        self.cur.execute("DELETE FROM bets")
        self.add_into_base(f'INSERT INTO bets(team, bet, condition) VALUES("{names_teams[0]}", 1, "NotState");')
        self.add_into_base(f'INSERT INTO bets(team, bet, condition) VALUES("{names_teams[1]}", 1, "NotState");')

        self.conn.commit()

    def Koeff(self):
        self.cur.execute("SELECT * FROM bets;")
        one_result = self.cur.fetchall()
        first = round(one_result[1][1]/one_result[0][1], 2)
        second = round(one_result[0][1]/one_result[1][1], 2)
        if first < 1.5:
            first = 1.5
        if second < 1.5:
            second = 1.5
        return (first, second)

    def Teams(self):
        self.cur.execute("SELECT * FROM bets;")
        one_result = self.cur.fetchall()
        print(one_result, 'бумага')
        try:
            return [one_result[0][0], one_result[1][0]]
        except Exception:
            return ['', '']

    def End(self, conditions_teams): # строго в том порядке, в каком пишется на place_a_bet.
        # conditions_teams = [1, 0]
        self.cur.execute("SELECT * FROM bets;")
        one_result = self.cur.fetchall()
        if conditions_teams == [2, 2]:
            self.add_into_base(f"UPDATE bets SET condition = 'NotState' WHERE team = '{one_result[0][0]}'")
            self.add_into_base(f"UPDATE bets SET condition = 'NotState' WHERE team = '{one_result[1][0]}'")
            #удаление банка
            self.add_into_base(f"UPDATE bets SET bet = 1 WHERE team = '{one_result[0][0]}'")
            self.add_into_base(f"UPDATE bets SET bet = 1 WHERE team = '{one_result[1][0]}'")
        else:
            self.add_into_base(f"UPDATE bets SET condition = '{conditions_teams[0]}' WHERE team = '{one_result[0][0]}'")
            self.add_into_base(f"UPDATE bets SET condition = '{conditions_teams[1]}' WHERE team = '{one_result[1][0]}'")

    def AllEnd(self):
        #начисление выйгранных монет игрокам
        self.cur.execute("SELECT * FROM bets;")
        one_result = self.cur.fetchall()
        second_result = self.cur.execute('SELECT teams FROM users WHERE userid=?', (int(self.id),)).fetchall() #значение на какую команду ставил
        # сравнение он выйграл или проиграл
        condition_user = ''
        number_team = 0
        for i in range(2):
            if one_result[i][0] == second_result[0][0]:
                if one_result[i][2] == "1":
                    condition_user = "Win"
                    number_team = i
                elif one_result[i][2] == "0":
                    condition_user = "Lose"
        if condition_user == 'Win':
            user_bet = self.cur.execute('SELECT bet FROM users WHERE userid=?', (int(self.id),)).fetchall()[0][0]
            winners_budget = user_bet * self.Koeff()[number_team]
            self.add_into_base(f"UPDATE users SET budget = {winners_budget + self.get_budget()} WHERE userid = '{self.id}';")

        #удаление данных о ставках
        self.cur.execute("SELECT userid FROM users;")
        one_result = [i[0] for i in self.cur.fetchall()]
        print(one_result, "LOLOLOLO")
        for i in one_result:
            self.add_into_base(f"UPDATE users SET bet = 0 WHERE userid = '{i}';")
            self.add_into_base(f"UPDATE users SET teams = '0' WHERE userid = '{i}';")

        #удаление значений победы команд и изменения на NotState
        self.End([2, 2])


    def registration(self, test=False): # test используется выше чтобы не коммитить пользователя
        # проверка есть ли userid в таблице users
        info = self.cur.execute('SELECT userid FROM users WHERE userid=?', (int(self.id),))
        if info.fetchone() is None:
            # если человека нету в бд
            none_team = "noneteam"
            self.add_into_base(f"INSERT INTO users VALUES({int(self.id)}, 100, 0, '0');")
            return "Added"
        else:
            # если человек есть в бд
            return "Been"


    def new_bet(self, bet, team): # деньги снимаются у чела и приходят на команду, нужно сделать кэффициент
        # блок взятие денег из кошелька
        self.cur.execute(f"SELECT bet FROM users WHERE userid = ?", (self.id, ))
        one_result = self.cur.fetchone()[0]
        self.cur.execute(f"SELECT teams FROM users WHERE userid = ?", (self.id, ))
        one_result2 = self.cur.fetchone()[0]
        if one_result == 0 and one_result2 == '0':
            money = self.get_budget()
            if money >= bet:
                self.add_into_base(f"UPDATE users SET budget = {money - bet} WHERE userid = '{self.id}'")
            else:
                return "Недостаточно средств"
            # блок пополнения суммарной ставки команды
            packet = self.cur.execute(f"SELECT bet FROM bets WHERE team = ?", (team, ))
            one_result = self.cur.fetchone()[0]
            #print(one_result, "соси")
            self.add_into_base(f"UPDATE bets SET bet = {one_result + bet} WHERE team = '{team}'")
            self.add_into_base(f"UPDATE users SET bet = {bet} WHERE userid = '{self.id}';")
            self.add_into_base(f"UPDATE users SET teams = '{team}' WHERE userid = '{self.id}';")
            return "Успешно"
        else:
            return "False"


    #далее тут будет находиться вспомогательная информация по классу
    def __str__(self):
        return """
        * Это файл с основной логикой бота.
        * Здесь мы будем обрабатывать все запросы от нашего клиента
        * Наш клиент будет ООП объектом, с которым мы будем общаться через методы его класса
        * Методы:
        **get_budget - возвращает нам int объект с количеством денег на счету
        **__str__ - выводит string информацию по классу
        """


# stikers links
ok = open("ok.webp", 'rb')
notOk = open("f.webp", 'rb')
notOk2 = open("f2.webp", 'rb')



client = Client()

# Инициализация бота и основные обработчики комманд,основная логика в Obj
bot = telebot.TeleBot(setting["token"]);
Bet = {}

# call back
Money = 0


#teams what we have
teams = []
choose_team = ''

def teams_check():
    global teams
    print(teams)
    if teams == client.Teams():
        return False
    else:
        teams = client.Teams()
        return True
teams_check()


#koeff what we have
koeff = []

def koeff_check():
    global koeff
    print(koeff)
    if koeff == client.Koeff():
        return False
    else:
        koeff = client.Koeff()
        return True


HELP = """
**********HELP**********
*Наши стикеры: https://t.me/addstickers/adadigitalnoise
*/start - создаём ваш аккаунт <3
* помощь - команда выводит информацию о возможностях бота
* бюджет - количество ваших Coins
*/bet (размер ставки) - сделать ставку
************************
"""


@bot.callback_query_handler(func=lambda call: call.data == 'cbTeam1')
def cb_buttonTeam1(message: types.Message):
    global choose_team, teams, Money
    #пачка обновления даныых
    client.id = str(message.from_user.id)
    if teams_check():
        bot.send_message(message.from_user.id, "Команды сменились!", reply_markup=keyboards(["бюджет", "помощь"]))

    choose_team = teams[0]
    bot.delete_message(message.from_user.id, message.message.message_id)
    bot.send_message(message.from_user.id, f"Ваш бюджет: {client.get_budget()}, ставка: {Money}")
    if client.new_bet(Money, choose_team) == "False":
        bot.send_message(message.from_user.id, "Ошибка! Вы уже делали ставку. Ждите результатов.")
        bot.send_sticker(message.from_user.id, open("f.webp", 'rb'))
    else:
        bot.send_sticker(message.from_user.id, open("ok.webp", 'rb'))

@bot.callback_query_handler(func=lambda call: call.data == 'cbTeam2')
def cb_buttonTeam1(message: types.Message):
    global choose_team, teams
    #пачка обновления даныых
    client.id = str(message.from_user.id)
    if teams_check():
        bot.send_message(message.from_user.id, "Команды сменились!", reply_markup=keyboards(["бюджет", "помощь"]))
    choose_team = teams[1]
    bot.delete_message(message.from_user.id, message.message.message_id)
    bot.send_message(message.from_user.id, f"Ваш бюджет: {client.get_budget()}, ставка: {Money}")
    if client.new_bet(Money, choose_team) == "False":
        bot.send_message(message.from_user.id, "Ошибка! Вы уже делали ставку. Ждите результатов.")
        bot.send_sticker(message.from_user.id, open("f2.webp", 'rb'))
    else:
        bot.send_sticker(message.from_user.id, open("ok.webp", 'rb'))



def keyboards(spisok):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*spisok)
    return keyboard



def take_bet(message):
    global CBET10, CBET1
    if CBET1:
        CBET1 = False

    elif CBET10:
        CBET10 = False
        client.new_bet(10, choose_team)
    bot.send_message(message.from_user.id, f"Ваш бюджет: {client.get_budget()}",reply_markup=keyboards(["помощь"]))



@bot.message_handler(content_types=["text"])
def get_text_messages(message):
    global teams, choose_team, Money, koeff
    client.id = str(message.chat.id)
    if teams_check():
        bot.send_message(message.from_user.id, "Команды сменились!", reply_markup=keyboards(["бюджет", "помощь"]))
    koeff_check()


    # класс с методами работы в базе данных




    # chech how much money
    def check_money():
        answer = client.registration()
        if answer == "Been":
            pass
        elif answer == "Added":
            pass


    #print(str(message.chat.id) + " " + message.from_user.username + ": " + message.text)
    print(message.text)

    if message.text in ["Привет", "привет", "сап", "s"]:
        bot.send_message(message.from_user.id, "Привет, введи 'помощь' для информации о моих возможностях", reply_markup=keyboards(["бюджет", "помощь"]))
    elif "@end" in message.text:
        command = message.text.split()
        if len(command) > 5 or len(command) < 5:
            bot.send_message(message.from_user.id, "Ошибка! Пример записи: команда <значение1> <значение2> <название1> <название2>")
        elif not command[1].isdigit() or not command[2].isdigit():
            bot.send_message(message.from_user.id, "Ошибка! Пример записи: команда <значение1 тип данных число(1 или 0)> <значение2 тип данных число(1 или 0)>")
        elif command[1].isdigit() and command[2].isdigit() and len(command) == 5:
            bot.send_message(message.from_user.id, "Отлично.")
            teams_spisok = message.text.split()
            try:
                client.End([command[1], command[2]])
                client.AllEnd()
                client.change_team([teams_spisok[3], teams_spisok[4]])
            except Exception as e:
                bot.send_message(message.from_user.id, f"Ошибка: {e}")
    elif message.text == "помощь":
        bot.send_message(message.from_user.id, HELP, reply_markup=keyboards(["бюджет", "помощь"]))
        bot.send_sticker(message.from_user.id, open("ok.webp", 'rb'))
    elif message.text == "/start":
        answer = client.registration()
        if answer == "Added":
            bot.send_message(message.from_user.id, "Отлично, вы зарегестрированы! Посмотреть мои возможности 'помощь'", reply_markup=keyboards(["бюджет", "помощь"]))
            bot.send_sticker(message.from_user.id, open("ok.webp", 'rb'))
            #bot.send_message(message.from_user.id, input("Введи сообщение"))
        elif answer == "Been":
            bot.send_message(message.from_user.id, "Ошибка! Вы уже зарегестрированы. Посмотреть мои возможности 'помощь'", reply_markup=keyboards(["бюджет", "помощь"]))
            bot.send_sticker(message.from_user.id, open("f.webp", 'rb'))

    elif message.text == "бюджет":
        answer = client.registration()
        if answer == "Been":
            bot.send_message(message.from_user.id, f"Ваш бюджет: {client.get_budget()}", reply_markup=keyboards(["бюджет", "помощь"]))
        else:
            bot.send_message(message.from_user.id, "Ошибка!! Вы не зарегестрированы, напишите /start или 'помощь' для большей информации", reply_markup=keyboards(["бюджет", "помощь"]))
            bot.send_sticker(message.from_user.id, open("f2.webp", 'rb'))

    elif "/bet" in message.text:
        #str(message.text).split()[0]
        #answer = self.client.new_bet(split(message.text)[1], "Sus") # не доделанная фича
        # вместо криворукой сборки я попробую инлайн кнопки чтобы принимать ставку фиксированную
        if len(message.text.split()) < 2 or len(message.text.split()) > 2:
            bot.send_message(message.from_user.id, "Ошибка, вы не указали ставку, либо написали лишнего!")
            bot.send_sticker(message.from_user.id, open("f2.webp", 'rb'))
        elif not message.text.split()[1].isdigit():
            bot.send_message(message.from_user.id, "Ошибка, вы написали что-то, не являющееся ставкой...")
            bot.send_sticker(message.from_user.id, open("f2.webp", 'rb'))
        elif int(message.text.split()[1]) > (client.get_budget() // 2):
            bot.send_message(message.from_user.id, f"Ваша ставка больше чем половина остатка средств. Проверьте, ваш баланс:{client.get_budget()}")
            bot.send_sticker(message.from_user.id, open("f.webp", 'rb'))
        elif len(message.text.split()) == 2 and message.text.split()[1].isdigit() and int(message.text.split()[1]) <= (client.get_budget() // 2):
            Money = int(message.text.split()[1])
            markup = types.InlineKeyboardMarkup()
            markup.row_width = 2
            markup.add(types.InlineKeyboardButton(teams[0], callback_data="cbTeam1"),
                       types.InlineKeyboardButton(teams[1], callback_data="cbTeam2"))
            bot.send_message(message.from_user.id, f"Коэффициенты: команда {teams[0]} :{koeff[0]}, команда {teams[1]} :{koeff[1]}")
            bot.send_message(message.from_user.id, "На кого ставите?", reply_markup=markup)



bot.polling(none_stop=True, interval=0)

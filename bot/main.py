from telebot import TeleBot
from telebot.types import InlineKeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup
from threading import Thread
from bs4 import BeautifulSoup as bs
from requests import get
from time import sleep
from pymongo import MongoClient, cursor

client = MongoClient("localhost", 27017)
db = client["Junggeselle_db"]
users = db["Users_data"]
inactive_users =db["Stop_list"]

token = "6211704099:AAEym56GVji_sTHvAvhd_o1V1Mltfge3eOg"
bot = TeleBot(token)
news_type = 0
news_types = ["1","2","3","4","5","6","7"]


def stop_list():
    query = inactive_users.find({}, {"Chat id": 1, "_id": 0})
    stop_list = [doc["Chat id"] for doc in query]                     # getting ids of people that do not want receiving news anymore
    return stop_list


def chat_ids():
    query = users.find({}, {"Chat id": 1, "_id": 0})
    chat_ids = [doc["Chat id"] for doc in query]                                      # get chat ids all registered users 
    return chat_ids

############################################################## Commands ######################################################################################

@bot.message_handler(commands=['start'])
def launch(message):
    id = message.chat.id
    bot.send_message(id, f"Hey {message.chat.first_name}, nice to see you here, I'm a newsletter bot.\nNews comes every 4 hours"
        "\nI have three types of news: sports (NBA), crypto news," 
        "politics\nTo select the type of news, enter one of the following options:\n1. Sports (NBA)\n2. Crypto news"
        "\n3. Politics\n4. Sports (NBA) + crypto news\n5. Sports (NBA) + politics\n6. Crypto news + politics\n7. All news")

    choice = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    choice.row("1", "2", "3", "4", "5", "6", "7")
    bot.send_message(id, "Please provide your choice", reply_markup=choice)


@bot.message_handler(commands=['stop'])
def stop(message):
    id = message.chat.id

    if id not in stop_list():
        options_menu = InlineKeyboardMarkup()
        option1 = InlineKeyboardButton(text="yes", callback_data="Stop the bot")
        option2 = InlineKeyboardButton(text="no", callback_data="Dont`t stop the bot")
        options_menu.add(option1, option2)
        bot.send_message(id, "Are you sure you want to stop the bot?", reply_markup=options_menu)
    else:
        bot.send_message(id, "At the moment you do not receive news, if you would like to continue receiving news type /resume command")


@bot.message_handler(commands=['resume'])
def resume(message):
    id = message.chat.id

    if id in stop_list():
        options_menu = InlineKeyboardMarkup()
        option1 = InlineKeyboardButton(text="yes", callback_data="Restart the bot")
        option2 = InlineKeyboardButton(text="no", callback_data="Dont`t restart the bot")
        options_menu.add(option1, option2)
        bot.send_message(id, "Do you want to start receiving news again?", reply_markup=options_menu)
    else:
        bot.send_message(id, "You are currently receiving news, if you want to stop that, type /stop command")

@bot.message_handler(commands=['support'])
def support(message):
    id = message.chat.id

    reasons_menu = InlineKeyboardMarkup()
    reason1 = InlineKeyboardButton(text="Complaints", callback_data="Support")
    reason2 = InlineKeyboardButton(text="Suggestions for improving the bot", callback_data="Support")
    reason3 = InlineKeyboardButton(text="Other questions", callback_data="Support")
    reasons_menu.add(reason1, reason2, reason3)
    bot.send_message(id, "Select the reason for contacting technical support", reply_markup=reasons_menu)



###############################################################################################################################################

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):

    if call.data == "Stop the bot":
        bot.send_message(call.from_user.id, "Ok, i got you, if you would like to continue receiving news, type /resume command")
        document = {"Chat id": call.from_user.id}
        inactive_users.insert_one(document) 

    elif call.data == "Dont`t stop the bot":
        bot.send_message(call.from_user.id, "Thank you for staying with me")

    elif call.data == "Restart the bot":
        inactive_users.delete_one({"Chat id": call.from_user.id})
        bot.send_message(call.from_user.id, "Cool that you are again with me, hope you are enjoying while using the bot)")

    elif call.data == "Dont`t restart the bot":
        bot.send_message(call.from_user.id, "Alright, if you would like to continue receiving news, hit /resume command")

    elif call.data == "Support":
        bot.send_message(call.from_user.id, "Thank you for contacting us, our specialist will contact you :)")

################################################################################################################################################

@bot.message_handler(content_types=['text'])
def registration(message):
    id = message.chat.id

    if id not in chat_ids():
        if message.text in news_types:
            global news_type
            news_type = message.text
            bot.send_message(id, "Awesome, in order to complete the registration you need to enter your first name, last name, age,\
                                country you are currently in\nExample: Ilon Mask 51 USA")

        if len(message.text.split(" ")) == 4:
            bot.send_message(id, "Cool!Thanks, from now on every 4 hours you will receive the news that you have chosen.\
                                \n\nThe following commands are available:\n/stop - if you want to stop the bot\
                                \n/resume - if you want to receive news again\n/support - if you need to contact technical support")
            data = message.text.split(" ")

            document = {"First name": f"{data[0]}",
                        "Last Name": f"{data[1]}",
                        "Age": f"{data[2]}",
                        "News type": news_type,
                        "Country": f"{data[3]}",
                        "Chat id": id}
            users.insert_one(document)

    else:
        bot.send_message(id, "You are already registered\n\nThe following commands are available:\n/stop - if you want to stop the bot\
                            \n/resume - if you want to receive news again\n/support - if you need to contact technical support")

################################################################ Getting news #####################################################################################

def sending_news():
    while True:
        for id in chat_ids():
            if id not in stop_list():

                query = users.find({"Chat id": id}, {"News type": 1, "_id": 0})
                type_news = [doc["News type"] for doc in query]

                if type_news[0] == "1":
                    sport_news(id)

                elif type_news[0] == "2":
                    crypto_news(id)

                elif type_news[0] == "3":
                    politics_news(id)

                elif type_news[0] == "4":
                    sport_news(id)
                    crypto_news(id)

                elif type_news[0] == "5":
                    sport_news(id)
                    politics_news(id)

                elif type_news[0] == "6":
                    crypto_news(id)
                    politics_news(id)

                elif type_news[0] == "7":
                    sport_news(id)
                    crypto_news(id)
                    politics_news(id)

        sleep(14400.0)

#######################################################################################################################################################3

def sport_news(id):
    url = "https://www.nba.com/news"
    req = get(url)
    soup = bs(req.text, "html.parser")
    news = soup.find("div", class_="NewsView_dazn__ZF2K2").find_all("div", class_="ArticleTile_tileMainContent__c_bU1", limit=3)
    for i in news:
        bot.send_message(id, text=(i.find("h3", class_="Text_text__I2GnQ ArticleTile_tileTitle__aA8g7").get_text()+ "\n"+
            i.find("p", class_="Text_text__I2GnQ ArticleTile_tileSub__kiMA0").get_text()+ 
            "\nLink = https://www.nba.com"+i.find("a").get("href"), "\n"))

def crypto_news(id):
    url = "https://cryptonews.com/news/"
    req = get(url)
    soup = bs(req.text, "html.parser")
    news = soup.find("section", class_="category_contents_details").find_all("article", class_="mb-15 mb-sm-30 article-item", limit=3)
    for i in news:
        bot.send_message(id, text=(i.find("a", class_="article__title article__title--lg article__title--featured mb-20").get_text()+ "\n"+
            i.find("div", class_="mb-25 d-none d-md-block").get_text()+
            "\nLink = https://cryptonews.com"+i.find("a").get("href")+ "\n"))


def politics_news(id):
    url = "https://www.cnbc.com/politics/"
    req = get(url)
    soup = bs(req.text, "html.parser")
    news = soup.find("div", class_="SectionWrapper-content").find_all("a", class_="Card-title", limit=3)
    for i in news:
        bot.send_message(id, text=(i.get_text()+ "\nLink = "+i.get("href")+ "\n"))

###################################################################################################################################################################

if __name__ == "__main__":

    try:
        thread1 = Thread(target=sending_news)
        thread2 = Thread(target=bot.polling)

        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()


    except Exception as e:
        print(e)


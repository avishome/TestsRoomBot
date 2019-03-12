import os
import telegram
from pymongo import MongoClient

uri = "mongodb://"+user+":"+password+"@"+server

def webhook(request):
    bot = telegram.Bot(token=Token)
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        chat_id = update.message.chat.id
        user_id = update.message.from_user.id
        stage = DB().IsKnow(chat_id)
        if stage == -1:
            DB().AddnewUser(chat_id,user_id,"",1)
            bot.sendMessage(chat_id=chat_id, text="ממתין לשליחת מספר זיהוי")
        elif stage == 1 or stage == 2:
            if DB().InsertLi(chat_id,update.message.text):
                bot.sendMessage(chat_id=chat_id, text="נרשמת לקבלת חדר בחינה")
            else:
                bot.sendMessage(chat_id=chat_id, text="מספר זיהוי לא תקין")
        elif stage == 3:
            bot.sendMessage(chat_id=chat_id, text="אתה חסום")
        elif stage == 4:
            if update.message.text == "זיהוי" or update.message.text == "/edit":
                bot.sendMessage(chat_id=chat_id, text="ממתין למספר זיהוי חדש")
                DB().EditLi(chat_id)
            else:
                bot.sendMessage(chat_id=chat_id, text="אתה רשום, שלח 'זיהוי' לעדכון מספר")
    return "ok"

class _DB:
    _instance = None

    def __init__(self):
        client = MongoClient(uri)
        db = client.get_default_database()
        self.Collection = db.test
        self.result = None
    
    def AddnewUser(self,Cn,Tu,Li,St):
        self.Collection.insert({"chatname":Cn,"telegramuser":Tu,"levid":Li,"status":St})
    
    def IsKnow(self,Cn):
        self.result = self.Collection.find_one({"chatname" : Cn})
        if self.result is None:
            return -1
        else:
            return self.result['status']
        #return status or -1 
    def EditLi(self,Cn):
        self.Collection.update_one({"chatname": Cn}, {'$set': {"status":2}})
    def InsertLi(self,Cn,Li):
        if Li.isdigit() and len(Li) > 1:
            self.Collection.update_one({"chatname": Cn}, {'$set': {"levid": Li,"status":4}})
            return True
        return False
    
def DB():
    if _DB._instance is None:
        _DB._instance = _DB()
    return _DB._instance
	
	#####
	#שםצאט
	#שםמשתמש
	#תזמשתמש
	#מצבשיחה
	
	#0 חדש
	#1 בקשה להכנסת תז
	#2 חידוש תז
	#3 חסום
	#4 פעיל
	#####
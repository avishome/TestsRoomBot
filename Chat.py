import os
import telegram
from pymongo import MongoClient

uri = "mongodb://"+user+":"+password+"@"+server

def webhook(request):
    bot = telegram.Bot(token=Token)
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        if not update.message:
            return "false"
        chat_id = update.message.chat.id
        user_id = update.message.from_user.id
        if update.message.text == "/help":
            bot.sendMessage(chat_id=chat_id, text="-.הבוט הוא יוזמה עצאית ואינו קשור להנהלת או מזכירות המכון \n -הפרטים שנשלחים לבוט נשמרים בבסיס נתונים סגור, אנחנו מבטיחים להגן על פרטיותכם ולא להשתמש בהם מעבר לתפעול הבוט ככל שתגיע ידנו, (בסיס הנתונים הוא mlab.com). בכל עת ניתן לשלוח /stop  והמידע שנאסף ימחק מהמאגר \n -אין אפשרות בשלב זה לודא האם התלמיד מאושר למבחן או ששמו מחוק ברשימות. \n -הבוט בודק את קבצי חדרי הבחינה בלב נט בכל יום ויום בשעה 20:00, בשעה זו ההודעות נשלחות לרשומים. \n -הבוט שולח לרשומים את חדרי הבחינה שלהם כאשר עולה קובץ חדרי בחינה חדש ללב נט, תאריך השליחה הוא לא בהכרח תמיד בערב המבחן. \n -לתלמידות בית הדפוס הזיהוי הוא באמצעות שם המשפחה, במידה ויש שם משפחה זהה לכמה בנות ניתן לשלוח את הפקודה /accuracy לאחר הרישום הבסיסי ולהוסיף זיהוי בעזרת שם פרטי.")
        stage = DB().IsKnow(chat_id)
        if stage == -1:
            DB().AddnewUser(chat_id,user_id,"",-5)
            bot.sendMessage(chat_id=chat_id, text="לומד בגבעת מרדכי שלח לב, לומדת בגבעת שאול שלחי טל")
        elif update.message.text == "/stop":
            DB().RemoveUser(chat_id)
            bot.sendMessage(chat_id=chat_id, text="להתראות")
        elif stage == -5:
            if update.message.text == "טל":
                DB().EditStage(chat_id,-4)
                bot.sendMessage(chat_id=chat_id, text="שלחי שם משפחה בדיוק כפי שמופיע במכון")
            elif update.message.text == "לב":
                DB().EditStage(chat_id,1)
                bot.sendMessage(chat_id=chat_id, text="שלח מספר זיהוי")
            else:
                bot.sendMessage(chat_id=chat_id, text="לומד בגבעת מרדכי שלח לב, לומדת בגבעת שאול שלחי טל")
        elif stage == -4:
            if DB().SetName(chat_id,update.message.text):
                bot.sendMessage(chat_id=chat_id, text="עודכן בהצלחה")
            else:
                bot.sendMessage(chat_id=chat_id, text="לא תקין")
        elif stage == 45:
            if DB().SetPName(chat_id,update.message.text):
                bot.sendMessage(chat_id=chat_id, text="עודכן בהצלחה")
            else:
                bot.sendMessage(chat_id=chat_id, text="לא תקין")
        elif stage == 1 or stage == 2:
            if DB().InsertLi(chat_id,update.message.text):
                bot.sendMessage(chat_id=chat_id, text="נרשמת לקבלת חדר בחינה")
            else:
                bot.sendMessage(chat_id=chat_id, text="מספר זיהוי לא תקין")
        elif stage == 3:
            bot.sendMessage(chat_id=chat_id, text="אתה חסום")
        elif stage == 4 or stage == 44 or stage == 46:
            if (update.message.text == "זיהוי" or update.message.text == "/edit") and stage == 4:
                bot.sendMessage(chat_id=chat_id, text="ממתין למספר זיהוי חדש")
                DB().EditLi(chat_id)
            elif update.message.text == "/info":
                regist = DB().Info(chat_id,stage)
                textR = "הרישום שלך הוא : -" + regist + "-."
                bot.sendMessage(chat_id=chat_id, text=textR)
            elif (update.message.text == "זיהוי" or update.message.text == "/edit") and (stage == 44 or stage == 46):
                bot.sendMessage(chat_id=chat_id, text="שלחי שם משפחה בדיוק כפי המופיע במכון")
                DB().EditStage(chat_id,-4)
            elif (update.message.text == "/accuracy") and stage == 44:
                bot.sendMessage(chat_id=chat_id, text="שלחי שם פרטי מדוייק כפי המופיע במכון")
                DB().EditStage(chat_id,45)
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
        
    def RemoveUser(self,Cn):
        self.Collection.remove({"chatname" : Cn})
        
    def Info(self,Cn,St):
        temp = self.Collection.find_one({"chatname" : Cn})
        if temp:
            if St == 4:
                return temp['levid']
            elif St == 44:
            	return temp['NameUser']
            elif St == 46:
            	return "שם פרטי:" + temp['PNameUser'] + ":שם משפחה:" + temp['NameUser'] + ":"
            else:
                return ""
        else:
            return "0"
    
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
        if Li is not None and Li.isdigit() and len(Li) > 1:
            self.Collection.update_one({"chatname": Cn}, {'$set': {"levid": Li,"status":4}})
            return True
        return False
    def EditStage(self,Cn,Stage):
        self.Collection.update_one({"chatname": Cn}, {'$set': {"status":Stage}})
        
    def SetName(self,Cn,Nu):
        if Nu is not None and len(Nu)<25:
            self.Collection.update_one({"chatname": Cn}, {'$set': {"status":44,"NameUser":Nu}})
            return True
        return False
    
    def SetPName(self,Cn,Nu):
        if Nu is not None and len(Nu)<25:
            self.Collection.update_one({"chatname": Cn}, {'$set': {"status":46,"PNameUser":Nu}})
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
	# -1 פעם ראשונה
    # -5 בחירת מכון
    # -4 ממתין לשם פרטי
    # -3 ממתין לשם משפחה
    # 45 ממתין לשם פרטי
    # 46 פעיל מדוייק מכון טל
    # 44 פעיל מכון טל
	#0 חדש
	#1 בקשה להכנסת תז
	#2 חידוש תז
	#3 חסום
	#4 פעיל
    #
    #####
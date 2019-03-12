import requests
import json
from pymongo import MongoClient
import csv
import telegram
import os
import tempfile

uri = "mongodb://"+user+":"+password+"@"+server
bot = None

def webhook(request):
    bot = telegram.Bot(token=Token)
    url = 'http:'+request.args.get('url')
    print(requests.get(url).content)
    Fileurl = 'http:'+json.loads(requests.get(url).content)["output"]["url"]
    
    r = requests.get(Fileurl)    
    with open(get_file_path('Fullfile.csv'), 'wb') as f:
        f.write(r.content)
    WorkOnCvs()
    return "Tr"

def WorkOnCvs():    
    with open(get_file_path('onlyJson.csv'), 'w') as ne:
        with open(get_file_path('Fullfile.csv')) as f:
            f1=f.readlines()
            x=-1
            header = ""
            while (x+1)<len(f1) and "ת.ז." not in f1[x+1]:
                if "יום" in f1[x]:
                    header = f1[x]
                x=x+1
            for y in range(len(f1)):
                if(y>x):
                    ne.write(f1[y])
    read_csv(get_file_path("onlyJson.csv"),get_file_path("file.json"))
    with open(get_file_path("file.json"), "r") as f:
        Data = json.loads(f.read())    
    client = MongoClient(uri)
    db = client.get_default_database()
    Collection = db.test
    Users = Collection.find({'status':4})
    TZ = ""
    for x in Data[0].keys():
        if str(x) == 'ת.ז.':
            TZ = x
    if TZ == "":
        print(TZ)
        return "Fl"
    for doc in Users:
        for data in Data:
            if data[TZ] == doc['levid']:
                print(data[TZ])
                bot.sendMessage(chat_id=doc['telegramuser'], text=header)
                textForSend = "";
                for y in data:
                    textForSend += y+' : '+data[y]+"\n"
                bot.sendMessage(chat_id=doc['telegramuser'], text=textForSend)

##help functions				
def read_csv(file, json_file):
    csv_rows = []
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        title = reader.fieldnames
        for row in reader:
            csv_rows.extend([{title[i]:row[title[i]] for i in range(len(title))}])
        write_json(csv_rows, json_file)
        
def write_json(data, json_file):
    with open(json_file, "wb") as f:
        f.write(json.dumps(data,ensure_ascii=False).encode('utf-8'))

# Helper function that computes the filepath to save files to
def get_file_path(filename):
    # Note: tempfile.gettempdir() points to an in-memory file system
    # on GCF. Thus, any files in it must fit in the instance's memory.
    file_name = filename
    return os.path.join(tempfile.gettempdir(), file_name)
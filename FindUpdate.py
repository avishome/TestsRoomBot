import cloudconvert
import json
import requests
import os
import tempfile
import random
api = cloudconvert.Api(ApiCode)
uri = "mongodb://"+user+":"+password+"@"+server
login_data = {'username':'user',"password":"pass"}
headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
TryLogin = 'https://levnet.jct.ac.il/api/home/login.ashx?action=TryLogin'
LoadAnnouncements = 'https://levnet.jct.ac.il/api/common/announcements.ashx?action=LoadAnnouncements'
DownloadFile = 'https://levnet.jct.ac.il/api/common/announcements.ashx?action=DownloadFile&fileId='
def convertion(request):
    with requests.Session() as s:
        url = TryLogin
        r = s.get(url, headers=headers)
        r = s.post(url, data=login_data, headers=headers)
        url = LoadAnnouncements
        req = {"announcementType":"TestRooms"}
        r = s.post(url, data=req, headers=headers)
        r = json.loads(r.content)
        cookie = s.cookies
    isNew = 0
    for Item in r['announcements']:
        u = requests.get(DownloadFile+str(Item['id']), headers=headers, cookies=cookie, allow_redirects=True)
        cookie = u.cookies
        FileName = str(random.randint(1,100000))+'.xlsx'
        FileType = u.headers['content-disposition'].split(".")[-1]
        if FileType == 'xlsx':
            open(get_file_path(FileName), 'wb').write(u.content)
            print(FileName)
            api.convert({
            "inputformat": "xlsx",
            "outputformat": "csv",
            "input": "upload",
            "save": True,
            "callback": NextFuncUrl,
            "file": open(get_file_path(FileName), 'rb')
            })
            isNew = isNew + 1
    if isNew == 0:
        return "no"
    return str(isNew)

# Helper function that computes the filepath to save files to
def get_file_path(filename):
    # Note: tempfile.gettempdir() points to an in-memory file system
    # on GCF. Thus, any files in it must fit in the instance's memory.
    file_name = filename
    return os.path.join(tempfile.gettempdir(), file_name)
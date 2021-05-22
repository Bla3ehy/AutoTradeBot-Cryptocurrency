import webbrowser
from __main__ import *
import os
import requests


def openFile():
    confirm = False
    text = input("Would you Open Profolio ok ?")
    if 'ok' == text.lower():
        filename = 'file:///'+'D:/BitHelper'+'/' + 'profolio.html'
        webbrowser.open_new_tab(filename)

    text = input("Would you like to Send this Order ok ?")
    if 'ok' == text.lower():
        confirm = True
    os.remove('D:/BitHelper/profolio.html')
    return confirm


def lineNotifyMessage(token, msg):
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    payload = {'message': msg}
    r = requests.post("https://notify-api.line.me/api/notify",
                        headers=headers, params=payload)
    return r.status_code




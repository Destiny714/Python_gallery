import requests
import json


def wx_pusher(summary,content):
    url = 'http://wxpusher.zjiecode.com/api/send/message'
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({
        "appToken": "",
        "content": content,
        "summary": summary,
        "contentType": 1,
        "topicIds": [],
        "uids": [''],
        "url": ""
    })
    requests.post(url=url, headers=headers, data=data, verify=False)


def bark_pusher(title,content):
    url = f'https://api.day.app/**/{title}/{content}'
    requests.get(url, verify=False)

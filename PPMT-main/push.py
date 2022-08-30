import requests
import json


def pusher(summary,content):
    url = 'http://wxpusher.zjiecode.com/api/send/message'
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({
        "appToken": "",
        "content": content,
        "summary": summary,
        "contentType": 1,
        "topicIds": [],
        "uids": ['',''],
        "url": ""
    })
    requests.post(url=url, headers=headers, data=data)

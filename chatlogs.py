import requests
import re
import sys
import json

API_REQUEST = 'https://discordapp.com/api/channels/%d/messages?token=%s&limit=100'
ID_REGEX = re.compile('<@!?(\d+)>')

channels = []
with open('channels.txt') as file:
    for line in file:
        name, id = line.split()
        channels.append((name, int(id)))

if len(sys.argv) != 2:
    print('usage: %s DISCORD_TOKEN' % sys.argv[0])
    raise SystemExit()

token = sys.argv[1]

def do_get(request):
    r = requests.get(request)
    if r.ok:
        return r.json()
    print(r.reason)
    raise SystemExit()

users = {}

def replace_userid(match):
    id = match.group(1)
    if id in users:
        return '@' + users[id]
    else:
        return '<@' + id + '>' 

for (channel_name, channel_id) in channels:
    print('Archiving', channel_name)
    messages = []
    j = do_get(API_REQUEST % (channel_id, token))
    while j:
        for message in j:
            users[message['author']['id']] = message['author']['username']
        messages = messages + j
        j = do_get(API_REQUEST % (channel_id, token) + '&before=%s' % j[-1]['id'])
    with open('channel_%s.json' % channel_name, 'w') as file:
        json.dump(messages[::-1], file)
    with open('channel_%s.csv' % channel_name, 'w') as file:
        print('user,message', file=file)
        for message in messages[::-1]:
            content = ID_REGEX.sub(replace_userid, message['content'])
            print('"%s","%s"' % (message['author']['username'], content), file=file)
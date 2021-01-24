#!/usr/bin/env python3

from datetime import datetime
import requests
import hashlib
import websocket
import json
import os
import time

DEBUG=os.environ.get('BOT_DEBUG')
ROCKET_WS_URL=os.environ.get('ROCKET_WS_URL')
ROCKET_USERNAME=os.environ.get('ROCKET_USERNAME')
ROCKET_PASSWORD=os.environ.get('ROCKET_PASSWORD')
GITHUB_PROJECT=os.environ.get('GITHUB_PROJECT')
GITHUB_USERNAME=os.environ.get('GITHUB_USERNAME')
GITHUB_TOKEN=os.environ.get('GITHUB_TOKEN')
DEFAULT_AVATAR_URL=os.environ.get('DEFAULT_AVATAR_URL')

def debug_print(msg):
    if DEBUG:
        print(msg)

class Bot:
    def __init__(self):
        self.sever_id = None
        self.session_id = None
        self.token = None
        self.token_expires = None
        self.id = None

        self.ws = websocket.WebSocketApp(ROCKET_WS_URL,
            on_message = lambda ws,msg: self.on_message(ws, msg),
            on_error = lambda ws,msg: self.on_error(ws, msg),
            on_close = lambda ws: self.on_close(ws),
            on_open = lambda ws: self.on_open(ws))

    def run(self):
        self.ws.run_forever()

    def send(self, message_dict):
        debug_print("Sending: " + message_dict.__repr__())
        self.ws.send(json.dumps(message_dict))

    def login(self):
        login_msg = {
            "msg": "method",
            "method": "login",
            "id": "login",
            "params" : [{
                "user": {
                    "username": ROCKET_USERNAME
                },
                "password": {
                    "digest": hashlib.sha256(ROCKET_PASSWORD.encode('utf-8')).hexdigest(),
                    "algorithm": "sha-256",
                },
            }],
        }
        self.send(login_msg)

    def get_subscriptions(self):
        subscriptions_msg = {
            "msg": "method",
            "method": "subscriptions/get",
            "id": "subscriptions",
        }
        self.send(subscriptions_msg)

    def subscribe(self, channel, channel_id):
        subscribe_msg = {
            "msg": "sub",
            "id": channel,
            "name": "stream-room-messages",
            "params":[
                channel_id,
                False
            ]
        }
        self.send(subscribe_msg)

    def update_msg(self, msg):
        debug_print("Updating message!")
        links = []

        for word in msg['msg'].split(' '):
            if not word.count('#'):
                continue

            parts = word.split('#')
            if len(parts) != 2:
                debug_print("Message doesn't have an issue tag")
                continue

            issue = 0
            repository = parts[0]
            try:
                issue = int(parts[1])
            except ValueError:
                debug_print("Message doesn't have a valid issue number")
                continue

            if issue < 100 and not repository:
                debug_print("Message issue # too low for unprefixed issue")
                continue

            if not repository:
                repository = 'godot'

            debug_print(f"Message contains issue for {repository}")

            headers = { 'User-Agent': 'Godot Issuebot by hpvb', }
            url = f"https://api.github.com/repos/{GITHUB_PROJECT}/{repository}/issues/{issue}"
            debug_print(f"GitHub API request: {url}")

            r = requests.get(url, headers=headers, auth=(GITHUB_USERNAME, GITHUB_TOKEN))
            if r.status_code != 200:
                debug_print(f"Github API returned an error {r.status_code}")
                debug_print(r.content)
                continue

            issue = r.json()

            avatar_url = DEFAULT_AVATAR_URL
            if 'avatar_url' in issue['user'] and issue['user']['avatar_url']:
                avatar_url = issue['user']['avatar_url']
            if 'gravatar_id' in issue['user'] and issue['user']['gravatar_id']:
                avatar_url = f"https://www.gravatar.com/avatar/{issue['user']['gravatar_id']}"

            is_pr = False
            pr_mergeable = None
            pr_merged = None
            pr_merged_by = None
            pr_draft = False
            pr_reviewers = None
            status = None
            closed_by = None

            if 'pull_request' in issue and issue['pull_request']:
                is_pr = True
                debug_print(f"GitHub API request: {issue['pull_request']['url']}")

                prr = requests.get(issue['pull_request']['url'], headers=headers, auth=(GITHUB_USERNAME, GITHUB_TOKEN))
                if prr.status_code == 200:
                    pr = prr.json()
                    status = pr['state']

                    if 'merged_by' in pr and pr['merged_by']:
                        pr_merged_by = pr['merged_by']['login']
                    if 'mergeable' in pr:
                        pr_mergeable = pr['mergeable']
                    if 'merged' in pr:
                        pr_merged = pr['merged']
                    if 'draft' in pr:
                        pr_draft = pr['draft']
                    if 'requested_reviewers' in pr and pr['requested_reviewers']:
                        reviewers = []
                        for reviewer in pr['requested_reviewers']:
                            reviewers.append(reviewer['login'])
                        pr_reviewers = ', '.join(reviewers)
            else:
                status = issue['state']

            if status == 'closed':
                if 'closed_by' in issue and issue['closed_by']:
                    closed_by = issue['closed_by']['login']

            issue_type = None

            if is_pr:
                issue_type = "Pull Request"
                if pr_merged:
                    status = "PR merged"
                    if pr_merged_by:
                        status += f" by {pr_merged_by}"
                elif status == 'closed':
                    status = "PR closed"
                elif not pr_merged:
                    status = "PR open"
                    if pr_draft:
                        status += " [draft]"
                    if pr_mergeable != None:
                        if pr_mergeable:
                            status += " [mergeable]"
                        else:
                            status += " [needs rebase]"
                    if pr_reviewers:
                        status += f" reviews required from {pr_reviewers}"
            else:
                issue_type = "Issue"
                status = f"Status: {status}"

            if not pr_merged and closed_by and status == 'closed':
                status += f" by {closed_by}"

            links.append({
                "author_icon": avatar_url,
                "author_link": issue['html_url'],
                "author_name": f"{repository.title()} [{issue_type}]: {issue['title']}  #{issue['number']}",
                "text": status,
            })

        if not len(links):
            return
                
        if not 'attachments' in msg:
            msg['attachments'] = []

        # We may be editing, remove all the github attachments
        old_attachments = []
        for attachment in msg['attachments']:
            if not attachment['author_link'].startswith(f'https://github.com/{GITHUB_PROJECT}'):
                old_attachments.append(attachment)

        msg['attachments'] = old_attachments

        # Hack Hack, the clients won't update without a change to this field. Even if we add or remove attachments.
        msg['msg'] = msg['msg'] + " "
        msg['attachments'].extend(links)

        update_msg = {
            "msg": "method",
            "method": "updateMessage",
            "id": "blah",
            "params": [ msg ]
        }
        self.send(update_msg)

    def on_message(self, ws, message):
        decoded_msg = json.loads(message)
        debug_print("Incoming: " + decoded_msg.__repr__())

        if 'server_id' in decoded_msg:
            self.server_id = decoded_msg['server_id']

        if 'msg' in decoded_msg:
            msg = decoded_msg['msg']
            if msg == 'ping':
                self.send({'msg': 'pong'})

            if msg == 'connected':
                self.session_id = decoded_msg['session']
                debug_print(f"Got session: {self.session_id}")
                self.login()

            if msg == 'result':
                if decoded_msg['id'] == 'login':
                    self.id = decoded_msg['result']['id']
                    self.token = decoded_msg['result']['token']
                    self.token_expires = datetime.fromtimestamp(int(decoded_msg['result']['tokenExpires']['$date']) / 1000)
                    debug_print(f"Loggedin: id: {self.id}, token: {self.token}, expires: {self.token_expires}")
                    self.get_subscriptions()

                if decoded_msg['id'] == 'subscriptions':
                    for subscription in decoded_msg['result']:
                        self.subscribe(subscription['name'], subscription['rid'])

            if msg == 'changed' and decoded_msg['collection'] == 'stream-room-messages':
                for chat_msg in decoded_msg['fields']['args']:
                    if 'editedBy' in chat_msg and chat_msg['editedBy']['_id'] == self.id:
                        continue
                    if chat_msg['msg'].count('#'):
                        self.update_msg(chat_msg)

    def on_error(self, ws, error):
        debug_print(error)

    def on_close(self, ws):
        debug_print("Disconnected, reconnecting")
        ws.close()
        #ws.run_forever()

    def on_open(self, ws):
        connect_msg = { "msg": "connect", "version": "1", "support": ["1"] }
        self.send(connect_msg)

if __name__ == "__main__":
    if DEBUG:
        websocket.enableTrace(True)

    while True:
        try: 
            bot = Bot()
            bot.run()
        except Exception as e:
            print(e)
            time.sleep(10)

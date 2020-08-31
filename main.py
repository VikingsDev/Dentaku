import json
import sys
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from fbchat import log, Client
import os
from fbchat import Message
from fbchat.models import *
import traceback
from datetime import datetime
import time
from fbchat import ThreadType
from fbchat import TypingStatus
import importlib
from signal import signal, SIGINT

database = {}


# Subclass fbchat.Client and override required methods
class dentaku_bot(Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        global database
        if database['testing'].lower() == "y" and thread_type != ThreadType.USER:
            return
        if "!" in str(message_object.text)[0] and len(message_object.text) > 1:
            client.setTypingStatus(
                TypingStatus.TYPING, thread_id=thread_id, thread_type=thread_type
            )
            message = str(message_object.text).replace("!", "").split(" ")
            print(message)
            if message == ['']:
                return
            command_index = 1
            if message[0] == '':
                for each in message:
                    if each != '':
                        command = each
                        break
                    command_index += 1
            else:
                command = message[0]
            try:
                parameters = {
                    "trigger": command.lower(),
                    "user": message[command_index:],
                    "author_id": author_id,
                    "message_object": message_object,
                    "thread_id": thread_id,
                    "thread_type": thread_type,
                    "database": database,
                    "gdb": gdb
                }
                command = command.lower()
                module = importlib.import_module(".." + command, "commands.subpkg")
                new_command = getattr(module, command)
                instance = new_command(parameters, client=self)
                instance.process()
            except ModuleNotFoundError:
                print(traceback.format_exc())
                self.send(
                    Message(text="Command not found."),
                    thread_id=thread_id,
                    thread_type=thread_type,
                )
            except Exception as e:
                # Sends error message to current chat
                if thread_type is ThreadType.GROUP or author_id not in database['subscription']:
                    self.send(
                        Message(text="Oh no! An error has occurred. Type !subscribe to receive error details.",
                                reply_to_id=message_object.uid),
                        thread_id=thread_id,
                        thread_type=thread_type,
                    )
                # Sends error message to subscribed members
                for thread in database['subscription']:
                    # Check if trigger is in PM
                    if thread == thread_id:
                        self.send(
                            Message(text="This message triggered an error!", reply_to_id=message_object.uid),
                            thread_id=thread,
                            thread_type=ThreadType.USER,
                        )
                        self.send(
                            Message(text="Error: " + traceback.format_exc()),
                            thread_id=thread,
                            thread_type=ThreadType.USER,
                        )
                    elif thread_type is ThreadType.GROUP and \
                        thread in self.fetchThreadInfo(thread_id)[thread_id].participants:
                        # Sends info through PMs
                        self.send(
                            Message(text="Message triggering error:\n\"{}\"".format(message_object.text)),
                            thread_id=thread,
                            thread_type=ThreadType.USER,
                        )
                        self.send(
                            Message(text="Error: " + traceback.format_exc()),
                            thread_id=thread,
                            thread_type=ThreadType.USER,
                        )
        elif author_id != client.uid:
            for word in keywords.keys():
                word = word.lower()
                if word in message_object.text.lower():
                    try:
                        parameters = {
                            "trigger": word,
                            "author_id": author_id,
                            "message_object": message_object,
                            "thread_id": thread_id,
                            "thread_type": thread_type,
                            "database": database,
                            "gdb": gdb
                        }
                        module = importlib.import_module(".." + keywords[word], "keywords.subpkg")
                        new_command = getattr(module, keywords[word])
                        instance = new_command(parameters, client=self)
                        instance.run()
                    except ModuleNotFoundError:
                        self.send(
                            Message(text="Keyword did not map to an existing python module."),
                            thread_id=thread_id,
                            thread_type=thread_type,
                        )
                    except Exception as e:
                        # Sends error message to current chat
                        if thread_type is ThreadType.GROUP or author_id not in database['subscription']:
                            self.send(
                                Message(text="Oh no! An error has occurred. Type !subscribe to receive error details.",
                                        reply_to_id=message_object.uid),
                                thread_id=thread_id,
                                thread_type=thread_type,
                            )
                        # Sends error message to subscribed members
                        for thread in database['subscription']:
                            # Check if trigger is in PM
                            if thread == thread_id:
                                self.send(
                                    Message(text="This message triggered an error!", reply_to_id=message_object.uid),
                                    thread_id=thread,
                                    thread_type=ThreadType.USER,
                                )
                                self.send(
                                    Message(text="Error: " + traceback.format_exc()),
                                    thread_id=thread,
                                    thread_type=ThreadType.USER,
                                )
                            elif thread_type is ThreadType.GROUP and \
                                    thread in self.fetchThreadInfo(thread_id)[thread_id].participants:
                                # Sends info through PMs
                                self.send(
                                    Message(text="Message triggering error:\n\"{}\"".format(message_object.text)),
                                    thread_id=thread,
                                    thread_type=ThreadType.USER,
                                )
                                self.send(
                                    Message(text="Error: " + traceback.format_exc()),
                                    thread_id=thread,
                                    thread_type=ThreadType.USER,
                                )


def export_env():
    with open("export.sh", "r") as file_in:
        for line in file_in:
            if "\"" in line:
                os.environ[line.split("=")[0].split(" ")[1]] = line[line.find("\"") + 1:line.rfind("\"")]
            else:
                line = line.replace("export", "").replace(" ", "")
                line = line.split("=")
                os.environ[line[0]] = line[1]


export_env()
cookies = []
try:
    # Load the session cookies
    with open('cookies.json', 'r') as f:
        cookies = json.load(f)
except:
    # If it fails, never mind, we'll just login again
    pass
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"
client = dentaku_bot(os.getenv('EMAIL'), os.getenv('PASSWORD'), user_agent=user_agent, session_cookies=cookies)
with open('cookies.json', 'w') as f:
    json.dump(client.getSession(), f)

if os.path.exists("database.json"):
    with open("database.json", 'r') as file:
        try:
            database = json.load(file)
        except json.decoder.JSONDecodeError:
            print("JSON file is invalid. Repair or delete database.json.")
            sys.exit()
        if 'deployment' in database:
            database['deployment'] += 1
        else:
            database['deployment'] = 0
        database['last_deployment_time'] = time.time()
    with open('database.json', 'w') as file:
        json.dump(database, file)
else:
    database = {"deployment": 0, "subscription": []}
    with open('database.json', 'w') as file:
        json.dump(database, file)

if os.path.exists("keywords.json"):
    with open("keywords.json", 'r') as file:
        try:
            keywords = json.load(file)
        except json.decoder.JSONDecodeError:
            print("JSON file is invalid. Repair or delete keywords.json.")
else:
    keywords = {}
    with open('keywords.json', 'w') as file:
        json.dump(keywords, file)

if 'testing' not in database:
    print("Testing mode will restrict all bot interactions to direct messages, or ThreadType.USER.")
    database['testing'] = input("Turn on testing mode? (y/n): ")
    if input("Save this decision? (y/n): ").lower() == 'y':
        with open('database.json', 'w') as file:
            json.dump(database, file)
            print("Decision saved to database.json with the key 'testing'")
else:
    print("Testing mode is currently " + ("on" if database['testing'].lower() == 'y' else 'off'))
    print("Mode is saved in database.json")

for thread in database['subscription']:
    client.send(Message(
        text="[" + datetime.now().strftime("%Y-%m-%d %-I:%M %p") + "] Dentaku deployed just now. #" + str(
            database['deployment'])),
        thread_id=thread, thread_type=ThreadType.USER)

if 'G_CREDENTIALS' in os.environ:
    cred = credentials.Certificate(os.environ['G_CREDENTIALS'])
    firebase_admin.initialize_app(cred)
    gdb = firestore.client()
else:
    gdb = None

def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    client.logout()
    exit(0)

client.listen()

signal(SIGINT, handler)

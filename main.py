from fbchat import log, Client
import os
from fbchat import Message
from fbchat.models import *


# Subclass fbchat.Client and override required methods
class dentaku_bot(Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        if (author.first_name == "Frank") and ("bad" in message_object.text.split()):
            self.send(
                Message(text="That is false, my master."),
                thread_id=thread_id,
                thread_type=thread_type, 
            )
        elif "!" in str(message_object.text)[0]:
            command = str(message_object.text).replace("!", "").split(" ")
            parameters = {
                "user": command[1:],
                "author_id": author_id,
                "message_object": message_object,
                "thread_id": thread_id,
                "thread_type": thread_type
            }
            command = command[0]
            try:
                module = __import__(command)
                new_command = getattr(module, command)
                instance = new_command(parameters, client=self)
            except ModuleNotFoundError:
                self.send(
                    Message(text="Command not found."),
                    thread_id=thread_id,
                    thread_type=thread_type,
                )
            except Exception as e:
                self.send(
                    Message(text="Error: " + str(e)),
                    thread_id=thread_id,
                    thread_type=thread_type,
                )


def export_env():
    with open("export.sh") as file_in:
        for line in file_in:
            if "\"" in line:
                os.environ[line.split("=")[0].split(" ")[1]] = line[line.find("\"") + 1:line.rfind("\"")]
            else:
                line = line.replace("export", "").replace(" ","")
                line = line.split("=")
                os.environ[line[0]] = line[1]

export_env()
client = dentaku_bot(os.getenv('EMAIL'), os.getenv('PASSWORD'))
if client.uid == "vikings.dev.73":
    client.send(Message(text="Dentaku is online."), thread_id="100011229734236", thread_type=ThreadType.USER)
else:
    client.send(Message(text="Dentaku is online."), thread_id=client.uid, thread_type=ThreadType.USER)
client.listen()

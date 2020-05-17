from commands.command import Command
from fbchat import Message
import requests


class dict(Command):

    def run(self):
        if len(self.user_params) == 0:
            response_text = "Please enter a search term like this: '!dict SEARCH_TERM'"
        else:
            word = self.user_params[0].lower()
            if word == "help":
                response_text = ("Add one of the following commands after your search term "
                                 "in the format of '!dict TERM COMMAND':"
                                 "\nsynonyms, derivation, examples")
            else:
                commands = ["synonyms", "derivation", "examples"]
                url = "https://wordsapiv1.p.rapidapi.com/words/{}".format(word)
                headers = {
                    "X-Mashape-Key": "8bef51c08bmsh96dc3702341e39ep14a15bjsn19a83064d62d",
                    "Accept": "application/json"
                }
                try:
                    response = requests.get(url, headers=headers)
                    results = response.json()['results']
                    if len(self.user_params) > 1 and self.user_params[1].lower() in commands:
                        response_text = ""
                        for d in results:
                            if self.user_params[1].lower() in d:
                                for i in d[self.user_params[1].lower()]:
                                    response_text += "\n" + i
                        if response_text != "":
                            response_text = self.user_params[1][0].upper() + self.user_params[1][1:].lower() \
                                            + " for: " + word + response_text
                        else:
                            response_text = self.user_params[1][0].upper() + self.user_params[1][1:].lower() \
                                            + " not found for {}.".format(word)

                    else:
                        response_text = "Definitions for: " + word
                        for i, d in enumerate(results):
                            response_text += "\n{}. {} – ".format(i + 1, d['partOfSpeech']) + d['definition']
                except:
                    response_text = "Unable to get information about the search term. Please check your spelling. " \
                                    "For a list of commands type '!dict help'."

        self.client.send(
            Message(text=response_text),
            thread_id=self.thread_id,
            thread_type=self.thread_type
        )

    def define_documentation(self):
        self.documentation = {
            "parameters": "WORD, COMMAND",
            "function": "Returns definition or other info based on COMMAND for WORD."
        }

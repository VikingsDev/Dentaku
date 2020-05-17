from commands.command import Command
from fbchat import Message, Mention, MessageReaction, FBchatException
from random import choice as choose
from random import seed, randint


def find_reply_id(message):
    message_id = str(message).split()
    for x in message_id:
        if x.startswith("reply_to_id="):
            x = x.replace("reply_to_id='", "")
            x = x.replace("',", "")
            x = x.replace("reply_to_id=", "")  # for x = "reply_to_id=None" case
            x = x.replace(",", "")
            return x


class react(Command):

    # dictionary for "string": "emoji"
    emoji_dict = {
        # heart react "❤"
        "<3": "❤", "heart": "❤",
        # love react "😍"
        "love": "😍", "heart_eyes": "😍", "hearteyes": "😍",
        # laugh react "😆"
        "laugh": "😆", "lol": "😆", "lmao": "😆", "haha": "😆", ":)": "😆", "xD": "😆", "XD": "😆", "yay": "😆",
        "LOL": "😆", "LMAO": "😆", "(:": "😆",
        # wow react "😮"
        "wow": "😮", "whoa": "😮", "woah": "😮", "wows": "😮", "wtf": "😮", ":O": "😮", "O:": "😮", "truck": "😮",
        "omg": "😮", "cool": "😮",
        # sad react "😢"
        "sad": "😢", "crying": "😢", "sadness": "😢", "cry": "😢", ":(": "😢", ";-;": "😢", "</3": "😢", "):": "😢",
        "oof": "😢", "oeuf": "😢", "rip": "😢",
        # angry react "😠"
        "angry": "😠", "angr": "😠", "ugh": "😠", ">:(": "😠", "mad": "😠", "):<": "😠", "amgery": "😠",
        # thumbs up react "👍"
        "thumbs_up": "👍", "yes": "👍", "good": "👍", "nice": "👍", "like": "👍", "up": "👍", "okay": "👍", "ok": "👍",
        "k": "👍", "yea": "👍", "fax": "👍", "agree": "👍", "concur": "👍", "yeah": "👍", "ya": "👍", "yup": "👍",
        # thumbs down react "👎"
        "thumbs_down": "👎", "no": "👎", "bad": "👎", "ew": "👎", "dislike": "👎", "down": "👎", "not_okay": "👎",
        "not_ok": "👎", "nah": "👎", "disagree": "👎", "boo": "👎", "nope": "👎",
        # random emoji!
        "random": "run_random", "r": "run_random", "react": "run_random"
    }

    def find_reaction_emoji(self):
        mentions = [Mention(self.author_id, length=len(self.author.first_name) + 1)]
        if len(self.user_params) == 0:
            return None
        elif len(self.user_params) == 1:
            emoji = self.user_params[0].strip().lower()
            try:
                emoji = MessageReaction(emoji)
                return emoji
            except ValueError:
                try:
                    emoji = self.emoji_dict[emoji]
                    if emoji == "run_random":
                        emoji = choose(["❤", "😍", "😆", "😮", "😢", "😠", "👍", "👎"])
                    return MessageReaction(emoji)
                except KeyError:
                    response_text = "@{}\nSorry, you can't react with that.".format(self.author.first_name)
                    self.client.send(
                        Message(text=response_text, mentions=mentions),
                        thread_id=self.thread_id,
                        thread_type=self.thread_type
                    )
                    return "invalid"
        else:
            response_text = "@{}\nPlease input only 1 emoji.".format(self.author.first_name)
            self.client.send(
                Message(text=response_text, mentions=mentions),
                thread_id=self.thread_id,
                thread_type=self.thread_type
            )
            return "invalid"

    def run(self):
        if "auto" not in self.database:
            self.database["auto"] = "off"
        seed(randint(0, 100))
        mentions = [Mention(self.author_id, length=len(self.author.first_name) + 1)]
        if len(self.user_params) > 0:
            if self.user_params[0] == "help":
                response_text = "@" + self.author.first_name
                response_text += " These are the possible react commands: \n```"
                for x in self.emoji_dict.keys():
                    response_text += "\n{}".format(x)
                response_text += "\n```"
                self.client.send(
                    Message(text=response_text, mentions=mentions),
                    thread_id=self.thread_id,
                    thread_type=self.thread_type
                )
                return
            if len(self.user_params) == 1 and self.user_params[0] == "auto":
                response_text = "@" + self.author.first_name \
                                + "\nIf you're looking for auto react, use `!react auto [status/on/off]`."
                self.client.send(
                    Message(text=response_text, mentions=mentions),
                    thread_id=self.thread_id,
                    thread_type=self.thread_type
                )
                return
            if len(self.user_params) > 1:
                response_text = ""
                if self.user_params[0] == "auto":
                    if self.user_params[1] == "on":
                        # auto react is now on.
                        self.database["auto"] = "on"
                    elif self.user_params[1] == "off":
                        # auto react is now off.
                        self.database["auto"] = "off"
                    elif self.user_params[1] == "status":
                        # checks if auto is on/off.
                        response_text = "@" + self.author.first_name \
                                + "\nDentaku's auto react is currently " + self.database["auto"] + "."
                    if response_text == "":
                        response_text = "@" + self.author.first_name \
                                        + "\nAuto react is now " + self.database["auto"] + "."
                else:
                    response_text = "@" + self.author.first_name \
                                        + "S orry, I didn't get that."
                self.client.send(
                    Message(text=response_text, mentions=mentions),
                    thread_id=self.thread_id,
                    thread_type=self.thread_type
                )
                return
        m = self.message_object
        reply_id = find_reply_id(m)
        try:
            emoji = self.find_reaction_emoji()
            if emoji != "invalid":
                self.client.reactToMessage(reply_id, self.find_reaction_emoji())
        except FBchatException:
            response_text = "@{}\nPlease select a message to reply to before reacting.".format(self.author.first_name)
            self.client.send(
                Message(text=response_text, mentions=mentions),
                thread_id=self.thread_id,
                thread_type=self.thread_type
            )

    def define_documentation(self):
        self.documentation = {
            "parameters": "REPLIED_MESSAGE, EMOJI / \"auto\", [status/on/off]",
            "function": "Reacts to a REPLIED_MESSAGE with the specified EMOJI."
                        "Also controls the status of AUTO_REACT."
        }
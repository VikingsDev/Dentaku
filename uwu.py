from command import Command
from fbchat import Message
from fbchat.models import *
from fbchat import Client
from fbchat import Mention
from random import randrange
sputters = [" .///.", " o:"," uwuwuwuu",
" *squirms*", " ovo", " o-owo", " *nuzzles*",
" *blushes*", " uwu", " rawr", " xD", " *purr*",
" ~murrrr~", " O//w//O", " (;" , " o3o", " 0///0",
 " *slurpp*", " XD", " *licks*", " *stares*", " ÚwÙ"]
def splitl(word):
    return [char for char in word]
def furryfy(input):
    owo = input
    owo = owo.replace(".","~")
    oworay = splitl(owo)
    ies = False
    for item in range(len(oworay)-2):
        replacing = oworay[item]
        if oworay[item+1]!=" ":
            ies = True
        if replacing == "s" and oworay[item+1]==" " and (randrange(3)==1) and ies == True and oworay[item-1] not in "aeiou":
            bc = 1
            oworay.insert(item,"ie")
            while oworay[item-bc]== "e":
                oworay.pop(item-bc)
                bc+=1
            ies = False
        elif replacing == "t" and oworay[item+1]=="h":
            oworay.insert(item,"d")
            oworay.pop(item+1)
            oworay.pop(item+1)
        elif replacing == "r" or replacing == "l":
            if oworay[item+1]!=" ":
                oworay[item] = "w"
        elif replacing == " ":
            if randrange(12)==1:
                oworay.insert(item,sputters[randrange(len(sputters))])
            elif randrange(10)==1 and oworay[item+1]!= ("l") and oworay[item+1]!="r" and oworay[item+1]!="t":
                oworay.insert(item+1,oworay[item+1]+"-")
    return("".join(oworay))

class uwu(Command):
    def run(self):
        try:
            target = lower(self.message_object.replied_to)
            response_text = furryfy(target.text)
        except:
            response_text = "I cannot perform this request due to an internal b-oFA error."
        self.client.send(
            Message(text=response_text, mentions= None),
            thread_id=self.thread_id,
            thread_type=self.thread_type
        )

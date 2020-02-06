from commands.command import Command
from fbchat import Message
from fbchat import Mention
try: 
	import googlesearch
except ImportError:  
	print("No module named 'google' found") 


class search(Command):

	def run(self):
		length = len(self.user_params)
		index = 1;
		query = ""


		for i in self.user_params:
			query += i
			if index < length:
				index += 1
				query += " "

		j = ""

		if length > 0:
			for j in googlesearch.search(query, tld="ca", num=1, stop=1, pause=2):
				print(j)

		j += ""

		k = ""
		query = ""
		# get message from a replied thread
		target = self.message_object.replied_to
		if target is not None:
			query = target.text
		if query != "":
			for k in googlesearch.search(query, tld="ca", num=1, stop=1, pause=2):
				print(k)

		if k == "" and j == "":
			response_text = "Please input a search term"
		elif k == "" or j == "":
			response_text = "Here is Google's top search! " + j + k
		else:
			response_text = "Here are Google's top searches for those terms!\n" + j + "\n" + k
		
		self.client.send(
			Message(text=response_text),
			thread_id=self.thread_id,
			thread_type=self.thread_type
		)

	def define_documentation(self):
		self.documentation = {
			"parameters": "SEARCH_TERM / SEARCH TERMS / REPLY TO MESSAGE",
			"function": "Searches Google and gives you the best result for your search"
		}
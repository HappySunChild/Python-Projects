# PyHook __init__.py

import requests as http

class Embed():
	def __init__(self, title: str = None, desc: str = None, **kwargs) -> None:
		self.Title = title
		self.Description = desc
		self.Color = kwargs.get('color')
		
		self.Url = kwargs.get('url')
		self.Footer = kwargs.get('footer')
		self.Author = kwargs.get('author')
		
		self.Fields = []
	
	def setTitle(self, title: str):
		self.Title = title
	
	def setDesc(self, desc: str):
		self.Description = desc
	
	def setColor(self, color: int):
		self.Color = color
	
	def addField(self, name: str, value: str, inline: bool = True):
		self.Fields.append({'name': name, 'value': str(value), 'inline': inline})
	
	def setFooter(self, text: str):
		self.Footer = {'text': text}
	
	def setAuthor(self, name: str):
		self.Author = {'name': name}
	
	def setUrl(self, url: str):
		self.Url = url
	
	@property
	def HttpData(self):
		data = {
			'title': self.Title,
			'description': self.Description,
			'color': self.Color,
			
			'url': self.Url,
			
			'fields': self.Fields,
			'footer': self.Footer,
			'author': self.Author,
		}
		
		return data

class Webhook():
	Id = ''
	Token = ''
	
	def __init__(self, id: int, token: str) -> None:
		self.Id = id
		self.Token = token
		
		self.Name = None
		self.AvatarUrl = None
	
	def SendMessage(self, message: str):
		data = self.HttpData
		data['content'] = message
		
		return _send(self.Url, data)
	
	def SendEmbeds(self, *embeds: Embed, message: str = ''):
		if len(embeds) <= 0:
			return
		
		embedData = []
		
		for embed in embeds:
			embedData.append(embed.HttpData if isinstance(embed, Embed) else embed)
		
		data = self.HttpData
		data['embeds'] = embedData
		data['content'] = message
		
		return _send(self.Url, data)
	
	@property
	def HttpData(self):
		data = {
			'username': self.Name,
			'avatar_url': self.AvatarUrl,
			'content': ''
		}
		
		return data
	
	@property
	def Url(self):
		return f'https://discord.com/api/webhooks/{self.Id}/{self.Token}'

class MultiHook():
	def __init__(self, *webhooks: Webhook) -> None:
		self.Webhooks = webhooks
	
	def SendMessage(self, message: str):
		for hook in self.Webhooks:
			hook.SendMessage(message)
	
	def SendEmbeds(self, *embeds: Embed, message: str = ''):
		for hook in self.Webhooks:
			hook.SendEmbeds(*embeds, message=message)

def _send(url: str, data: dict):
	try:
		response = http.post(url, json=data)
		response.raise_for_status()
		
		return response.ok
	except http.exceptions.RequestException as e:
		print(f'Error sending data: \n{e}\n{response.json()}')
		
		return False
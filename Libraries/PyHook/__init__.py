# PyHook __init__.py

import requests as http
from dateutil.parser import parse

class Message():
	def __init__(self, message_data: dict) -> None:
		self.ChannelId = message_data.get('channel_id', -1)
		self.Id = message_data.get('id', -1)
		self.Type = message_data.get('type', -1)
		
		self.Content = message_data.get('content', '')
		self.Embeds = message_data.get('embeds', [])
		
		self.PostTimestamp = parse(message_data.get('timestamp', 0))
		
		self.Raw = message_data
		
		#self.EditTimestamp = parse(message_data.get('edited_timestamp'))
	
	def GetHttpData(self):
		data = {
			'content': self.Content,
			'embeds': self.Embeds
		}
		
		return data

class Embed():
	def __init__(self, title: str = None, desc: str = None, **kwargs) -> None:
		self.Title = title
		self.Description = desc
		self.Color = kwargs.get('color')
		
		self.Url = kwargs.get('url')
		self.Footer = kwargs.get('footer')
		self.Author = kwargs.get('author')
		
		self.Fields = []
	
	def addField(self, name: str, value: str, inline: bool = True):
		self.Fields.append({'name': name, 'value': str(value), 'inline': inline})
	
	def setTitle(self, title: str):
		self.Title = title
	
	def setDesc(self, desc: str):
		self.Description = desc
	
	def setColor(self, color: int):
		self.Color = color
	
	def setFooter(self, text: str):
		self.Footer = {'text': text}
	
	def setAuthor(self, name: str):
		self.Author = {'name': name}
	
	def setUrl(self, url: str):
		self.Url = url
	
	def GetHttpData(self):
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
	'''
	Instance responsible for sending requests to discord.
	'''
	
	def __init__(self, id: int, token: str) -> None:
		self.Id = id
		self.Token = token
		
		self.Name = None
		self.AvatarUrl = None
		
		self.LastMessage = None
	
	def Delete(self, message: Message):
		if not isinstance(message, Message):
			return
		
		_request(f'{self.Url}/messages/{message.Id}', method='delete')
	
	def Edit(self, message: Message = None, text: str = '', *embeds: Embed):
		'''
		Edits a given message.
		'''
		
		if not isinstance(message, Message):
			if not self.LastMessage or not message:
				return self.Send(text, *embeds)
			else:
				message = self.LastMessage
		
		data = message.GetHttpData()
		data['content'] = text or data['content']
		
		if len(embeds) > 0:
			data['embeds'] = embeds
		
		_request(f'{self.Url}/messages/{message.Id}', data, 'patch')
		
		return message
	
	def Send(self, text: str = '', *embeds: Embed):
		'''
		Sends a message with the webhook.
		'''
		
		embedData = []
		
		for embed in embeds:
			embedData.append(embed.GetHttpData() if isinstance(embed, Embed) else embed)
		
		data = self.GetHttpData()
		data['content'] = text
		data['embeds'] = embedData
		
		self.LastMessage = _send_message(self.Url, data)
		
		return self.LastMessage
	
	def GetHttpData(self):
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
	'''
	Interface for sending messages with multiple webhooks.
	'''
	
	def __init__(self, *webhooks: Webhook) -> None:
		self.Webhooks = webhooks
	
	def AddWebhook(self, webhook: Webhook):
		if not webhook:
			return
		
		self.Webhooks.append(webhook)
	
	def Send(self, text: str = '', *embeds: Embed):
		'''
		Automatically sends a message to each webhook.
		'''
		
		for hook in self.Webhooks:
			hook.Send(text, *embeds)
	
	def Edit(self, text: str = '', *embeds: Embed):
		'''
		Automatically edits the last message sent by each webhook.
		'''
		
		for hook in self.Webhooks:
			hook.Edit(None, text, *embeds)

def _request(url: str, data: dict = None, method: str = 'post'):
	try:
		response = http.request(method, url, json=data, headers={'content-type': 'application/json'})
		response.raise_for_status()
		
		return response
	except http.exceptions.HTTPError as e:
		print(e)
	
	return None

def _send_message(url: str, data: dict):
	response = _request(f'{url}?wait=true', data, 'post')
	
	return Message(response.json())
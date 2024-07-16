base_site = 'roblox.com'

class URLGenerator:
	def __init__(self, base_url: str):
		self.base_url = base_url
	
	def get_url(self, subdomain: str, path: str = '', protocol: str = 'https'):
		return f'{protocol}://{subdomain}.{self.base_url}/{path}'
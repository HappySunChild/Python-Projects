# RoAPI fetch.py

import requests as http

_token = None
base_url = 'roblox.com'

class Page:
	def __init__(self, rawPageData: dict) -> None:
		self.Pager = None
		self.PageNumber = 1
		
		self.PreviousCursor = rawPageData.get('previousPageCursor', None)
		self.NextCursor = rawPageData.get('nextPageCursor', None)
		self.Data = rawPageData.get('data', [])
		
		self.Raw = rawPageData
	
	@property
	def NumEntries(self):
		return len(self.Data)
	
	def __repr__(self) -> str:
		return f"Page #{self.PageNumber} ({self.NumEntries} entries)"
	
	def __str__(self) -> str:
		return f"Page: #{self.PageNumber} <- ({self.Pager})"

class Pager: # meant for endpoints that return pages of information
	def __init__(self, url: str, pageSize: int = 25) -> None:
		self.BaseUrl = url
		
		self.Pages: list[Page] = []
		
		self.PageSize = pageSize
		self.PageNumber = 1
		self.PageCursor = ''
		self.PageRaw = None
		
		self.IsFinished = False
	
	def getCurrentPage(self) -> Page: # returns current page data
		if self.IsFinished:
			return
		
		requestUrl = self.BaseUrl + f'&cursor={self.PageCursor}&limit={self.PageSize}'
		rawPageData = fetch(requestUrl, default={'IsEnd': True})
		
		newPage = Page(rawPageData)
		newPage.PageNumber = self.PageNumber
		newPage.Pager = self
		
		self.PageRaw = rawPageData
		self.Pages.append(newPage)
		
		return newPage
	
	def advanceToNextPage(self) -> bool: # doesn't actually get the page data, just shifts everything to be ready for the next page
		if not self.PageRaw:
			self.getCurrentPage()
		
		cursor = self.PageRaw.get('nextPageCursor')
		
		if not cursor:
			self.IsFinished = True
			
			return False
		
		self.PageNumber += 1
		self.PageCursor = cursor
		
		self.PageRaw = None # reset page data
		
		return True
	
	def getPages(self, pageLimit: int = 10) -> list[Page]:
		if self.IsFinished:
			return
		
		if not pageLimit:
			pageLimit = 10
		
		while not self.IsFinished and self.PageNumber <= pageLimit:
			self.getCurrentPage() # automatically appends to instance's `Pages` list
			self.advanceToNextPage()
		
		return self.Pages
	
	@property
	def NumEntries(self):
		count = 0
		
		for page in self.Pages:
			count += page.NumEntries
		
		return count
	
	def __str__(self) -> str:
		return f"Pager: [{self.BaseUrl}&cursor={self.PageCursor}&limit={self.PageSize}]"

def setToken(newToken: str):
	_token = newToken
	
	return _token

def getToken():
	return _token

def genUrl(subdomain = 'apis', path = '', protocol = 'https'):
	return f'{protocol}://{subdomain}.{base_url}/{path}'

def fetch(url: str, json = None, method = 'get', headers = {}, default = None):
	try:
		if _token:
			headers['cookie'] = _token
		
		response = http.request(url=url, json=json, method=method, headers=headers)
		response.raise_for_status()
		
		return response.json()
	except http.exceptions.HTTPError as e:
		#log.warning('A ROBLOSECURITY token is required to access this endpoint.')
		pass
	
	return default
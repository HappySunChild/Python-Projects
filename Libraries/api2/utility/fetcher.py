from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Callable, Any

from ..enums import SortOrder
from requests import Session, Response

if TYPE_CHECKING:
	from ..client import Client

class Page:
	def __init__(self, page_data: list) -> None:
		self.data = page_data
	
	@property
	def count(self):
		return len(self.data)
	
	def __repr__(self) -> str:
		return f'<{self.__class__.__name__}: {self.count}>'

class Pages:
	def __init__(self, pages: list[Page]) -> None:
		self.pages = pages
	
	def get_pages_data(self):
		data = []
		
		for page in self.pages:
			for entry in page.data:
				data.append(entry)
		
		return data
	
	@property
	def data_count(self):
		count = 0
		
		for page in self.pages:
			count += page.count
		
		return count
	
	@property
	def page_count(self):
		return len(self.pages)
	
	def __repr__(self) -> str:
		return f'<{self.__class__.__name__}>'

class PageIterator:
	def __init__(
			self, 
			fetcher: Fetcher,
			url: str,
			page_size: int,
			sort_order: SortOrder = SortOrder.Ascending,
			handler: Optional[Callable] = None,
			**extra_params
		) -> None:
		
		self.fetcher = fetcher
		self.url = url
		self.sort_order = sort_order
		self.page_size = page_size
		
		self.current_page_index = 0
		self.cached_pages = []
		
		self.next_cursor = ''
		self.prev_cursor = ''
		self.page_cursor = ''
		
		self.handler = handler
		self.extra_params = extra_params
		
		self.is_finished = False
	
	def getAllPages(self, page_limit: int = 5):
		while not self.is_finished and self.current_page_index < page_limit:
			self.getCurrentPage()
			self.advanceToNextPage()
		
		return Pages(self.cached_pages)
	
	def getCurrentPage(self):
		page_data, _ = self.fetcher.get(
			self.url,
			params = {
				"cursor": self.page_cursor,
				"limit": self.page_size,
				"sortOrder": self.sort_order.value,
				**self.extra_params
			}
		)
		
		self.next_cursor = page_data.get('nextPageCursor')
		self.prev_cursor = page_data.get('previousPageCursor')
		
		data = page_data.get('data')
		
		if self.handler:
			data = [
				self.handler(
					data=item_data
				) for item_data in data
			]
		
		new_page = Page(data)
		
		self.cached_pages.append(new_page)
		
		return new_page
	
	def advanceToNextPage(self):
		if self.next_cursor is None:
			self.is_finished = True
			
			return
		
		self.current_page_index += 1
		
		self.prev_cursor = self.page_cursor
		self.page_cursor = self.next_cursor
		self.next_cursor = None
	
	def __repr__(self) -> str:
		return f'<{self.__class__.__name__}: {self.url!r}>'


class Fetcher:
	def __init__(self, client: Client, session: Session = None, xcsrf_token_name: str = 'X-CSRF-Token'):
		self.client = client
		self.session = session or Session()
		
		self.xcsrf_token_name = xcsrf_token_name
		
		self.set_header('Content-Type', 'application/json')
		self.set_header('User-Agent', 'Roblox/WinInet')
		self.set_header('Referer', 'https://www.roblox.com/')
	
	def set_header(self, header: str, value: Any):
		self.session.headers[header] = value
	
	def set_cookie(self, name: str, value: Any):
		self.session.cookies[name] = value
	
	def request(self, method: str, url: str, *args, **kwargs) -> tuple[dict, Response]:
		if self.client.config._debug_print_requests:
			print(f'{method} request: {url}')
		
		response = self.session.request(method, url, *args, **kwargs)
		
		if response.status_code == 403 and self.xcsrf_token_name in response.headers:
			self.set_header(self.xcsrf_token_name, response.headers.get(self.xcsrf_token_name))
			
			response = self.session.request(method, url, *args, **kwargs)
		
		return response.json(), response
	
	def get(self, url: str, *args, **kwargs) -> tuple[dict, Response]:
		return self.request("GET", url, *args, **kwargs)
	
	def post(self, url: str, *args, **kwargs) -> tuple[dict, Response]:
		return self.request("POST", url, *args, **kwargs)
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ..client import Client

class EconomyProvider:
	def __init__(self, client: Client) -> None:
		self.client = client
	
	def get_user_has_premium(self, user_id: int):
		client = self.client
		
		_, premium_response = client.fetcher.get(
			url=client.url_generator.get_url('premiumfeatures', f'v1/users/{user_id}/validate_membership')
		)
		
		return premium_response.text == 'true'
	
	def get_user_currency(self, user_id: int):
		client = self.client
		
		currency_data, _ = client.fetcher.get(
			url=client.url_generator.get_url('economy', f'v1/users/{user_id}/currency')
		)
		
		return currency_data['robux']
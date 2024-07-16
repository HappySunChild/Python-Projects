from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Optional

from dateutil.parser import parse
from ..enums import AssetType
from ..classes.base import BaseData
from ..utility.fetcher import PageIterator, SortOrder

if TYPE_CHECKING:
	from ..client import Client

class Asset(BaseData):
	def __init__(self, client: Client, asset_data: dict) -> None:
		self.id = asset_data.get('assetId')
		
		self.created = parse(asset_data['created']).timestamp()
		self.updated = parse(asset_data['updated']).timestamp()
		
		owner = None
		
		if client.config.allow_partials:
			from ..classes.users import PartialUser
			
			owner = PartialUser(client, asset_data['owner'])
		else:
			owner = client.get_User(asset_data['owner']['userId'])
		
		self.owner = owner

class InventoryProvider:
	def __init__(self, client: Client) -> None:
		self.client = client
	
	def can_view_inventory(self, user_id: int):
		client = self.client
		
		inventory_data, _ = client.fetcher.get(
			url=client.url_generator.get_url('inventory', f'v1/users/{user_id}/can-view-inventory')
		)
		
		return inventory_data['canView']
	
	def get_user_inventory(self, user_id: int, asset_type: AssetType, page_size: int = 10, sort_order: SortOrder = SortOrder.Descending, handler: Optional[Callable] = None):
		client = self.client
		
		if handler is None:
			handler = lambda data: Asset(client, data)
		
		return PageIterator(
			fetcher=client.fetcher,
			url=client.url_generator.get_url('inventory', f'v2/users/{user_id}/inventory/{asset_type.value}'),
			page_size=page_size,
			sort_order=sort_order,
			handler=handler
		)
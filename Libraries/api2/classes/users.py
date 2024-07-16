from __future__ import annotations
from typing import TYPE_CHECKING

from dateutil.parser import parse

from .base import BaseData
from .badges import Badge
from ..enums import AssetType
from ..utility.fetcher import PageIterator, SortOrder

if TYPE_CHECKING:
	from ..client import Client

class FriendRequest(BaseData):
	def __init__(self, client: Client, data: dict) -> None:
		friend_request_data = data['friendRequest']
		
		self.client = client
		
		self.id = friend_request_data.get('senderId')
		self.source_universe_id = friend_request_data.get('sourceUniverseId')
		self.origin_source_type = friend_request_data.get('originSourceType')
		self.contact_name = friend_request_data.get('contactName')
		self.sent_at = parse(friend_request_data['sentAt']).timestamp()
		
		self.origin_user = User(client, data) # why does friend request contain the same information as a user who knows
	
	def accept(self):
		client = self.client
		client.fetcher.post(
			url=client.url_generator.get_url('friends', f'v1/users/{self.id}/accept-friend-request')
		)
	
	def decline(self):
		client = self.client
		client.fetcher.post(
			url=client.url_generator.get_url('friends', f'v1/users/{self.id}/decline-friend-request')
		)
	
	def __repr__(self) -> str:
		return f'<{self.__class__.__name__}: {self.origin_user.fullname}>'

class BaseUser(BaseData):
	def __init__(self, client: Client, user_id: int):
		self.client = client
		self.id = user_id
	
	def get_presence(self):
		presences = self.client.presence.get_user_presences([self.id])
		
		try:
			return presences[0]
		except IndexError:
			return None
	
	def get_friends(self):
		client = self.client
		
		friends_data, _ = client.fetcher.get(
			url=client.url_generator.get_url('friends', f'v1/users/{self.id}/friends')
		)
		
		return [Friend(client, friend_data) for friend_data in friends_data['data']]
	
	def get_mutuals_with(self, other: BaseUser):
		mutuals = []
		
		friends = self.get_friends()
		other_friends = other.get_friends()
		
		mutuals = [friend if friend in other_friends else None for friend in friends]
		
		for _ in range(mutuals.count(None)):
			mutuals.remove(None)
		
		return mutuals
	
	def get_currency(self):
		return self.client.economy.get_user_currency(self.id)
	
	def get_badges(self, page_size: int = 10, sort_order: SortOrder = SortOrder.Descending):
		client = self.client
		
		return PageIterator(
			fetcher=client.fetcher,
			url=client.url_generator.get_url('badges', f'v1/users/{self.id}/badges'),
			sort_order=sort_order,
			page_size=page_size,
			handler=lambda data: Badge(client, data)
		)
	
	def get_games(self, page_size: int = 10, sort_order: SortOrder = SortOrder.Ascending):
		from .universes import Universe
		
		client = self.client
		
		return PageIterator(
			fetcher=client.fetcher,
			url=client.url_generator.get_url('games', f'v2/users/{self.id}/games'),
			page_size=page_size,
			sort_order=sort_order,
			handler=lambda data: Universe(client, data)
		)
	
	def get_inventory(self, asset_type: AssetType, page_size: int = 10, sort_order: SortOrder = SortOrder.Ascending):
		client = self.client
		
		return client.inventory.get_user_inventory(
			user_id=self.id,
			asset_type=asset_type,
			page_size=page_size,
			sort_order=sort_order
		)
	
	def get_currency(self):
		return self.client.economy.get_user_currency(self.id)
	
	@property
	def can_view_inventory(self):
		return self.client.inventory.can_view_inventory(self.id)
	
	@property
	def has_premium(self):
		if self._has_premium:
			return self._has_premium
		
		has_premium = self.client.economy.get_user_has_premium(self.id)
		
		self._has_premium = has_premium
		
		return has_premium
	
	@property
	def link(self):
		return f'https://www.roblox.com/{self.id}/profile'
	
	def __repr__(self) -> str:
		return f'<{self.__class__.__name__}: {self.id}>'

class PartialUser(BaseUser):
	def __init__(self, client: Client, partial_data: dict):
		super().__init__(client, partial_data.get('userId'))
		
		self.name = partial_data.get('username', partial_data.get('name'))
		self.display_name = partial_data.get('displayName')

class User(BaseUser):
	def __init__(self, client: Client, data: dict):
		_id = data.get('id', data.get('userId'))
		
		super().__init__(client, _id)
		
		self.raw = data
		
		self.name = data.get('name', data.get('username'))
		self.display_name = data.get('displayName')
		self.description = data.get('description')
		
		self.is_banned = data.get('isBanned')
		self.has_verified_badge = data.get('hasVerifiedBadge')
		
		if data.get('created'):
			self.created = parse(data.get('created')).timestamp()
	
	def update_info(self):
		client = self.client
		
		user_data, _ = client.fetcher.get(
			url=client.url_generator.get_url('users', f'v1/users/{self.id}')
		)
		
		self.__init__(client, user_data)
	
	@property
	def fullname(self):
		return f'{self.display_name} @{self.name}'
	
	def __repr__(self) -> str:
		return f'<{self.__class__.__name__}: {self.fullname}>'

class AuthenticatedUser(User):
	def __init__(self, client: Client, data: dict):
		super().__init__(client, data)
	
	def follow_user(self, target_id: int):
		client = self.client
		_, res = client.fetcher.post(
			url=client.url_generator.get_url('friends', f'v1/users/{target_id}/follow')
		)
		
		return res
	
	def unfollow_user(self, target_id: int):
		client = self.client
		_, res = client.fetcher.post(
			url=client.url_generator.get_url('friends', f'v1/users/{target_id}/unfollow')
		)
		
		return res
	
	
	def get_friend_requets(self, page_size: int = 10, sort_order: SortOrder = SortOrder.Descending):
		client = self.client
		
		return PageIterator(
			fetcher=client.fetcher,
			url=client.url_generator.get_url('friends', 'v1/my/friends/requests'),
			page_size=page_size,
			sort_order=sort_order,
			handler=lambda data: FriendRequest(client, data)
		)
	
	def send_friend_request(self, target_id: int):
		client = self.client
		_, res = client.fetcher.post(
			url=client.url_generator.get_url('friends', f'v1/users/{target_id}/request-friendship')
		)
		
		return res
	
	def unfriend_user(self, target_id: int):
		client = self.client
		client.fetcher.post(
			url=client.url_generator.get_url('friends', f'v1/users/{target_id}/unfriend')
		)

class Friend(User):
	def __init__(self, client: Client, data: dict):
		super().__init__(client, data)
		
		self.is_online = data.get('isOnline')
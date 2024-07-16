from typing import Optional

from .utility.fetcher import Fetcher
from .utility.url import URLGenerator

from .services.presence import PresenceProvider
from .services.economy import EconomyProvider
from .services.inventory import InventoryProvider

from .classes.groups import Group, BaseGroup
from .classes.users import User, BaseUser, AuthenticatedUser
from .classes.places import Place, BasePlace
from .classes.universes import Universe, BaseUniverse
from .classes.badges import Badge

class ClientConfig:
	def __init__(self, allow_partials: bool = True, debug_print_requests: bool = False):
		self._debug_print_requests = debug_print_requests
		self.allow_partials = allow_partials

class Client:
	def __init__(self, token: str = None, config: Optional[ClientConfig] = None , base_url = 'roblox.com'):
		if config is None:
			config = ClientConfig()
		
		self.config = config
		
		self.fetcher = Fetcher(self)
		self.url_generator = URLGenerator(base_url)
		
		self.economy = EconomyProvider(self)
		self.presence = PresenceProvider(self)
		self.inventory = InventoryProvider(self)
		
		if token:
			self.set_token(token)
	
	def _get_universe_id(self, place_id: int):
		universe_data, _ = self.fetcher.get(
			url=self.url_generator.get_url('apis', f'universes/v1/places/{place_id}/universe')
		)
		
		return universe_data.get('universeId')
	
	def set_token(self, token: str):
		self.fetcher.set_cookie('.ROBLOSECURITY', token)
	
	
	def get_User(self, user_id: int):
		user_data, _ = self.fetcher.get(
			url=self.url_generator.get_url('users', f'v1/users/{user_id}')
		)
		
		return User(self, user_data)
	
	def get_base_User(self, user_id: int):
		return BaseUser(self, user_id)
	
	def get_authenticated_User(self, full: bool = True):
		user_data, _ = self.fetcher.get(
			url=self.url_generator.get_url('users', f'v1/users/authenticated')
		)
		
		if full:
			authenticated_user = AuthenticatedUser(self, {'id': user_data['id']})
			authenticated_user.update_info()
			
			return authenticated_user
		
		return BaseUser(self, user_data['id'])
	
	
	def get_Group(self, group_id: int):
		group_data, _ = self.fetcher.get(
			url=self.url_generator.get_url('groups', f'v1/groups/{group_id}')
		)
		
		return Group(self, group_data)
	
	def get_base_Group(self, group_id: int):
		return BaseGroup(self, group_id)
	
	
	def get_Universe(self, universe_id: int=None, place_id: int=None):
		if place_id and not universe_id:
			universe_id = self._get_universe_id(place_id)
		
		return self.multiget_Universes([universe_id])[0]
	
	def get_base_Universe(self, universe_id: int):
		return BaseUniverse(universe_id)
	
	def multiget_Universes(self, universe_ids: list[int]):
		universes_data, _ = self.fetcher.get(
			url=self.url_generator.get_url('games', 'v1/games'),
			params = {'universeIds': universe_ids}
		)
		
		return [Universe(self, data=universe_data) for universe_data in universes_data['data']]
	
	def multiget_Universes_place_ids(self, place_ids: list[int]):
		places = self.multiget_Places(place_ids)
		
		return self.multiget_Universes([place.universe_id for place in places])
	
	
	def get_Place(self, place_id: int):
		return self.multiget_Places([place_id])[0]
	
	def get_base_Place(self, place_id: int):
		return BasePlace(self, place_id)
	
	def multiget_Places(self, place_ids: list[int]):
		places_data, _ = self.fetcher.get(
			url=self.url_generator.get_url('games', 'v1/games/multiget-place-details'),
			params={'placeIds': place_ids}
		)
		
		return [Place(self, place_data) for place_data in places_data]
	
	
	def get_Badge(self, badge_id: int):
		badge_data, _ = self.fetcher.get(
			url=self.url_generator.get_url('badges', f'v1/badges/{badge_id}')
		)
		
		return Badge(self, badge_data)
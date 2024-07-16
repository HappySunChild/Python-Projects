from __future__ import annotations
from typing import TYPE_CHECKING

from dateutil.parser import parse

from .base import BaseData
from .places import BasePlace
from ..utility.fetcher import PageIterator

if TYPE_CHECKING:
	from ..client import Client

class BaseUniverse(BaseData):
	def __init__(self, client: Client, universe_id: int):
		self.client = client
		self.id = universe_id
	
	def get_badges(self, page_size: int = 10):
		from .badges import Badge
		
		client = self.client
		
		return PageIterator(
			fetcher=client.fetcher,
			url=client.url_generator.get_url('badges', f'v1/universes/{self.id}/badges'),
			page_size=page_size,
			handler=lambda data: Badge(client, data)
		)

class PartialUniverse(BaseUniverse):
	def __init__(self, client: Client, partial_data: dict):
		super().__init__(client, partial_data['id'])
		
		self.name = partial_data.get('name')
		
		place_id = None
		
		if partial_data.get('rootPlace'):
			place_id = partial_data['rootPlace']['id']
		else:
			place_id = partial_data.get('rootPlaceId')
		
		self.root_place = BasePlace(client, place_id)
	
	@property
	def link(self):
		return self.root_place.link

class Universe(PartialUniverse):
	def __init__(self, client: Client, data: dict):
		super().__init__(client, data)
		
		self.description = data.get('description')
		
		self.playing = data.get('playing')
		self.visits = data.get('visits')
		self.max_players = data.get('maxPlayers')
		
		self.is_favorited = data.get('isFavoritedByUser')
		self.favorited_count = data.get('favoritedCount')
		
		self.is_genre_enforced = data.get('isGenreEnforced')
		self.genre = data.get('genre')
		self.price = data.get('price')
		self.copying_allowed = data.get('copyingAllowed')
		
		self.created = parse(data.get('created')).timestamp()
		self.updated = parse(data.get('updated')).timestamp()
		
		creator_data = data.get('creator')
		
		if creator_data:
			creator_type = creator_data.get('type')
			creator_id = creator_data.get('id')
			
			new_creator = None
			
			if creator_type == 'User':
				from .users import BaseUser
				
				if client.config.allow_partials:
					new_creator = BaseUser(client, creator_id)
				else:
					new_creator = client.get_User(creator_id)
			elif creator_type == 'Group':
				from .groups import BaseGroup
				
				if client.config.allow_partials:
					new_creator = BaseGroup(client, creator_id)
				else:
					new_creator = client.get_Group(creator_id)
			
			self.creator = new_creator
	
	def __repr__(self) -> str:
		return f'<{self.__class__.__name__}: {self.name}>'
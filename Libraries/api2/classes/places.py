from __future__ import annotations
from typing import TYPE_CHECKING

from .base import BaseData
from ..utility.fetcher import PageIterator

if TYPE_CHECKING:
	from ..client import Client

class GameInstance(BaseData):
	def __init__(self, data: dict) -> None:
		self.job_id = data.get('id')
		
		self.max_players = data.get('maxPlayers')
		self.playing = data.get('playing')
		
		self.fps = data.get('fps')
		self.ping = data.get('ping')
		
		self.player = data.get('players')
	
	def __repr__(self) -> str:
		return f'<{self.__class__.__name__} id={self.job_id!r}>'

class BasePlace(BaseData):
	def __init__(self, client: Client, place_id: int):
		self.client = client
		self.id = place_id
	
	def get_instances(self, page_size: int = 10):
		return PageIterator(
			fetcher=self.client.fetcher,
			url = self.client.url_generator.get_url('games', f'v1/games/{self.id}/servers/0'),
			page_size=page_size,
			handler=lambda data: GameInstance(data)
		)
	
	@property
	def link(self):
		return f'https://www.roblox.com/games/{self.id}/game'

class Place(BasePlace):
	def __init__(self, client: Client, data: dict):
		super().__init__(client, data['placeId'])
		
		self.name = data.get('name')
		self.description = data.get('description')
		
		self.is_playable = data.get('isPlayable')
		self.reason_prohibited = data.get('reasonProhibited')
		
		self.price = data.get('price')
		self.universe_id = data.get('universeId')
		
		self.builder = data.get('builder')
		self.builderId = data.get('builderId')
	
	def get_Universe(self):
		client = self.client
		
		return client.get_Universe(universe_id=self.universe_id)
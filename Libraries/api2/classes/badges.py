from __future__ import annotations
from typing import TYPE_CHECKING

from dateutil.parser import parse

from .base import BaseData
from .universes import PartialUniverse

if TYPE_CHECKING:
	from ..client import Client

class BadgeStatistics:
	def __init__(self, statistic_data: dict) -> None:
		self.past_day_awarded_count = statistic_data.get('pastDayAwardedCount')
		self.awarded_count = statistic_data.get('awardedCount')
		self.win_rate_percentage = statistic_data.get('winRatePercentage')

class BaseBadge(BaseData):
	def __init__(self, client: Client, badge_id: int) -> None:
		self.client = client
		self.id = badge_id
	
	@property
	def link(self):
		return f'https://www.roblox.com/badges/{self.id}/badge'

class Badge(BaseBadge):
	def __init__(self, client: Client, data: dict) -> None:
		super().__init__(client, data['id'])
		
		self.name = data.get('name')
		self.description = data.get('description')
		self.enabled = data.get('enabled')
		
		self.created = parse(data['created']).timestamp()
		self.updated = parse(data['updated']).timestamp()
		
		self.statistics = BadgeStatistics(data['statistics'])
		
		universe_data = data.get('awardingUniverse')
		
		if universe_data:
			awarding_universe = None
			
			if client.config.allow_partials:
				awarding_universe = PartialUniverse(client, universe_data)
			else:
				awarding_universe = client.get_Universe(universe_id=universe_data.get('id'))
			
			self.awarding_universe = awarding_universe
	
	def __repr__(self) -> str:
		return f'<{self.__class__.__name__}: {self.name}>'
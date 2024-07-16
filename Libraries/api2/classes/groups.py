from __future__ import annotations
from typing import TYPE_CHECKING

from dateutil.parser import parse
from ..utility.fetcher import PageIterator

from .base import BaseData
from .users import User

if TYPE_CHECKING:
	from ..client import Client

class GroupShout(BaseData):
	def __init__(self, client: Client, data: dict) -> None:
		self.body = data.get('body')
		
		self.poster = User(client, data.get('poster'))
		
		self.created = parse(data.get('created')).timestamp()
		self.updated = parse(data.get('updated')).timestamp()

class GroupRole(BaseData):
	def __init__(self, data: dict) -> None:
		self.id = data.get('id')
		self.name = data.get('name')
		self.rank = data.get('rank')

class GroupMember(User):
	def __init__(self, client: Client, data: dict, group: Group):
		super().__init__(client, data['user'])
		
		self.group = group
		self.role = GroupRole(data['role'])

class BaseGroup(BaseData):
	def __init__(self, client: Client, group_id: int) -> None:
		self.client = client
		self.id = group_id
	
	def get_members(self, page_size: int = 10):
		return PageIterator(
			fetcher=self.client.fetcher,
			url=self.client.url_generator.get_url('groups', f'v1/groups/{self.id}/users'),
			page_size=page_size,
			handler=lambda data: GroupMember(self.client, data, self)
		)

class Group(BaseGroup):
	def __init__(self, client: Client, data: dict) -> None:
		super().__init__(client, data['id'])
		
		self.name = data.get('name')
		self.description = data.get('description')
		
		self.member_count = data.get('memberCount')
		self.public_entry_allowed = data.get('publicEntryAllowed')
		self.is_locked = data.get('isLocked', False)
		
		self.owner = User(client, data.get('owner')) if data.get('owner') else None
	
	def __repr__(self) -> str:
		return f'<{self.__class__.__name__}: {self.name}>'
# RoAPI __init__.py

import logging as log
from dateutil.parser import parse
from .fetch import fetch, setToken, getToken
from .Endpoints import (badges, economy, games, groups, users)

Cache = {
	'users': {},
	'games': {},
	'groups': {}
}
PresenceTypes = [
	'Offline',
	'Online',
	'InGame',
	'Studio',
	'Invisible'
]

# Base Data Class

class BaseData:
	FormatString = r'ID: {0.Id} NAME: {0.Name}'
	CacheVar = None
	
	def __init__(self, jsonInfo: dict = None) -> None:
		if not jsonInfo:
			jsonInfo = {}
		
		self.Id = _search(jsonInfo, 'id', 'userId', 'assetId', default=-1)
		self.Name = _search(jsonInfo, 'name', 'username', default=None)
		
		self.Raw = jsonInfo
		
		if self.CacheVar:
			Cache[self.CacheVar][self.Id] = self.Raw
	
	def __repr__(self) -> str:
		return str(self)
	
	def __str__(self) -> str:
		return self.FormatString.format(self)
	
	def __getattr__(self, attr):
		return None

# Misc Data Classes

class Role(BaseData):
	FormatString = r'Role: {0.Name} [{0.Id}]'
	
	def __init__(self, jsonInfo: dict) -> None:
		super().__init__(jsonInfo)
		
		self.Rank = jsonInfo.get('rank', 0)
		self.MemberCount = jsonInfo.get('memberCount', 0)

class Asset(BaseData):
	FormatString = r'Asset: {0.Name} : {0.AssetType} [0.Link]'
	
	def __init__(self, jsonInfo: dict = None) -> None:
		super().__init__(jsonInfo)
		
		self.AssetType = jsonInfo.get('assetType', 'Model')
	
	@property
	def Link(self):
		return f'https://www.roblox.com/library/{self.Id}/_'

class Badge(BaseData):
	FormatString = r'Badge: {0.Name} [{0.Link}]'
	
	def __init__(self, badgeId: int = None, jsonInfo: dict = None) -> None:
		if badgeId and not jsonInfo:
			jsonInfo = badges.info(badgeId)
		
		super().__init__(jsonInfo)
		
		self.Enabled = jsonInfo.get('enabled', True)
		self.Description = jsonInfo.get('description', 'DESC')
		
		self.Created = parse(jsonInfo.get('created'))
		self.Updated = parse(jsonInfo.get('updated'))
	
	@property
	def Link(self):
		return f'https://www.roblox.com/badges/{self.Id}/_'

class UserPresence(BaseData):
	FormatString = r'Presence: {0.UserId}, {0.PresenceType} [{0.LastLocation}]'
	
	def __init__(self, jsonInfo: dict = None) -> None:
		super().__init__(jsonInfo)
		
		self.PresenceType = jsonInfo.get('userPresenceType', 0)
		self.LastLocation = jsonInfo.get('lastLocation', 'Offline')
		self.LastOnline = parse(jsonInfo.get('lastOnline'))
		
		self.JobId = jsonInfo.get('gameId')
		self.PlaceId = jsonInfo.get('rootPlaceId', 1)
		self.UniverseId = jsonInfo.get('universeId', 1)
		
		self.UserId = jsonInfo.get('userId', -1)
	
	def updateInfo(self):
		newData = users.presence(self.UserId)
		
		self.__init__(jsonInfo=newData)

# Main Data Classes

class Game(BaseData):
	FormatString = r'Game: {0.Name} [{0.Link}]'
	CacheVar = 'games'
	
	def __init__(self, placeId: int = None, jsonInfo: dict = None) -> None:
		if placeId and not jsonInfo:
			jsonInfo = _search(Cache[self.CacheVar], placeId, resolveCallback=games.info, resolveArgs=[placeId])
		
		super().__init__(jsonInfo)
		
		self.Id = jsonInfo.get('rootPlaceId', jsonInfo.get('rootPlace', {}).get('id', 0)) # id overwrite because placeId isn't the id
		self.UniverseId = jsonInfo.get('id', None)
		self.Description = jsonInfo.get('description', None)
		self.Genre = jsonInfo.get('genre', 'All')
		
		self.Visits = _search(jsonInfo, 'visits', 'placeVisits', default=0)
		self.Active = jsonInfo.get('playing', 0)
		self.Favorites = jsonInfo.get('favoritedCount', 0)
		self.MaxServerSize = jsonInfo.get('maxPlayers', -1)
		
		self.Created = parse(jsonInfo.get('created'))
		self.Updated = parse(jsonInfo.get('updated'))
		
		creator = jsonInfo.get('creator')
		
		if creator:
			creatorType = creator.get('type')
			
			if creatorType == 'User':
				creator = User(jsonInfo=creator)
			elif creatorType == 'Group':
				creator = Group(jsonInfo=creator)
			else:
				log.error("game don't got a creator")
		
		self.Creator = creator
	
	@property
	def Link(self):
		return f'https://www.roblox.com/games/{self.Id}/_'
	
	def updateInfo(self):
		newData = games.info(placeId = self.Id, universeId = self.UniverseId)
		
		self.__init__(jsonInfo=newData)

class User(BaseData):
	FormatString = 'User: {0.FullName} [{0.Link}] Banned: {0.IsBanned}'
	CacheVar = 'users'
	
	def __init__(self, userId: int = None, jsonInfo: dict = None) -> None:
		if userId and not jsonInfo:
			jsonInfo = _search(Cache[self.CacheVar], userId, resolveCallback=users.info, resolveArgs=[userId])
		
		super().__init__(jsonInfo=jsonInfo)
		
		self.DisplayName = jsonInfo.get('displayName', "DISPLAYNAME")
		
		self.IsBanned = jsonInfo.get('isBanned', False)
		self.IsVerified = jsonInfo.get('hasVerifiedBadge', False)
		
		self.Presence = None
		
		self.Friends = []
		self.Groups = []
		self.Games = []
		self.Badges = []
		self.Inventory = {}
	
	@property
	def Link(self):
		return f'https://www.roblox.com/users/{self.Id}/profile'
	
	@property
	def FullName(self):
		return f'{self.DisplayName:20} @{self.Name:20}'
	
	def getPresence(self):
		if self.Presence:
			self.Presence.updateInfo()
			
			return self.Presence
		else:
			userPresence = UserPresence(users.presence(self.Id))
			
			self.Presence = userPresence
			
			return userPresence
	
	def getFriends(self):
		Friends = []
		
		for friend in users.friends(self.Id):
			Friends.append(User(jsonInfo=friend))
		
		self.Friends = Friends
		
		return Friends
	
	def getGroups(self):
		Groups = []
		
		for group in users.groups(self.Id):
			Groups.append(Group(jsonInfo=group.get('group')))
		
		self.Groups = Groups
		
		return Groups
	
	def getGames(self, pageLimit: int = None, pageSize: int = None) -> list[Game]:
		Games = []
		
		pages = users.games(self.Id, pageSize).getPages(pageLimit)
		
		for page in pages:
			for gameRaw in page.Data:
				Games.append(Game(jsonInfo=gameRaw))
		
		self.Games = Games
		
		return Games
	
	def getInventory(self, assetType: str, pageLimit: int = None, pageSize: int = None) -> list[Asset]:
		Assets = []
		
		pages = users.inventory(self.Id, assetType, pageSize).getPages(pageLimit)
		
		for page in pages:
			for assetRaw in page.Data:
				Assets.append(Asset(jsonInfo=assetRaw))
		
		self.Inventory[assetType] = Assets
		
		return Assets
	
	def getBadges(self, pageLimit: int = None, pageSize: int = None) -> list[Badge]:
		Badges = []
		
		pages = users.badges(self.Id, pageSize).getPages(pageLimit)
		
		for page in pages:
			for badgeRaw in page.Data:
				Badges.append(Badge(jsonInfo=badgeRaw))
		
		self.Badges = Badges
		
		return Badges
	
	def updateInfo(self):
		newData = users.info(self.Id)
		
		self.__init__(jsonInfo=newData)

class Group(BaseData):
	FormatString = r'Group: {0.Name} [{0.Link}]'
	CacheVar = 'groups'
	
	def __init__(self, groupId: int = None, jsonInfo: dict = None) -> None:
		if groupId and not jsonInfo:
			jsonInfo = _search(Cache[self.CacheVar], groupId, resolveCallback=groups.info, resolveArgs=[groupId])
		
		super().__init__(jsonInfo)
		
		self.IsVerified = jsonInfo.get('hasVerifiedBadge', False)
		self.Owner = User(jsonInfo=jsonInfo.get('owner', {}))
		
		self.Members = []
		self.Games = []
		self.Roles = []
	
	@property
	def Link(self):
		return f'https://www.roblox.com/groups/{self.Id}/_'
	
	def getMembers(self, pageLimit: int = None, pageSize: int = None):
		Members = []
		
		pages = groups.members(self.Id, pageSize).getPages(pageLimit)
		
		for page in pages:
			for member in page.Data:
				Members.append(User(jsonInfo=member))
		
		self.Members = Members
		
		return Members
	
	def getGames(self, pageLimit: int = None, pageSize: int = None):
		Games = []
		
		pages = groups.games(self.Id, pageSize).getPages(pageLimit)
		
		for page in pages:
			for gameRaw in page.Data:
				Games.append(Game(jsonInfo=gameRaw))
		
		self.Games = Games
		
		return Games
	
	def getRoles(self):
		Roles = []
		
		for role in groups.roles(self.Id):
			Roles.append(Role(jsonInfo=role))
		
		self.Roles = Roles
		
		return Roles
	
	def updateInfo(self):
		newData = groups.info(self.Id)
		
		self.__init__(jsonInfo=newData)

# helper methods

def _search(object: dict, *indices: str, resolveCallback = None, resolveArgs: list[str] = None, default = None):
	for index in indices:
		val = object.get(index, None)
		
		if val:
			return val
	
	if resolveCallback:
		default = resolveCallback(*resolveArgs)
	
	return default

# badge methods

if __name__ == "__main__":
	u = User(223478192)
	
	for badge in u.getBadges(1, 10):
		print(badge)
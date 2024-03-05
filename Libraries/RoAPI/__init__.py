# RoAPI __init__.py

import requests as http
from typing import Any, Callable
from time import sleep
from datetime import datetime

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

RobloxToken = ''
RetryFetches = True
RetryTimer = 10

# Paging classes

class Page:
	def __init__(self, rawPageData: dict) -> None:
		self.Pager = None
		self.PageNumber = 1
		
		self.PreviousCursor = rawPageData.get('previousPageCursor', None)
		self.NextCursor = rawPageData.get('nextPageCursor', None)
		self.Data = rawPageData.get('data', [])
		
		self.Raw = rawPageData
	
	@property
	def NumEntries(self):
		return len(self.Data)
	
	def __repr__(self) -> str:
		return f"Page #{self.PageNumber} ({self.NumEntries} entries)"
	
	def __str__(self) -> str:
		return f"Page: #{self.PageNumber} <- ({self.Pager})"

class Pager: # meant for endpoints that return pages of information
	def __init__(self, url: str, pageSize: int = 25) -> None:
		self.BaseUrl = url
		
		self.Pages: list[Page] = []
		
		self.PageSize = pageSize
		self.PageNumber = 1
		self.PageCursor = ''
		self.PageRaw = None
		
		self.IsFinished = False
	
	def getCurrentPage(self) -> Page: # returns current page data
		if self.IsFinished:
			return
		
		requestUrl = self.BaseUrl + f'&cursor={self.PageCursor}&limit={self.PageSize}'
		rawPageData = _fetch(requestUrl, {'IsEnd': True})
		
		newPage = Page(rawPageData)
		newPage.PageNumber = self.PageNumber
		newPage.Pager = self
		
		self.PageRaw = rawPageData
		self.Pages.append(newPage)
		
		return newPage
	
	def advanceToNextPage(self) -> bool: # doesn't actually get the page data, just shifts everything to be ready for the next page
		if not self.PageRaw:
			self.getCurrentPage()
		
		cursor = self.PageRaw.get('nextPageCursor')
		
		if not cursor:
			self.IsFinished = True
			
			return False
		
		self.PageNumber += 1
		self.PageCursor = cursor
		
		self.PageRaw = None # reset page data
		
		return True
	
	def getPages(self, pageLimit: int = 10) -> list[Page]:
		if self.IsFinished:
			return
		
		if not pageLimit:
			pageLimit = 10
		
		while not self.IsFinished and self.PageNumber <= pageLimit:
			self.getCurrentPage() # automatically appends to instance's `Pages` list
			self.advanceToNextPage()
		
		return self.Pages
	
	@property
	def NumEntries(self):
		count = 0
		
		for page in self.Pages:
			count += page.NumEntries
		
		return count
	
	def __str__(self) -> str:
		return f"Pager: [{self.BaseUrl}&cursor={self.PageCursor}&limit={self.PageSize}]"

# Base Data Class

class BaseData:
	FormatString = r'ID: {0.Id} NAME: {0.Name}'
	RequestUrl = r''
	CacheVar = None
	
	def __init__(self, base: dict = None) -> None:
		if not base:
			base = {}
		
		self.Id = _search(base, 'id', 'userId', 'assetId', default=-1)
		self.Name = _search(base, 'name', 'username', default='NULL')
		
		self.Raw = base
		
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
	RequestUrl = None
	
	def __init__(self, base: dict) -> None:
		super().__init__(base)
		
		self.Rank = base.get('rank', 0)
		self.MemberCount = base.get('memberCount', 0)

class Asset(BaseData):
	FormatString = r'Asset: {0.Name} : {0.AssetType} [0.Link]'
	
	def __init__(self, base: dict = None) -> None:
		super().__init__(base)
		
		self.AssetType = base.get('assetType', 'Model')
	
	@property
	def Link(self):
		return f'https://www.roblox.com/library/{self.Id}/_'

class Badge(BaseData):
	FormatString = r'Badge: {0.Name} [{0.Link}]'
	
	def __init__(self, badgeId: int = None, base: dict = None) -> None:
		if badgeId and not base:
			base = fetchBadgeInfo(badgeId)
		
		super().__init__(base)
		
		self.Enabled = base.get('enabled', True)
		self.Description = base.get('description', 'DESC')
		
		self.Created = _toEpoch(base.get('created'))
		self.Updated = _toEpoch(base.get('updated'))
	
	@property
	def Link(self):
		return f'https://www.roblox.com/badges/{self.Id}/_'

# Main Data Classes

class Game(BaseData):
	FormatString = r'Game: {0.Name} [{0.Link}]'
	CacheVar = 'games'
	
	def __init__(self, placeId: int = None, base: dict = None) -> None:
		if placeId and not base:
			base = _search(Cache[self.CacheVar], placeId, resolveCallback=fetchGameInfo, resolveArgs=[placeId])
		
		super().__init__(base)
		
		self.Id = base.get('rootPlaceId', base.get('rootPlace', {}).get('id', 0)) # id overwrite because placeId isn't the id
		self.UniverseId = base.get('id', None)
		self.Description = base.get('description', None)
		self.Genre = base.get('genre', 'All')
		
		self.Visits = _search(base, 'visits', 'placeVisits', default=0)
		self.Active = base.get('playing', 0)
		self.Favorites = base.get('favoritedCount', 0)
		self.MaxServerSize = base.get('maxPlayers', -1)
		
		self.Created = _toEpoch(base.get('created'))
		self.Updated = _toEpoch(base.get('updated'))
		
		creator = base.get('creator')
		
		if creator:
			creatorType = creator.get('type')
			
			if creatorType == 'User':
				creator = User(base=creator)
			elif creatorType == 'Group':
				creator = Group(base=creator)
			else:
				print("game don't got a creator")
		
		self.Creator = creator
	
	@property
	def Link(self):
		return f'https://www.roblox.com/games/{self.Id}/_'
	
	def updateInfo(self):
		newData = fetchGameInfo(placeId = self.Id, universeId = self.UniverseId)
		
		self.__init__(base=newData)

class User(BaseData):
	FormatString = 'User: {0.FullName} [{0.Link}] Banned: {0.IsBanned}'
	CacheVar = 'users'
	
	def __init__(self, userId: int = None, base: dict = None) -> None:
		if userId and not base:
			base = _search(Cache[self.CacheVar], userId, resolveCallback=fetchUserInfo, resolveArgs=[userId])
		
		super().__init__(base)
		
		self.DisplayName = base.get('displayName', "DISPLAYNAME")
		
		self.IsBanned = base.get('isBanned', False)
		self.IsVerified = base.get('hasVerifiedBadge', False)
		
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
		presence = fetchUserPresence(self.Id)
		
		self.Presence = presence
		
		return presence
	
	def getFriends(self):
		Friends = []
		
		for friend in fetchUserFriends(self.Id):
			Friends.append(User(base=friend))
		
		self.Friends = Friends
		
		return Friends
	
	def getGroups(self):
		Groups = []
		
		for group in fetchUserGroups(self.Id):
			Groups.append(Group(base=group.get('group')))
		
		self.Groups = Groups
		
		return Groups
	
	def getGames(self, pageLimit: int = None, pageSize: int = None) -> list[Game]:
		Games = []
		
		pages = fetchUserGames(self.Id, pageSize).getPages(pageLimit)
		
		for page in pages:
			for gameRaw in page.Data:
				Games.append(Game(base=gameRaw))
		
		self.Games = Games
		
		return Games
	
	def getInventory(self, assetType: str, pageLimit: int = None, pageSize: int = None) -> list[Asset]:
		Assets = []
		
		pages = fetchUserInventory(self.Id, assetType, pageSize).getPages(pageLimit)
		
		for page in pages:
			for assetRaw in page.Data:
				Assets.append(Asset(base=assetRaw))
		
		self.Inventory[assetType] = Assets
		
		return Assets
	
	def getBadges(self, pageLimit: int = None, pageSize: int = None) -> list[Badge]:
		Badges = []
		
		pages = fetchUserBadges(self.Id, pageSize).getPages(pageLimit)
		
		for page in pages:
			for badgeRaw in page.Data:
				Badges.append(Badge(base=badgeRaw))
		
		self.Badges = Badges
		
		return Badges
	
	def updateInfo(self):
		newData = fetchUserInfo(self.Id)
		
		self.__init__(base=newData)

class Group(BaseData):
	FormatString = r'Group: {0.Name} [{0.Link}]'
	CacheVar = 'groups'
	
	def __init__(self, groupId: int = None, base: dict = None) -> None:
		if groupId and not base:
			base = _search(Cache[self.CacheVar], groupId, resolveCallback=fetchGroupInfo, resolveArgs=[groupId])
		
		super().__init__(base)
		
		self.IsVerified = base.get('hasVerifiedBadge', False)
		self.Owner = User(base=base.get('owner', {}))
		
		self.Members = []
		self.Games = []
		self.Roles = []
	
	@property
	def Link(self):
		return f'https://www.roblox.com/groups/{self.Id}/_'
	
	def getMembers(self, pageLimit: int = None, pageSize: int = None):
		Members = []
		
		pages = fetchGroupMembers(self.Id, pageSize).getPages(pageLimit)
		
		for page in pages:
			for member in page.Data:
				Members.append(User(base=member))
		
		self.Members = Members
		
		return Members
	
	def getGames(self, pageLimit: int = None, pageSize: int = None):
		Games = []
		
		pages = fetchGroupGames(self.Id, pageSize).getPages(pageLimit)
		
		for page in pages:
			for gameRaw in page.Data:
				Games.append(Game(base=gameRaw))
		
		self.Games = Games
		
		return Games
	
	def getRoles(self):
		Roles = []
		
		for role in fetchGroupRoles(self.Id):
			Roles.append(Role(base=role))
		
		self.Roles = Roles
		
		return Roles
	
	def updateInfo(self):
		newData = fetchGroupInfo(self.Id)
		
		self.__init__(base=newData)

def _toEpoch(roblox_isoformat: str):
	if not roblox_isoformat:
		return 0
	
	fixed_format = roblox_isoformat.replace('Z', "+00:00")[:-6]
	
	return int(datetime.strptime(fixed_format, "%Y-%m-%dT%H:%M:%S.%f").timestamp())

# http methods

def _search(object: dict, *indices: str, resolveCallback: Callable[..., Any] = None, resolveArgs: list[str] = None, default: Any = None):
	for index in indices:
		val = object.get(index, None)
		
		if val:
			return val
	
	if resolveCallback:
		default = resolveCallback(*resolveArgs)
	
	return default

def _fetch(url: str, data: dict = None, resolve: Any = None, method: str = 'GET') -> dict:
	try:
		headers = {
			'cookie': RobloxToken
		}
		
		if method == 'GET':
			response = http.get(url, data=data, headers=headers)
		elif method == "POST":
			response = http.post(url, json=data, headers=headers)
		
		response.raise_for_status()
		
		return response.json()
	except http.exceptions.HTTPError as e:
		errData = response.json()
		
		if errData:
			errorList = errData.get('errors')
			
			for err in errorList:
				print(f"Error: [code: {err.get('code', -1)}, message: '{err.get('message')}']")
		
		if RetryFetches:
			print(f"Retrying fetch for '{url}'...")
			
			sleep(RetryTimer)
			
			return _fetch(url)
		
		print(f"Unable to fetch '{url}'. ({e})")
		
		return resolve

def isAvailable(endpointName: str = 'www'):
	endpointUrl = f'https://{endpointName}.roblox.com'
	
	try:
		response = http.get(endpointUrl)
		response.raise_for_status()
		
		return True
	except:
		return False

# user methods

def fetchUserInfo(userId: int):
	requestUrl = f'https://users.roblox.com/v1/users/{userId}'
	
	return _fetch(requestUrl)

def fetchUserFriends(userId: int):
	requestUrl = f'https://friends.roblox.com/v1/users/{userId}/friends'
	
	return _fetch(requestUrl).get('data', [])

def fetchUserGroups(userId: int):
	requestUrl = f'https://groups.roblox.com/v2/users/{userId}/groups/roles?includeLocked=false'
	
	return _fetch(requestUrl).get('data')

def fetchUserGames(userId: int, pageSize: int = 10) -> Pager:
	requestUrl = f'https://games.roblox.com/v2/users/{userId}/games?sortOrder=Desc'
	
	return Pager(requestUrl, pageSize)

def fetchUserPresence(userId: int):
	requestUrl = 'https://presence.roblox.com/v1/presence/users'
	data = {
		'userIds': [userId]
	}
	
	return _fetch(requestUrl, data, method='POST').get('userPresences', [])[0]

def fetchUserBadges(userId: int, pageSize: int = 10) -> Pager:
	requestUrl = f'https://badges.roblox.com/v1/users/{userId}/badges?sortOrder=Desc'
	
	return Pager(requestUrl, pageSize)

# inventory methods

def canViewInventory(userId: int):
	requestUrl = f'https://inventory.roblox.com/v1/users/{userId}/can-view-inventory'
	
	return _fetch(requestUrl).get('canView')

def fetchUserInventory(userId: int, assetType: str, pageSize: int = 25) -> Pager:
	requestUrl = f'https://inventory.roblox.com/v2/users/{userId}/inventory?assetTypes={assetType}&sortOrder=Desc'
	
	return Pager(requestUrl, pageSize)

# group methods

def fetchGroupInfo(groupId: int):
	requestUrl = f'https://groups.roblox.com/v1/groups/{groupId}'
	
	return _fetch(requestUrl)

def fetchGroupMembers(groupId: int, pageSize: int = 25) -> Pager:
	requestUrl = f'https://groups.roblox.com/v1/groups/{groupId}/users?sortOrder=Asc'
	
	return Pager(requestUrl, pageSize)

def fetchGroupRoles(groupId: int):
	requestUrl = f'https://groups.roblox.com/v1/groups/{groupId}/roles'
	
	return _fetch(requestUrl).get('roles')

def fetchGroupGames(groupId: int, pageSize: int = 25) -> Pager:
	requestUrl = f'https://games.roblox.com/v2/groups/{groupId}/games?sortOrder=Asc'
	
	return Pager(requestUrl, pageSize)

# games methods

def fetchUniverseId(placeId: int):
	requestUrl = f'https://apis.roblox.com/universes/v1/places/{placeId}/universe'
	
	return _fetch(requestUrl).get('universeId')

def fetchGameInfo(placeId: int = None, universeId: int = None):
	if not universeId and placeId != None:
		universeId = fetchUniverseId(placeId)
	
	requestUrl = f'https://games.roblox.com/v1/games?universeIds={universeId}'
	
	return _fetch(requestUrl).get('data', [])[0]

# economy methods

def fetchRobuxCount():
	requestUrl = 'https://economy.roblox.com/v1/user/currency'
	
	return _fetch(requestUrl).get('robux')

# badge methods

def fetchBadgeInfo(badgeId: int):
	requestUrl = f'https://badges.roblox.com/v1/badges/{badgeId}'
	
	return _fetch(requestUrl)

if __name__ == "__main__":
	u = User(223478192)
	
	for badge in u.getBadges(1, 10):
		print(badge)

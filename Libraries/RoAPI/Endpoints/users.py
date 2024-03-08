# RoAPI users.py

from ..fetch import fetch, genUrl, Pager

def canViewInventory(userId: int):
	return fetch(genUrl('inventory', f'v1/users/{userId}/can-view-inventory')).get('canView')

def info(userId: int):
	return fetch(genUrl('users', f'v1/users/{userId}'))

def friends(userId: int):
	return fetch(genUrl('friends', f'v1/users/{userId}/friends')).get('data', [])

def groups(userId: int):
	return fetch(genUrl('groups', f'v2/users/{userId}/groups/roles?includeLocked=false')).get('data')

def presence(userId: int):
	return fetch(genUrl('presence', 'v1/presence/users'), json={'userIds': [userId]}, method='POST').get('userPresences', [])[0]

def games(userId: int, pageSize: int = 10) -> Pager:
	return Pager(genUrl('games', f'v2/users/{userId}/games?sortOrder=Desc'), pageSize)

def badges(userId: int, pageSize: int = 10) -> Pager:
	return Pager(genUrl('badges', f'v1/users/{userId}/badges?sortOrder=Desc'), pageSize)

def inventory(userId: int, assetType: str, pageSize: int = 25) -> Pager:
	return Pager(genUrl('inventory', f'v2/users/{userId}/inventory?assetTypes={assetType}&sortOrder=Desc'), pageSize)

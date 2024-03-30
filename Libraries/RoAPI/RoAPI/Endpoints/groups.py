# RoAPI groups.py

from ..fetch import fetch, genUrl, Pager

def info(groupId: int):
	return fetch(genUrl('groups', f'v1/groups/{groupId}'))

def roles(groupId: int):
	return fetch(genUrl('groups', f'v1/groups/{groupId}/roles')).get('roles')

def members(groupId: int, pageSize: int = 25) -> Pager:
	return Pager(genUrl('groups', f'v1/groups/{groupId}/users?sortOrder=Asc'), pageSize)

def games(groupId: int, pageSize: int = 25) -> Pager:
	requestUrl = f'https://games.roblox.com/v2/groups/{groupId}/games?sortOrder=Asc'
	
	return Pager(requestUrl, pageSize)

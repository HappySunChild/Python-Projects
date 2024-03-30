# RoAPI games.py

from ..fetch import fetch, genUrl

def getUniverseId(placeId: int):
	return fetch(genUrl('apis', f'universes/v1/places/{placeId}/universe')).get('universeId')

def info(placeId: int = None, universeId: int = None):
	print(placeId, universeId)
	
	if universeId == None and placeId != None:
		universeId = getUniverseId(placeId)
	
	return fetch(genUrl('games', f'v1/games?universeIds={universeId}')).get('data', [])[0]
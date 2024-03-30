# RoAPI badges.py

from ..fetch import fetch, genUrl

def info(badgeId):
	return fetch(genUrl('badges', f'v1/badges/{badgeId}'))
# RoAPI economy.py

from ..fetch import fetch, genUrl

def robux():
	return fetch(genUrl('economy', 'v1/user/currency'))
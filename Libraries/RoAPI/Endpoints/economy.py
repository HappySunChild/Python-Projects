# RoAPI economy.py

import logging as log
from ..fetch import fetch, genUrl, _token

def robux():
	return fetch(genUrl('economy', 'v1/user/currency'))
import RoAPI as RoAPI
from PyHook import Webhook, Embed
from time import sleep, time

TrackingUser = RoAPI.User(int(input('UserID to track: ')))
BotWebhook = Webhook('WebhookId', 'WebhookToken')

PresenceColors = [
	0x383838,
	0x5081F2,
	0x4FFF38,
	0xF09D3E,
	0x000000
]

def discordLog(activityType: str, fieldData: dict, color: int = 0, footer: str = None):
	StatusEmbed = Embed('Ben Activity', f'{activityType} Update', color)
	StatusEmbed.setUrl(TrackingUser.Link)
	
	for name, value in fieldData.items():
		StatusEmbed.addField(name, value, True)
	
	StatusEmbed.setFooter(footer)
	
	BotWebhook.SendEmbeds(StatusEmbed)

def isUserInList(baseUser: RoAPI.User, list: list[RoAPI.User]):
	for user in list:
		if user.Id == baseUser.Id:
			return True
	
	return False

def comparePresence(last: dict, current: dict):
	if last == None or (current.get('userPresenceType') != last.get('userPresenceType')) or (current.get('lastLocation') != last.get('lastLocation')):
		presenceType = current.get('userPresenceType', 0)
		
		footer = None
		data = {
			'New Location:': RoAPI.PresenceTypes[presenceType]
		}
		
		if presenceType == 2: # InGame
			gameName = str(current.get('lastLocation', 'game'))
			
			gameId = current.get('rootPlaceId', 'placeId')
			jobId = current.get('gameId', 'jobId')
			
			footer = f'Roblox.GameLauncher.joinGameInstance({gameId}, "{jobId}");'
			
			data['New Location:'] = f'[{gameName}](https://www.roblox.com/games/{gameId}/{gameName.replace(" ", "-")})'
		
		discordLog('User Presence', data, PresenceColors[presenceType], footer)
	
	return None

def compareUserInfo(last: dict, current: dict):
	changes = {}
	
	for index, value in current.items():
		if last[index] != value:
			changes[index] = {'last': last[index], 'current': value}
	
	if len(changes) > 0:
		data = {}
		
		for label, dif in changes.items():
			data[label] = f"Old:\n{dif['last']}\n--------------\nNew:\n{dif['current']}"
		
		discordLog('User Info', data, 0xF02FA3)
	
	return None

def compareFriends(last: list[RoAPI.User], current: list[RoAPI.User]):
	if len(last) != len(current):
		AffectedUsers = []
		
		if len(last) < len(current): # gained a friend
			for user in current:
				if not isUserInList(user, last): # this user was added
					AffectedUsers.append({'user': user, 'added': True})
			
			col = 0x83F6B1
		else:
			for user in last:
				if not isUserInList(user, current): # this user was removed
					AffectedUsers.append({'user': user, 'added': False})
			
			col = 0xCF5B5B
		
		AffectedString = ''
		
		for user in AffectedUsers:
			roUser: RoAPI.User = user['user']
			AffectedString += '**{}** [{}]({})\n'.format(user["added"] and "+" or r"\-", roUser.FullName, roUser.Link)
		
		data = {
			'Old Friend Count:': len(last),
			'New Friend Count:': len(current),
			'Affected Users:': AffectedString
		}
		
		discordLog('User Friends', data, col)
	
	return None

def compareBadges(lastBadgeList: list[RoAPI.Badge], newBadgeList: list[RoAPI.Badge]):
	newBadges: list[RoAPI.Badge] = []
	
	for badge in newBadgeList:
		if not badge.Id in [b.Id for b in lastBadgeList]:
			newBadges.append(badge)
	
	if len(newBadges) > 0:
		badgeStr = ''
		
		for badge in newBadges:
			badgeStr += f'**+** [{badge.Name}]({badge.Link})\n'
		
		discordLog('User Badges', {'New Badges': badgeStr}, 0xFFAAAA)

def getCurrentStudioGame():
	latest = None
	
	for game in TrackingUser.getGames(1, 10):
		print(time())
		print(game.Updated, game.Name)
		
	return latest

def main():
	OfflineTimer = float(input('Seconds between api checks when user is offline: '))
	OnlineTimer = float(input('Seconds between api checks when user is online: '))
	
	BotWebhook.SendMessage(f'**Tracking [{TrackingUser.Name}]({TrackingUser.Link})**')
	
	PingTimer = OfflineTimer
	
	lastUserInfo = TrackingUser.Raw
	lastFriendsList = TrackingUser.getFriends()
	lastBadgeList = TrackingUser.getBadges(1, 10)
	
	lastPresence = None #TrackingUser.getPresence()
	
	while True:
		TrackingUser.updateInfo()
		
		currentPresence: dict = TrackingUser.getPresence()
		presenceType = currentPresence.get('userPresenceType', 0)
		
		comparePresence(lastPresence, currentPresence)
		
		if presenceType == 0:
			PingTimer = OfflineTimer
		else:
			PingTimer = OnlineTimer
			
			currentUserInfo = TrackingUser.Raw
			currentFriendsList = TrackingUser.getFriends()
			currentBadgeList = TrackingUser.getBadges(1, 10)
			
			compareUserInfo(lastUserInfo, currentUserInfo)
			compareFriends(lastFriendsList, currentFriendsList)
			compareBadges(lastBadgeList, currentBadgeList)
			
			lastUserInfo = currentUserInfo
			lastFriendsList = currentFriendsList
			lastBadgeList = currentBadgeList
		
		lastPresence = currentPresence
		
		sleep(PingTimer)

if __name__ == '__main__':
	main()

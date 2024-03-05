import logging as log
import RoAPI as interface
from info import keywords, ids

users = {}

log.basicConfig(level=log.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Filter Methods

def filter(list, callback):
	filtered = []
	
	for value in list:
		ret = callback(value)
		if ret != None:
			filtered.insert(1, ret)
	
	return filtered

def filterUsers(user: interface.User):
	if user.IsBanned: #ignore banned
		return None
	
	name = user.Name
	display = user.DisplayName
	
	if users.get(name, None): # ignore duplicates
		log.warning(f"Discarding {user} (already found)")
		
		return None
	
	for label, pattern in keywords['username'].items():
		if pattern.search(name) or pattern.search(display):
			user.Keyword = label
			
			users[name] = user
			
			return user
	
	log.warning(f"Didn't pass {user}")
	
	return None

# Main Methods

def searchUser(user: interface.User):
	log.info(f'Searching {user.FullName} {user.Link}')
	
	friends = user.getFriends()
	filtered: list[interface.User] = filter(friends, filterUsers)
	
	for friend in filtered:
		log.info(friend)
	
	return filtered

interface.User.FormatString += " Keyword: {0.Keyword}"

def main():
	if not interface.isAvailable():
		log.error("Roblox api is not available currently.")
		return
	
	count = 0
	
	log.info("Searching base user ids.")
	
	for userid in ids['users']:
		baseUser = interface.User(userid)
		
		count += len(searchUser(baseUser))
	
	log.info(f"Found {count} total suspicious users (excluding duplicates)")
	log.warning("End of file.")

if __name__ == "__main__":
	main()

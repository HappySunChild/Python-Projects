import re as regex
import RoAPI as interface

keywords = {
	'username': {
		'ass': regex.compile(r'[a4][sz]{2}', regex.IGNORECASE),
		'bbc': regex.compile(r'b[bw].?c', regex.IGNORECASE),
		'bio': regex.compile(r'b[i1][o0]', regex.IGNORECASE),
		'bull': regex.compile(r'[b8][uvxznc]{1,3}[1il]{1,2}', regex.IGNORECASE),
		'cow': regex.compile(r'c[o0]w', regex.IGNORECASE),
		'con': regex.compile(r'c[o0]n', regex.IGNORECASE),
		'cum': regex.compile(r'c.?[uzxvn]{1,3}[mn]', regex.IGNORECASE), #imbautublooww,
		'cream': regex.compile(r'cr[e3][e3a4]m', regex.IGNORECASE),
		'clap': regex.compile(r'cl[xa4]pp?[il1]?n?[g]?', regex.IGNORECASE),
		'dump': regex.compile(r'd[uxvz]{1,2}(n|m|v)p', regex.IGNORECASE),
		'snow': regex.compile(r'sn[o0][we3]?', regex.IGNORECASE),
		'usable': regex.compile(r'u[s5][a4]b[il1][e3]', regex.IGNORECASE),
		'femboy': regex.compile(r'f[ex3]?m[x]?[b8][ox0]?[yi1]?', regex.IGNORECASE),
		'inches': regex.compile(r'\d.?[li1]n(ch)?', regex.IGNORECASE),
		'toy': regex.compile(r't[o0][yi]', regex.IGNORECASE),
		'futa': regex.compile(r'f.{1,2}t[a4]', regex.IGNORECASE),
		'slut': regex.compile(r's.?l[uxohi10]?[td2]', regex.IGNORECASE),
		'bunny': regex.compile(r'b[w]?[ux]?nn[eiy1]?', regex.IGNORECASE),
		'hung': regex.compile(r'h[uox0]?ng', regex.IGNORECASE),
		'master': regex.compile(r'm[a4]st[e3]r', regex.IGNORECASE),
		'blacked': regex.compile(r'b[il1][xa4]?ck[e3]d', regex.IGNORECASE),
		'yearold': regex.compile(r'\dy(o|r|ear)', regex.IGNORECASE),
		'spade': regex.compile(r'sp[a4]d[e3]', regex.IGNORECASE),
		'queen': regex.compile(r'q[uw]?[e3]{1,2}[nm]', regex.IGNORECASE),
		'deep': regex.compile(r'd[e3]{1,3}p', regex.IGNORECASE),
		'fill': regex.compile(r'f[iux1][il1]{2,3}', regex.IGNORECASE),
		'pound': regex.compile(r'p[ox0]?u?.?nd?', regex.IGNORECASE), #british pounds right?
		'cuck': regex.compile(r'cu[h]?[xc]?k', regex.IGNORECASE),
		'breed': regex.compile(r'b.?r[e3][e3a]d', regex.IGNORECASE),
		'tits': regex.compile(r't[oixu][h]?t', regex.IGNORECASE),
		'trade': regex.compile(r'tr[a4]d[e3]', regex.IGNORECASE),
		'stretch': regex.compile(r'str[e3]?[t]?ch', regex.IGNORECASE),
		'twink': regex.compile(r'tw[il1][nm]?k', regex.IGNORECASE),
		'minor': regex.compile(r'm[il1]n[eo0]r', regex.IGNORECASE),
		'milk': regex.compile(r'm[il1][il1]k', regex.IGNORECASE),
		'young': regex.compile(r'y[ou]?[u]?ng', regex.IGNORECASE),
		'sex': regex.compile('rs[e3][xck]s?', regex.IGNORECASE),
		'yk': regex.compile(r'yk', regex.IGNORECASE),
		'add': regex.compile(r'[a4]d?d', regex.IGNORECASE), # subtract
		'heat': regex.compile(r'h[e3][a4]t', regex.IGNORECASE),
		'con': regex.compile(r'c[o0]n', regex.IGNORECASE),
		'long': regex.compile(r'l[o0]ng?', regex.IGNORECASE),
		'gut': regex.compile(r'gut', regex.IGNORECASE), # no guts no glory dumbass
		'booty': regex.compile(r'b.?[o0]{2}t[iey]?', regex.IGNORECASE),
		'knot': regex.compile(r'k?n[o0]t', regex.IGNORECASE), # 🤮
		'womb': regex.compile(r'w[ou0]mb', regex.IGNORECASE),
		'maid': regex.compile(r'm[a4][i1]d', regex.IGNORECASE),
		'pie': regex.compile(r'p[i1][e3]', regex.IGNORECASE),
		'wink': regex.compile(r'w[i1]nk', regex.IGNORECASE),
		'deez': regex.compile(r'd[e3]{2}z', regex.IGNORECASE), # deitz nuts
		'old': regex.compile(r'[o0][il1]d', regex.IGNORECASE),
		'mom': regex.compile(r'm[o0]m', regex.IGNORECASE),
		'dad': regex.compile(r'd[a4]d', regex.IGNORECASE),
		'juice': regex.compile(r'ju[il1][cx][e3]', regex.IGNORECASE),
		'ride': regex.compile(r'r[il1]d[e3]?', regex.IGNORECASE),
		'iced': regex.compile(r'[il1]c[e3]d', regex.IGNORECASE),
		'hub': regex.compile(r'hu[b8]', regex.IGNORECASE),
		'alt': regex.compile(r'[a4]lt', regex.IGNORECASE),
		'kitty': regex.compile(r'k[i1]tt?[iey]e?', regex.IGNORECASE),
		'trade': regex.compile(r'tr[a4]d[e3]', regex.IGNORECASE),
		'bust': regex.compile(r'b[hx]{0,2}[ux]st[yie]?e?', regex.IGNORECASE),
		'bang': regex.compile(r'b[ax4]ng', regex.IGNORECASE),
		'backshot': regex.compile(r'b[ax4][ck]{1,2}sh[oux0]{1,2}t'),
		'bitty': regex.compile(r'b[il1]?tt?[iey][se]?s?', regex.IGNORECASE),
		'fav': regex.compile(r'f[xa4]v[e3]?', regex.IGNORECASE),
		'fun': regex.compile(r'f[ux]n', regex.IGNORECASE),
		'slave': regex.compile(r'sl[ax4]v[e3]?', regex.IGNORECASE),
		'love': regex.compile(r'l[xou0]v[e3]?', regex.IGNORECASE),
		'goon': regex.compile(r'g[o0]{2}n', regex.IGNORECASE)
	},
	'group': {}
} # keywords to look for in a names

ids = {
	'users': [
		4660283845, 5247297872, 1385792310, 5458279546,
		5131526601, 5472223218, 5533428973, 5240315500,
		4854665168, 4736287988, 5557673158, 5517971771,
		3543123639, 5363641087, 4793902761, 5412327608,
		5119571152, 5442245171
	],
	'groups': [
		33903172, 4088228, 10376187, 6573130, 16064371,
		3250364
	]
}

if __name__ == "info":
	removeList = []
	
	for userId in ids['users']:
		user = interface.User(userId)
		
		if user.IsBanned:
			print(f'Removing banned user from search list... {user}')
			
			removeList.append(userId)
	
	for userId in removeList:
		ids['users'].remove(userId)
import praw
import time
import sqlite3
import datetime
import pytz

print('BB bot USER CONFIGURATION')#####################SETUP######################################################################################
#USERNAME  = "rbodybuilding"
USERNAME  = "bodybuildingbot"
PASSWORD  = "@@@@@@"
USERAGENT = "Windows:BBposter:V1.3.2 (by /u/protomor)"
SUBREDDIT = "bodybuilding"
refreshtoken = '@@@@@@'

WAIT = 1800

#http://www.timeanddate.com/time/map/
PTIME = "11:00"
DDPTIME = 3

#    https://docs.python.org/2/library/time.html#time.strftime
#Type 0
DDTITLE = "Daily Discussion Thread: %m/%d/%Y"
DDTEXT = """Feel free to post things in the Daily Discussion Thread that don't warrant a subreddit-level discussion. Although most of our posting rules will be relaxed here, you should still consider your audience when posting. Most importantly, show respect to your fellow redditors. General redditiquette always applies.  
"""

#Type 1
MMTITLE = "Mirin' Mondays"
MMTEXT = "It's Monday and time to post your best progress pics, poses, body parts, muscle groups, or whatever. As long as it's worth mirin'. Post a pic and some stats and let the mirin' begin."

#Type 2
TTTITLE = "Training Thursdays"
TTTEXT = "Submit form checks, programs, questions about programs and program success stories (especially if you saw growth from it)."

#Type 3
FMTITLE = "Freestyle/Mandatory Pose Fridays: Vote Now!"
FMTEXT = """
We have shifted Mandatory Pose Monday to Friday to spread out content a little better. The format for these posts has changed a little as well. From here on out, we'll vote from a combination of freestyle and mandatory poses every week, instead of alternating. So you can choose from the mandatory poses or a freestyle pose of your choice and the most highly upvoted pose will be the post for Friday.  

For those who don't know the 8 mandatory poses, they are:  

Front Double Biceps Back Double Biceps Abdominals and Thighs Most Muscular Side Chest Side Triceps Front Lat Spread Rear Lat Spread  
"""
#Type 4
FFTITLE = "Foodie Fridays"
FFTEXT = "Post recipes, nutritional plans, favorite foods, macro schemes or diet questions."

#Type 5
SSTITLE = "Steroid Saturday"
SSTEXT = """Welcome to the steroid Saturday discussion. Please follow the rules, and be kind. If you see any hatred, arguing, etc. Please report the comment so it can be removed. If you do not agree with this post, do not participate. It is that simple.  
RULES:  
*  NO SOURCE TALK. this is very important for a variety of what we hope are obvious reasons.
*  NO FIGHTING. arguing and ridiculing others will only get your comment deleted. Constructive criticism only. Post anything that is on topic. This involves how cycles change close to competition prep, what has worked for you in the past, before/after cycle pictures, dietary changes with different compounds, etc.  
*  Questions are allowed, but should be limited. /r/steroids has a specific thread just for new comers, where you can get amazing answers from some of the most knowledgeable people. Lab talk is alright, but remember how to get a particular lab's product would be prohibited source talk.  
*  We hope everybody enjoys this thread Thanks to the /r/steroids community to help make this work. They have been a huge help and will be chiming in on this post.  
"""

#Type 6
FOFTITLE = "FREAKOUT FRIDAYS (Weekly Rant Thread)"
FOFTEXT = """What makes you want to flip? Tell us today in our weekly Freakout Friday thread!"""

#Type 7
NTTITLE = "Newbie Tuesdays"
NTTEXT = """Ask all newbie BB related questions here."""

WAITS = str(WAIT)

sql = sqlite3.connect('sql.db')
cur = sql.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS posts(ID TEXT, STAMP TEXT, CREATED INT, TYPE INT)')
cur.execute('CREATE TABLE IF NOT EXISTS CurHour(LastHour INT)')
print('Loaded SQL Database')
sql.commit()


print('Logging in')
r = praw.Reddit(USERAGENT)
#r.login(USERNAME, PASSWORD)

r.set_oauth_app_info(client_id='@@@@@@', client_secret='@@@@@@', redirect_uri='http://127.0.0.1:65010/authorize_callback')
r.refresh_access_information(refreshtoken)
print(r.is_oauth_session())

ptime = PTIME.split(':')
ptime = (60*int(ptime[0])) + int(ptime[1])
##########################################END SETUP######################################################################################
def realdailypost(toType):
	subreddit = r.get_subreddit(SUBREDDIT, fetch=True)
	
	cur.execute('SELECT COUNT(*) FROM CurHour')
	sqlTime = cur.fetchone()[0] 

	#if the database is fresh, set the first one to 3am (why not?)
	if sqlTime == 0:
		cur.execute('INSERT INTO CurHour VALUES(3)')
		sql.commit()
		print('CurHour had nothing in it. So we inserted 3am')
		DDPTIME = 60*3
		sqlTime = 3
	else:
		#ddptime is the shifting 23 hour timeline for the daily discussion
		cur.execute('SELECT LastHour FROM CurHour')
		sqlTime = cur.fetchone()[0]
		DDPTIME = 60*sqlTime
		print('ddp time is ' + str(sqlTime))
		
	#I want to ping reddit on every cycle. I've had bots lose their session before
	#now = datetime.datetime.now()
	now = datetime.datetime.now(pytz.timezone('US/Eastern'))
	daystamp = datetime.datetime.strftime(now, "%d%b%Y")
	cur.execute('SELECT ID FROM posts WHERE STAMP=? AND TYPE=?', [daystamp, str(toType)])
	nowtime = (60*now.hour) + now.minute
	
	
	if toType == 0:
		print('\n\nTrying to post Daily Discussion')
			
	#If we haven't done the post yet today, let's post it		
	if not cur.fetchone():
		print('Now: ' + datetime.datetime.strftime(now, "%H:%M"))
		print('Past: ' + str(DDPTIME) + ':00')
		diff = nowtime-DDPTIME
		if diff > 0:
			print('t+ ' + str(abs(diff)) + ' minutes')
			if toType == 0:
				makepost(now, daystamp, DDTEXT, DDTITLE, toType)
				
				#update our projected submission time.
				if sqlTime <= 0:
					sqlTime = 23
					print('ddp time reset to 11pm')
				else:
					sqlTime = sqlTime - 1
					print('ddp time reset to ' + str(sqlTime))
				cur.execute('UPDATE CurHour set LastHour=' + str(sqlTime))
				sql.commit()
		else:
			print('t- ' + str(diff) + ' minutes')
	else:
		print("Already made today's daily post")

#Daily post is now the daily CHECK for a post. The real daily post is the realdailypost function		
def dailypost(toType):
	subreddit = r.get_subreddit(SUBREDDIT, fetch=True)
	#I want to ping reddit on every cycle. I've had bots lose their session before
	now = datetime.datetime.now()
	daystamp = datetime.datetime.strftime(now, "%d%b%Y")
	cur.execute('SELECT ID FROM posts WHERE STAMP=? AND TYPE=?', [daystamp, str(toType)])
	nowtime = (60*now.hour) + now.minute
	
	if toType == 0:
		print('\n\nTrying to post Daily Discussion')
	elif toType == 1:
		print('\n\nTrying to post Mirin Monday')
	elif toType == 2:
		print('\n\nTrying to post Training Tuesday')
	elif toType == 3:
		print('\n\nTrying to post Freestyle/Mandatory pose monday')
	elif toType == 4:
		print('\n\nTrying to post Foodie Friday')
	elif toType == 5:
		print('\n\nTrying to post Steroid Saturday')
	elif toType == 6:
		print('\n\Trying to post Freakout Fridays')
	elif toType == 7:
		print('\n\Trying to post Newbie Tuesdays')
			
	#If we haven't done the post yet today, let's post it		
	if not cur.fetchone():
		print('Now: ' + str(nowtime) + ' ' + datetime.datetime.strftime(now, "%H:%M"))
		print('Past: ' + str(ptime) + ' ' + PTIME)
		diff = nowtime-ptime
		if diff > 0:
			print('t+ ' + str(abs(diff)) + ' minutes')
			if toType == 0:
				makepost(now, daystamp, DDTEXT, DDTITLE, toType)
			elif toType == 1:
				makepost(now, daystamp, MMTEXT, MMTITLE, toType)
			elif toType == 2:
				makepost(now, daystamp, TTTEXT, TTTITLE, toType)
			elif toType == 3:
				makepost(now, daystamp, FMTEXT, FMTITLE, toType)
			elif toType == 4:
				makepost(now, daystamp, FFTEXT, FFTITLE, toType)
			elif toType == 5:
				makepost(now, daystamp, SSTEXT, SSTITLE, toType)
			elif toType == 6:
				makepost(now, daystamp, FOFTEXT, FOFTITLE, toType)
			elif toType == 7:
				makepost(now, daystamp, NTTITLE, NTTEXT, toType)
		else:
			print('t- ' + str(diff) + ' minutes')
	else:
		print("Already made today's post")

def makepost(now, daystamp, toText, toTitle, toType):
	print('Making post...')
	ptitle = datetime.datetime.strftime(now, toTitle)
	ptext = datetime.datetime.strftime(now, toText)

	print('\n' + ptitle)
	print(ptext)
	try:			
		newpost = r.submit(SUBREDDIT, ptitle, text=ptext, captcha=None)
		#newpost.set_contest_mode(True)
		#sort DD by new
		if toType == 0:
			newpost.set_suggested_sort(sort=u'new')
		print('Success: ' + newpost.short_link)
		cur.execute('INSERT INTO posts VALUES(?, ?, ? , ?)', [newpost.id, daystamp, newpost.created_utc, toType])
		#cur.execute('INSERT INTO posts VALUES(?, ?, ? , ?)', ['newpost.id', daystamp, 1, toType])
		sql.commit()
	except Exception as e:
		print('ERROR: PRAW HTTP Error.', e)

print('\n\n\nStarting fresh cycle.\n')
while True:
	DAYOFTHEWEEK = datetime.datetime.today().weekday()
	try:
		#Always do daily post	
		realdailypost(0)
	except Exception as e:
		print("ERROR:", e)

	try:
		#Mirin Monday
		if DAYOFTHEWEEK == 0: #0 is monday
			dailypost(1)
		#Training Tuesdays Moved to Thursdays 11-16-15
		#Newbie Tuesdays
		elif  DAYOFTHEWEEK == 1:
			dailypost(7)
		#Freestyle wednesday thingy killed 11-16-15
		#Freestyle/Mandatory pose friday vote (happens on wednesday)
		#elif  DAYOFTHEWEEK == 2:
		#	dailypost(3)
		#Training Thursdays
		elif  DAYOFTHEWEEK == 3:
			dailypost(2)
		#Foodie Friday and Freakout Friday
		elif  DAYOFTHEWEEK == 4:
			dailypost(4)
			dailypost(6)
		#Steroid Saturday
		elif  DAYOFTHEWEEK == 5:
			dailypost(5)
	except Exception as e:
		print("ERROR:", e)
		
	print('\nSleeping ' + WAITS + ' seconds.\n')
	time.sleep(WAIT)
	r.refresh_access_information(refreshtoken)

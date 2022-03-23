#! /usr/bin/python
# -*- coding: utf-8 -*-
import time, datetime, tweepy, sys, json
from tweepy.cursor import Cursor
from tweepy.models import Status
from tweepy.api import API

## Eventually you'll need to use OAuth. Here's the code for it here.
## You can learn more about OAuth here: https://dev.twitter.com/docs/auth/oauth
## DanielMa
consumer_key = "Il2fTPpc1W8A8oPK3IVx1Q"
consumer_secret = "V7iW1phpMYEumOFmOu8MKEWNqzagBsSV4B1rIrI4UY"
access_token = "2284815920-A3WMqwzz3ShcxdK4jZI6YqHmjlrJ74sUuNfNPRw"
access_token_secret = "DPgNXiGQa4c5J0j5rkzIqJsk5KuBSppFLlh1ccLl2xfh4"

# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, timeout=300) # default timeout=60 seconds

def main( mode = 1 ):
	user_sucess = open('./log/friends-ids-success-1.txt', 'r')
	user_ok = []
	for line in user_sucess:
		if line != '':
			eles = line.strip().split(',')
			if eles[2] == '1':
				user_ok.append(eles[0])
	user_sucess.close()
	print 'already success collect %s users'%len(user_ok)
	
	user_records = open('./users/newyork-user-1.txt', 'r')
	user_ids = []
	for line in user_records:
		if line != '':
			elements = line.strip().split('\t')
			if elements[0] not in user_ok:
				user_ids.append(elements[0])
	user_records.close()
	
	print 'still need to collect %s users...'%len(user_ids)
	success_recorder = open('./log/friends-ids-success-1.txt', 'a')
	for user_id in user_ids:
		print 'collect user:%s'%user_id
		output = open('./newyork-relations/' + user_id, 'w')
		try: 
			friend_count = 0
			friends = []
			count = 0
			# allowed_param = ['id', 'user_id', 'screen_name', 'cursor']
			for ids in Cursor(api.friends_ids, user_id=user_id, count=5000).items():
				count+=1
				friends.append(ids)
			friend_count = 	len(friends)
			print '%s friends-ids have been collected...'%friend_count		
					
			output.write(json.dumps(friends) + '\n')
			output.close()
			success_recorder.write(user_id + ',%s,1\n'%friend_count)
			success_recorder.flush()
			
			time.sleep(60*(friend_count/5001+1))
		except Exception, e:
			success_recorder.write(user_id + ',%s,0\n'%friend_count)
			success_recorder.flush()
			output.close()
			print e
			time.sleep(60) # Rate limit window duration is currently 15 minutes long
			continue		
		print 'done!user_id:%s,friend_count:%s'%(user_id, friend_count)
	success_recorder.close()

if __name__ == '__main__':
    main()

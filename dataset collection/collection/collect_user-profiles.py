#! /usr/bin/python
# -*- coding: utf-8 -*-
import time, datetime, tweepy, sys, json
from tweepy.cursor import Cursor
from tweepy.models import Status
from tweepy.api import API

## Eventually you'll need to use OAuth. Here's the code for it here.
## You can learn more about OAuth here: https://dev.twitter.com/docs/auth/oauth
consumer_key = "Il2fTPpc1W8A8oPK3IVx1Q"
consumer_secret = "V7iW1phpMYEumOFmOu8MKEWNqzagBsSV4B1rIrI4UY"
access_token = "2284815920-A3WMqwzz3ShcxdK4jZI6YqHmjlrJ74sUuNfNPRw"
access_token_secret = "DPgNXiGQa4c5J0j5rkzIqJsk5KuBSppFLlh1ccLl2xfh4"

# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, timeout=300) # default timeout=60 seconds

def main( mode = 1 ):
	user_sucess = open('./log/userprofile-success-1.txt', 'r')
	user_ok = []
	for line in user_sucess:
		if line != '':
			eles = line.strip().split(',')
			if eles[1] == '1':
				user_ok.append(eles[0])
	user_sucess.close()
	print 'already success collect %s users'%len(user_ok)
	
	user_records = open('./users/users-1.txt', 'r')
	user_ids = []
	for line in user_records:
		if line != '':
			elements = line.strip().split('\t')
			if elements[0] not in user_ok:
				user_ids.append(elements[0])
	user_records.close()
	
	print 'still need to collect %s users...'%len(user_ids)
	success_recorder = open('./log/userprofile-success-1.txt', 'a')
	output = open('./users/user_profiles-1.txt', 'a')
	user_count = 0
	ids_for_collect = []
	for user_id in user_ids:
		ids_for_collect.append(user_id)
		user_count+=1
		#output = open('./data/newyork/tweets/' + user_id, 'w')
		try: 
			if user_count%100==0:
				# since_id tweet_id after 11:00 AM 12 Dec 13 (aquired from youtube)
				users = api.lookup_users(user_ids=ids_for_collect)
				for user in users:
					processed_user = process_user(user)
					output.write(json.dumps(processed_user) + '\n')
				output.flush()
				for tmp in ids_for_collect:					
					success_recorder.write(str(tmp) + ',1\n')
				success_recorder.flush()
				ids_for_collect = []
				print '%s user_profile have been collected...'%user_count
				time.sleep(5) # limitation from twitter: only allow 180 request per 15 minutes
		except Exception, e:
			print e
			for tmp in ids_for_collect:					
					success_recorder.write(str(tmp) + ',0\n')
			ids_for_collect = []
			success_recorder.flush()
			output.flush()			
			time.sleep(60) # Rate limit window duration is currently 15 minutes long
			continue
	success_recorder.close()
	output.close()
	
def process_user(user):
	result = user.__getstate__()
	created_at = result['created_at']
	result['created_at'] = created_at.strftime('%Y-%m-%d %H:%M:%S')
	# deal with inside Status Object
	if 'status' in result:
		del result['status']
	if 'entities' in result:
		del result['entities']
	return result
	
if __name__ == '__main__':
    main()

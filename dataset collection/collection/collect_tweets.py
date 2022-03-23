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
api = tweepy.API(auth, timeout=1200) # default timeout=60 seconds

def main( mode = 1 ):
	user_sucess = open('./log/tweets-success-1.txt', 'r')
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
	success_recorder = open('./log/tweets-success-1.txt', 'a')
	for user_id in user_ids:
		kargs = {}
		print 'collect user:%s'%user_id
		output = open('./newyork-tweets/' + user_id, 'w')
		try: 
			tweet_count = 0
			# since_id tweet_id after 7:54 PM - 24 Dec 2013
			for status in Cursor(api.user_timeline, None, user_id=user_id, count=200, include_rts='true', since_id=415450313802674176).items(3200):
				tweet_count += 1
				processed_status = process_status(status)

				output.write(json.dumps(processed_status) + '\n')
				if tweet_count%200 == 0:
					print '%s tweets have been collected...'%tweet_count
					time.sleep(5) # limitation from twitter: only allow 180 request per 15 minutes
			output.flush()
			output.close()
			success_recorder.write(user_id + ',%s,1\n'%tweet_count)
			success_recorder.flush()
		except Exception, e:
			success_recorder.write(user_id + ',%s,0\n'%tweet_count)
			success_recorder.flush()
			output.flush()
			output.close()
			print e
			time.sleep(60) # Rate limit window duration is currently 15 minutes long
			continue		
		print 'done!user_id:%s,tweet_count:%s'%(user_id, tweet_count)
	success_recorder.close()

def process_status(status):
	result = status.__getstate__()
	created_at = result['created_at']
	result['created_at'] = created_at.strftime('%Y-%m-%d %H:%M:%S')
	user = result['author'].__getstate__()
	result['user_id'] = user['id']
	del result['author']
	del result['user']
	# deal with inside Status Object
	if 'retweeted_status' in result:
		result['retweeted_status'] = process_status(result['retweeted_status'])
	if 'place' in result:
		del result['place']
	return result
	
def process_place(place):
	if place is null:
		return null
	result = place.__getstate__()
	if 'bounding_box' in result:
		result['bounding_box'] = result['bounding_box'].__getstate__()
	return result

if __name__ == '__main__':
    main()

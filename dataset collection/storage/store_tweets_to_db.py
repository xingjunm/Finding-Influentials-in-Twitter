#! /usr/bin/python
# -*- coding: utf-8 -*-
# store tweet of separate magnitudes into redis. 

import os,json
import MySQLdb
from datetime import *
import dateutil.parser as dp

def convert_to_tweet(retweet):
	try:
		tweet = []
		## text
		if retweet['text'] is None:
  			tweet.append('null')
  		else:
  			tweet.append(retweet['text'].encode('utf-8'))
  		## source_url
  		if retweet['source_url'] is None:
  			tweet.append('null')
  		else:
  			tweet.append(retweet['source_url'].encode('utf-8'))
  		## id
  		tweet.append(retweet['id'])
  		## favorite_count
  		tweet.append(retweet['favorite_count'])
  		## source
  		if retweet['source'] is None:
  			tweet.append('null')
  		else:
  			tweet.append(retweet['source'].encode('utf-8'))
  		## lang
  		if retweet['lang'] is None:
  			tweet.append('null')
  		else:
  			tweet.append(retweet['lang'].encode('utf-8'))
  		## user_id
  		tweet.append(retweet['user_id'])
  		## created_at
  		if retweet['created_at'] is None:
  			tweet.append('null')
  		else:
  			standard_time = dp.parse(retweet['created_at'])
			tweet.append(standard_time.strftime('%Y-%m-%d %H:%M:%S'))
		## retweeted by the authorized user
		if retweet['retweeted']:
  			tweet.append('1')
  		else:
  			tweet.append('0')
  		 				
  		if retweet['entities'] is None:
  			tweet.append('null') ## symbols 
  			tweet.append('null') ## user_mentions
  			tweet.append('null') ## hashtags
  			tweet.append('null') ## urls
  		else:
  			entities = retweet['entities']
  			## symbols 
  			if entities['symbols'] is None or len(entities['symbols']) == 0:
  				tweet.append('null')
  			else:
  				symbols = ''
  				for symbol in entities['symbols']:
  					symbols = symbols + symbol['text'] + ','
  				symbols = symbols.encode('utf-8')					
  				tweet.append(symbols[0:len(symbols)-1])
  			## user_mentions 
  			if entities['user_mentions'] is None or len(entities['user_mentions']) == 0:
  				tweet.append('null')
  			else:
  				user_mentions = ''
  				for mention in entities['user_mentions']:
  					user_mentions = user_mentions + str(mention['id']) + ','
  				user_mentions = user_mentions.encode('utf-8')  						
  				tweet.append(user_mentions[0:len(user_mentions)-1])
  			## hashtags 
  			if entities['hashtags'] is None or len(entities['hashtags']) == 0:
  				tweet.append('null')
  			else:
  				hashtags = ''
  				for tag in entities['hashtags']:
  					hashtags = hashtags + tag['text'] + ','
  				hashtags = hashtags.encode('utf-8')  						
  				tweet.append(hashtags[0:len(hashtags)-1])
  			## urls 
  			if entities['urls'] is None or len(entities['urls']) == 0:
  				tweet.append('null')
  			else:
  				urls = ''
  				for url in entities['urls']:
  					urls = urls + url['url'] + ','
  				urls = urls.encode('utf-8')  						
  				tweet.append(urls[0:len(urls)-1])
  		## in_reply_to_status_id_str varchar(128)
  		if retweet['in_reply_to_status_id_str'] is None:
  			tweet.append('null')
  		else:
  			tweet.append(retweet['in_reply_to_status_id_str'].encode('utf-8'))
  		## retweet_count,
  		tweet.append(retweet['retweet_count'])
  		## in_reply_to_user_id varchar(128),
  		if retweet['in_reply_to_user_id'] is None:
  			tweet.append('null')
  		else:
  			tweet.append(retweet['in_reply_to_user_id'])
		return tweet
		#print tweet
		#break
	except Exception, e:
	        print 'exception:user %s'%user_id
	        print retweet
	        return None
	        
# create database connection
try:
	conn=MySQLdb.connect(host='localhost',user='root',passwd='root',db='twitter',port=3306)
	cur=conn.cursor()
except MySQLdb.Error,e:
     	print "Mysql Error %d: %s" % (e.args[0], e.args[1])

fo = open('../log/store-tweets-success.txt','r')
users_done = []
for line in fo:
	tmp_line = line.strip()
	if tmp_line != '':
		users_done.append(tmp_line)
fo.close()

fi = open('../log/store-tweets-success.txt','a')
count = 0
file_list = os.listdir('../tweets/')
for tweet_file in file_list:
	f = open('../tweets/' + tweet_file, 'r')
	user_id = tweet_file
	# check if done already
	if user_id in users_done:
		continue		
	tweets=[]
	retweets=[]
	total_count = [[0 for i in range(24)] for j in range(7)]
	retweet_count = [[0 for i in range(24)] for j in range(7)]
	reply_count = [[0 for i in range(24)] for j in range(7)]
	for line in f:
		tmp = line.strip()
		if tmp == '':
			print 'The end of tweets file...'
		else:
			try:
				tmp = json.loads(tmp)
				tweet = []
				## text
				if tmp['text'] is None:
  					tweet.append('null')
  				else:
  					tweet.append(tmp['text'].encode('utf-8'))
  				## source_url
  				if tmp['source_url'] is None:
  					tweet.append('null')
  				else:
  					tweet.append(tmp['source_url'].encode('utf-8'))
  				## id
  				tweet.append(tmp['id'])
  				## favorite_count
  				tweet.append(tmp['favorite_count'])
  				## source
  				if tmp['source'] is None:
  					tweet.append('null')
  				else:
  					tweet.append(tmp['source'].encode('utf-8'))
  				## lang
  				if tmp['lang'] is None:
  					tweet.append('null')
  				else:
  					tweet.append(tmp['lang'].encode('utf-8'))
  				## user_id
  				tweet.append(tmp['user_id'])
  				## retweeted_status
  				if 'retweeted_status' in tmp:
  					retweet = convert_to_tweet(tmp['retweeted_status'])
  					if retweet:
  						retweets.append(retweet)
  					tweet.append(tmp['retweeted_status']['id'])
  				else:
  					tweet.append('null')
  				## created_at
  				if tmp['created_at'] is None:
  					tweet.append('null')
  				else:
  					standard_time = dp.parse(tmp['created_at'])
					tweet.append(standard_time.strftime('%Y-%m-%d %H:%M:%S'))
					# count the number of tweets by hour and week day
					week_day = standard_time.weekday() #Monday is 0 and Sunday is 6
					hour = standard_time.hour # 0: [00:00 - 1:00] 1: [1:00 -- 2:00]
					total_count[week_day][hour] = total_count[week_day][hour] + 1
					if 'retweeted_status' in tmp:
						retweet_count[week_day][hour] = retweet_count[week_day][hour] + 1
					if tmp['in_reply_to_status_id_str'] is not None:
						reply_count[week_day][hour] = reply_count[week_day][hour] + 1
				## retweeted by the authorized user
				if tmp['retweeted']:
  					tweet.append('1')
  				else:
  					tweet.append('0')
  				 				
  				if tmp['entities'] is None:
  					tweet.append('null') ## symbols 
  					tweet.append('null') ## user_mentions
  					tweet.append('null') ## hashtags
  					tweet.append('null') ## urls
  				else:
  					entities = tmp['entities']
  					## symbols 
  					if entities['symbols'] is None or len(entities['symbols']) == 0:
  						tweet.append('null')
  					else:
  						symbols = ''
  						for symbol in entities['symbols']:
  							symbols = symbols + symbol['text'] + ','
  						symbols = symbols.encode('utf-8')					
  						tweet.append(symbols[0:len(symbols)-1])
  					## user_mentions 
  					if entities['user_mentions'] is None or len(entities['user_mentions']) == 0:
  						tweet.append('null')
  					else:
  						user_mentions = ''
  						for mention in entities['user_mentions']:
  							user_mentions = user_mentions + str(mention['id']) + ','
  						user_mentions = user_mentions.encode('utf-8')  						
  						tweet.append(user_mentions[0:len(user_mentions)-1])
  					## hashtags 
  					if entities['hashtags'] is None or len(entities['hashtags']) == 0:
  						tweet.append('null')
  					else:
  						hashtags = ''
  						for tag in entities['hashtags']:
  							hashtags = hashtags + tag['text'] + ','
  						hashtags = hashtags.encode('utf-8')  						
  						tweet.append(hashtags[0:len(hashtags)-1])
  					## urls 
  					if entities['urls'] is None or len(entities['urls']) == 0:
  						tweet.append('null')
  					else:
  						urls = ''
  						for url in entities['urls']:
  							urls = urls + url['url'] + ','
  						urls = urls.encode('utf-8')					
  						tweet.append(urls[0:len(urls)-1])
  				## in_reply_to_status_id_str varchar(128)
  				if tmp['in_reply_to_status_id_str'] is None:
  					tweet.append('null')
  				else:
  					tweet.append(tmp['in_reply_to_status_id_str'].encode('utf-8'))
  				## retweet_count,
  				tweet.append(tmp['retweet_count'])
  				## in_reply_to_user_id varchar(128),
  				if tmp['in_reply_to_user_id'] is None:
  					tweet.append('null')
  				else:
  					tweet.append(tmp['in_reply_to_user_id'])
  				tweets.append(tweet)
				#print tweets
				#print retweets
				#break
				# print len(profile)
			except Exception, e:
					print e
			   		print 'exception:user %s'%user_id
			   		print tmp
			   		continue
	count = count + 1
	if count%50==0:
		print 'handle %s users\' tweets.'%count
	
	## insert the tweet count info into mysql db
	tweet_counts = []
	for i in range(7):
		for j in range(24):
			tmp_count = [0 for k in range(6)]
			tmp_count[0] = user_id
			tmp_count[1] = i
			tmp_count[2] = j
			tmp_count[3] = total_count[i][j] # total number/4 weeks (we collect four weeks tweets)
			tmp_count[4] = retweet_count[i][j] # retweet number
			tmp_count[5] = reply_count[i][j] # reply number
			tweet_counts.append(tmp_count)
	total_count = []
	retweet_count = []
	reply_count = []
	#print tweet_counts
	#break
	try:
		cur.executemany('insert ignore into twitter_tweets values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',tweets)
		cur.executemany('insert ignore into twitter_retweets values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',retweets)
		#cur.executemany('insert ignore into tweet_count values(%s,%s,%s,%s,%s,%s)', tweet_counts)
		conn.commit()
		fi.write(user_id + '\n')
		fi.flush()
		tweets = []
		retweets = []
		tweet_counts = []
	except MySQLdb.Error,e:
		print "Mysql Error %d: %s" % (e.args[0], e.args[1])
     	
	f.close()
	
fi.close()
try:
    cur.close()
    conn.close()
except MySQLdb.Error,e:
     print "Mysql Error %d: %s" % (e.args[0], e.args[1])

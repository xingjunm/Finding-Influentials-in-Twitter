#! /usr/bin/python
# -*- coding: utf-8 -*-

import os
import MySQLdb

# get all of the users' information
def collect_userInfo():	
	r_file = open('links.dat','r')
	valid_users = set()
	for line in r_file:
		if line.strip() == '':
			continue
		items = line.split()
		valid_users.add(items[0])
		valid_users.add(items[1])
	r_file.close()
	
	conn=MySQLdb.connect(host='localhost',user='root',passwd='root',db='twitter',port=3306)
	cur=conn.cursor()
	cur.execute('select id, followers_count, friends_count, listed_count, favourites_count, statuses_count from twitter_user order by id')
	count=0
	file = open('user_info.dat', 'w')
	while True:
		row = cur.fetchone()
		if row == None:
			break
		if row[0] not in valid_users:
			continue
		ratio = float(row[1])/float(row[2])
		file.write(row[0] + '\t' + str(row[1]) + '\t' + str(row[2]) + '\t' + str('%.4f'%ratio) + '\t' + str(row[3]) + '\t' + str(row[4])  + '\t' + str(row[5]) + '\n')
		count+=1
		if count%1000 == 0:
			print 'load %s users info.'%count
	file.close()
	cur.close()
	conn.commit ()
	conn.close ()
	print 'done: %s user infos ...'%count

# get all of the users' timeSeries
def collect_timeSeries():	
	r_file = open('user_info.dat','r')
	valid_users = set()
	for line in r_file:
		if line.strip() == '':
			continue
		items = line.split()
		valid_users.add(items[0])
	r_file.close()
	
	conn=MySQLdb.connect(host='localhost',user='root',passwd='root',db='twitter',port=3306)
	cur=conn.cursor()
	cur.execute('select user_id, hour, total_count from tweet_count_hour_normalized')
	count=0
	timeSeries = {}
	
	while True:
		row = cur.fetchone()
		if row == None:
			break
		user_id = row[0]
		if user_id not in valid_users:
			continue
		if user_id not in timeSeries:
			series = [0 for i in range(24)]
			timeSeries[user_id] = series
		timeSeries[user_id][int(row[1])] = float(row[2])
		count+=1
		if count%10000 == 0:
			print 'load %s users time series.'%count
	cur.close()
	conn.commit ()
	conn.close ()
	
	file = open('timeSeries.dat', 'w')
	for key, series in timeSeries.items():
		str_out = key
		for i in range(24):
			str_out += '\t' + str('%.4f'%series[i])
		file.write(str_out + '\n')
	file.close()
	
	print 'done: %s time series ...'%count
	
# get retweets needed to train
def collect_retweets():
	file = open('retweets.dat', 'w')
	conn=MySQLdb.connect(host='localhost',user='root',passwd='root',db='twitter',port=3306)
	cur=conn.cursor()
	cur.execute('select user_id, friend_id, tweet_id, retweet_id, hour(tweet_time) as tweet_hour, hour(retweet_time) as retweet_hour from count_retweet_delay_valid')
	count=0
	while True:
		row = cur.fetchone()
		if row == None:
			break
		file.write(row[0] + '\t' + row[1] + '\t' + row[2] + '\t' + row[3] + '\t' + str(row[4])  + '\t' + str(row[5]) + '\n')
		count+=1
		if count%10000 == 0:
			print 'load %s retweets.'%count
	file.close()
	cur.close()
	conn.commit ()
	conn.close ()
	print 'done: %s retweet between users ...'%count

# get tweets of the on-going checking users
def collect_tweets():
	file = open('user_tweets.dat','w')
	conn=MySQLdb.connect(host='localhost',user='root',passwd='root',db='twitter',port=3306)
	cur=conn.cursor()
	
	# load user ids
	cur.execute('select friend_id, retweet_id  from count_retweet_delay_valid union select friend_id, reply_id  from count_reply_delay_valid')
	count=0
	valid_users = set()
	valid_tweets = set()
	while True:
		row = cur.fetchone()
		if row == None:
			break
		valid_users.add(row[0])
		valid_tweets.add(row[1])
		count+=1
		if count%100 == 0:
			print 'load %s users and retweets.'%count
	
	# check tweets
	cur.execute('select user_id, id, hour(created_at) as tweet_hour from twitter_tweets order by user_id')
	count=0
	while True:
		row = cur.fetchone()
		if row == None:
			break
		if row[0] in valid_users and row[1] in valid_tweets:
			file.write(row[0] + '\t' + row[1] + '\t' + str(row[2]) + '\n')
			count+=1
			if count%10000 == 0:
				print 'load %s tweets.'%count
				
	file.close()
	cur.close()
	conn.commit ()
	conn.close ()
	print 'done: %s tweets ...'%count	
	
# get links between users
# links.dat: friend_id	user_id
def collect_links():
	conn=MySQLdb.connect(host='localhost',user='root',passwd='root',db='twitter',port=3306)
	cur=conn.cursor()
	cur.execute('select distinct(friend_id) as id from count_retweet_delay_valid union select distinct(friend_id) as id from count_reply_delay_valid')
	count=0
	valid_users = []
	while True:
		row = cur.fetchone()
		if row == None:
			break
		valid_users.append(row[0])
		count+=1
		if count%1000 == 0:
			print 'load %s users.'%count			
	cur.close()
	conn.commit ()
	conn.close ()
	
	count = 0
	file = open('links.dat','w')
	edges = open('edges.dat', 'r')
	for edge in edges:
		ids = edge.split()
		if ids[0] in valid_users:
			file.write(edge)
			count+=1
			if count%100000 == 0:
				print 'load %s links.'%count
	file.close()
	edges.close()	
	print 'done: %s links ...'%count

# compute two array's cosine distance
def cosine_distance(a, b):
    if len(a) != len(b):
    	raise ValueError, "a and b must be same length" #Steve
    numerator = 0
    denoma = 0
    denomb = 0
    for i in range(len(a)):       #Mike's optimizations:
    	ai = float(a[i])             #only calculate once
    	bi = float(b[i])
    	numerator += ai*bi    #faster than exponent (barely)
    	denoma += ai*ai       #strip abs() since it's squaring
    	denomb += bi*bi
    result = 1 - numerator / (sqrt(denoma)*sqrt(denomb))
    return str('%.4f'%result)

# get i-j-ratio.dat
def collect_ratio():
	file = open('i-j-ratio.dat','w')
	conn=MySQLdb.connect(host='localhost',user='root',passwd='root',db='twitter',port=3306)
	cur=conn.cursor()
	cur.execute('select A.user_id, A.friend_id, B.avg_total/C.total_count as ratio from user_friend A, user_habit B, friends_tweet_num C where A.user_id = C.user_id and A.friend_id = B.user_id')
	count=0
	while True:
		row = cur.fetchone()
		if row == None:
			break
		file.write(row[1] + '\t' + row[0] + '\t' + str('%.4f'%row[2]) + '\n')
		count+=1
	file.close()
	cur.close()
	conn.commit ()
	conn.close ()
	print 'done: %s ratios between relations ...'%count

# compute topic similarity of two users
def collect_sim():
	#load user_id list
	user_ids = os.listdir('../LDA/processed-texts')
	#print user_ids
	#load edges
	edges = []
	file = open('./links.dat','r')
	for line in file:
		if line == '':
			continue
		edges.append(line.split())
	file.close()
	
	# load doc-topic distribution row normalize
	doc_topic = []
	file = open('./doc-topic_rownorm.txt', 'rb')
	for line in file:
		doc_topic.append(line.split())
	file.close()
	
	# compute the sim: sim = 1 - |DTi - DTj|
	# and teleportation probability
	file_sim = open('./sim.dat', 'w')
	file_cossim = open('./cosine-sim.dat', 'w')
	for edge in edges:
		#print edge
		if len(edge) != 2:
			print 'edge is not 2!'
			print edge
			continue
		user_i = edge[0]
		user_j = edge[1]
		
		result = user_i + '_' + user_j # the first column of the result
		cos_result = user_i + '_' + user_j # the first column of the cosine result
		#print result
		index_i = user_ids.index(user_i) # user index in doc-topic distribution
		index_j = user_ids.index(user_j)
		
		row_i = doc_topic[index_i]
		row_j = doc_topic[index_j]
		
		if len(row_i) != 50 or len(row_j) != 50:
			print 'length not 50!'
			print row_i
			print row_j
			continue
		cos_sim = cosine_distance(row_i,row_j)
		cos_result += '\t' + str(cos_sim) + '\n'
		file_cossim.write(cos_result)
		for i in range(50): 
			sim = 1.0 - abs(float(row_i[i]) - float(row_j[i]))
			result += '\t' + str('%.4f'%sim) + '\n'
		file_sim.write(result)
	file_cossim.close()
	file_sim.close()

# Define i-j-cosine.dat time distances
def collect_cosine():
	conn=MySQLdb.connect(host='localhost',user='root',passwd='root',db='twitter',port=3306)
	cur=conn.cursor()
	
	links = []
	cur.execute('select user_id, friend_id from user_friend order by friend_id')
	count=0
	while True:
		row = cur.fetchone()
		if row == None:
			break
		tmp = []
		tmp.append(row[1])
		tmp.append(row[0])
		links.append(tmp)
		count+=1
	print 'load %s relations.'%count

	timeSeries = {}
	cur.execute('select user_id, hour, total_count from tweet_count_hour_normalized order by user_id')
	count = 0
	while True:
		row = cur.fetchone()
		if row == None:
			break
		user_id = row[0]
		if user_id not in timeSeries:
			mm = [0 for i in range(24)]
			timeSeries[user_id] = mm
		timeSeries[user_id][int(row[1])]=float(row[2])
		count+=1
	print 'load %s time series.'%count
	cur.close()
	conn.commit()
	conn.close()
	
	file = open('i-j-cosine.dat','w')
	count = 0
	for link in links:
		user_i = link[0]
		user_j = link[1]
		
		time_i = timeSeries[user_i]
		time_j = timeSeries[user_j]
		cos = cosine_distance(time_i, time_j)
 
		file.write(user_i + '\t' + user_j + '\t' + str(cos) + '\n')
			
		count+=1
		if count%100000 == 0:
			print 'compute %s cosine distances.'%count
			
	file.close()
	print 'done collect_cosine() ...'

if __name__ == '__main__':
	# execute methods according to the following orders
	#collect_retweets()
	collect_links()
	#collect_tweets()	
	collect_userInfo()
	collect_timeSeries()
	#collect_ratio() # when links are changed, needs to regenerate friends_tweet_num
	#collect_cosine() # when links are changed, needs to rerun the code
	collect_sim() # when links are changed, needs to rerun the code
	print 'all done!'

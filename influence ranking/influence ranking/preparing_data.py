#! /usr/bin/python
# -*- coding: utf-8 -*-

import os, math, csv
import MySQLdb
from math import sqrt
import numpy as np

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

# get nodes of the digraph
def collect_nodes():
	file = open('nodes.dat','w')
	conn=MySQLdb.connect(host='localhost',user='root',passwd='root',db='twitter',port=3306)
	cur=conn.cursor()
	cur.execute('select distinct(id) as id from twitter_user order by id')
	count=0
	while True:
		row = cur.fetchone()
		if row == None:
			break
		file.write(row[0] + '\n')
		count+=1
	file.close()
	cur.close()
	conn.commit ()
	conn.close ()
	print 'done: %s nodes ...'%count	
	
# get edges of the digraph
def collect_edges():
	file = open('edges.dat','w')
	conn=MySQLdb.connect(host='localhost',user='root',passwd='root',db='twitter',port=3306)
	cur=conn.cursor()
	cur.execute('select user_id, friend_id from user_friend order by friend_id')
	count=0
	while True:
		row = cur.fetchone()
		if row == None:
			break
		file.write(row[1] + '\t' + row[0] + '\n')
		count+=1
	file.close()
	cur.close()
	conn.commit ()
	conn.close ()
	print 'done: %s edges ...'%count

# compute topic similarity of two users
def collect_sim():
	#load user_id list
	user_ids = os.listdir('../LDA/processed-texts')
	#print user_ids
	#load edges
	edges = []
	file = open('./edges.dat','r')
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
	file_sim = open('./sim-100.dat', 'w')
	file_cossim = open('./cosine-sim-100.dat', 'w')
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

# this method is for page rank algorithm
def collect_tele():
	#load user_id list
	user_ids = os.listdir('../LDA/processed-texts')

	# load doc-topic distribution row normalize
	doc_topic = []
	file = open('./doc-topic_columnnorm.txt', 'rb')
	for line in file:
		doc_topic.append(line.split())
	file.close()
	
	file_tele = open('./jump-100.dat', 'w')
	for i in range(len(user_ids)):
		user_id = user_ids[i]
		
		result = user_id
		
		row = doc_topic[i]
		
		for j in range(50):
			tele = float(row[j])
			result += '\t' + str('%.4f'%tele)
		file_tele.write(result + '\n')
	file_tele.close()
	
def collect_topicweight():
	# load topic-word distribution
	topic_word = []
	csvfile = open('topic-word-100.csv', 'rb')
	reader = csv.reader(csvfile)
	for row in reader:
		tmp = []
		for i in range(len(row)):
			tmp.append(float(row[i]))
		topic_word.append(tmp)
	csvfile.close()
	dist = np.matrix(topic_word)
	row_sum = dist.sum(axis=1)
	np.savetxt('topicweight-100.txt', row_sum/row_sum.sum(axis=0)) # normalized topic weight refering to the count of words assigned to the topic

def test():
	file = open('./i-j-cosine.dat','r')
	for line in file:
		items = line.split()
		if items[0] == '14724533' and items[1] == '684983':
			print line
		if items[1] == '14724533' and items[0] == '684983':
			print line 
	file.close()

if __name__ == '__main__':
	#collect_nodes()
	#collect_edges()
	#collect_ratio() # 当edges改变时需要先重新生成friends_tweet_num，然后再重新执行
	#collect_cosine() # 当edges改变时需要重新执行
	collect_sim()	# 当edges改变时需要重新执行
	collect_tele()	# 当edges改变时需要重新执行
	#collect_topicweight() # 
	#test()
	print 'all done!'

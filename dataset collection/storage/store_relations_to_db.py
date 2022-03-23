#! /usr/bin/python
# -*- coding: utf-8 -*-
# store valid user-relation into txt file and mysql database:table: user_friend.
import os
import MySQLdb

# create database connection
try:
	conn=MySQLdb.connect(host='localhost',user='root',passwd='root',db='twitter',port=3306)
	cur=conn.cursor()
except MySQLdb.Error,e:
     	print "Mysql Error %d: %s" % (e.args[0], e.args[1])

# load valid user list
user_collected = open('../users/users.txt', 'r')
user_ok = []
for line in user_collected:
	if line != '':
		tmp = line.strip().split('\t')
		user_ok.append(tmp[0])
user_collected.close()
print '%s collected users'%len(user_ok)

file_list = os.listdir('../relations/')
count = 0
fw = open('./user_relation.txt', 'w')
for tweet_file in file_list:
	f = open('../relations/' + tweet_file, 'r')
	user_id = tweet_file
	friends = []
	for line in f:
		tmp = line.strip()
		if tmp == '':
			print 'The end of tweets file...'
		else:			
			tmp = tmp.replace(' ','')
			tmp = tmp.replace('[','')
			tmp = tmp.replace(']','')
			friends = tmp.split(',')
	count+=1	
	## insert the tweet count info into mysql db
	user_Friends = []
	for friend_id in friends:
		if friend_id in user_ok:
			tmp_relation = [0 for k in range(3)]
			tmp_relation[0] = user_id
			tmp_relation[1] = friend_id
			tmp_relation[2] = '1'
			user_Friends.append(tmp_relation)
			print '%s	%s'%(user_id,friend_id)
			fw.write(user_id + '\t' + friend_id + '\n')
	fw.flush()
	try:
		cur.executemany('insert ignore into user_friend values(%s,%s,%s)', user_Friends)
		conn.commit()
	except MySQLdb.Error,e:
		print "Mysql Error %d: %s" % (e.args[0], e.args[1])
	f.close()
fw.close()
try:
    cur.close()
    conn.close()
except MySQLdb.Error,e:
     print "Mysql Error %d: %s" % (e.args[0], e.args[1])
		

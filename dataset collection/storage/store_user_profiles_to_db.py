#! /usr/bin/python
# -*- coding: utf-8 -*-
# store user_profile of separate magnitudes into redis. 

import os,json
import MySQLdb
from datetime import *
import dateutil.parser as dp

# files for reading and writing

profile_file = open('../users/user_profiles-5.txt', 'r')

# create database connection
try:
	conn=MySQLdb.connect(host='localhost',user='root',passwd='root',db='twitter',port=3306)
	cur=conn.cursor()
except MySQLdb.Error,e:
     	print "Mysql Error %d: %s" % (e.args[0], e.args[1])

user_profiles=[]
count = 0
for line in profile_file:
	tmp = line.strip()
	if tmp == '':
		print 'The end of user profile'
	else:
		try:
			tmp_profile = json.loads(tmp)
			user_profile = []
  			user_profile.append(tmp_profile['id'])
  			user_profile.append(tmp_profile['followers_count'])
  			user_profile.append(tmp_profile['listed_count'])
  			if tmp_profile['utc_offset'] is None:
  				user_profile.append('null')
  			else:
  				user_profile.append(tmp_profile['utc_offset'])
  			user_profile.append(tmp_profile['statuses_count'])
  			if tmp_profile['description'] is None:
  				user_profile.append('null')
  			else:
  				user_profile.append(tmp_profile['description'].encode('utf-8'))
  			user_profile.append(tmp_profile['friends_count'])
  			if tmp_profile['location'] is None:
  				user_profile.append('null')
  			else:
  				user_profile.append(tmp_profile['location'].encode('utf-8'))
  			if tmp_profile['geo_enabled']:
  				user_profile.append('1')
  			else:
  				user_profile.append('0')
  			if tmp_profile['name'] is None:
  				user_profile.append('null')
  			else:
  				user_profile.append(tmp_profile['name'].encode('utf-8'))
  			if tmp_profile['lang'] is None:
  				user_profile.append('null')
  			else:
  				user_profile.append(tmp_profile['lang'].encode('utf-8'))
  			user_profile.append(tmp_profile['favourites_count'])
  			if tmp_profile['screen_name'] is None:
  				user_profile.append('null')
  			else:
  				user_profile.append(tmp_profile['screen_name'].encode('utf-8'))
  			if tmp_profile['created_at'] is None:
  				user_profile.append('null')
  			else:
  				standard_time = dp.parse(tmp_profile['created_at'])
				user_profile.append(standard_time.strftime('%Y-%m-%d %H:%M:%S'))
			if tmp_profile['time_zone'] is None:
  				user_profile.append('null')
  			else:
  				user_profile.append(tmp_profile['time_zone'])
  			if tmp_profile['protected']:
  				user_profile.append('1')
  			else:
  				user_profile.append('0')
  			
			user_profiles.append(user_profile)
			# print user_profiles
			# break
			count = count + 1
			# print len(profile)
		except IndexError, e:
	        	print line
		        continue
	if count%1000==0:
		print 'handle %s users.'%count
		try:
			cur.executemany('insert into twitter_user values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',user_profiles)
			conn.commit()
			user_profiles = []
			print 'done! list_size=%s'%len(user_profiles)
		except MySQLdb.Error,e:
     			print "Mysql Error %d: %s" % (e.args[0], e.args[1])

print 'last! list_size=%s'%len(user_profiles)

if len(user_profiles) > 0:
	try:
		cur.executemany('insert into twitter_user values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',user_profiles)
		conn.commit()
		count = 0
		user_profiles = []
		print 'done! list_size=%s'%len(user_profiles)
	except MySQLdb.Error,e:
     			print "Mysql Error %d: %s" % (e.args[0], e.args[1])
profile_file.close()
try:
    cur.close()
    conn.close()
except MySQLdb.Error,e:
     print "Mysql Error %d: %s" % (e.args[0], e.args[1])
		

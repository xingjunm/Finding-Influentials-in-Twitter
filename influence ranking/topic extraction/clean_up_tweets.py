#! /usr/bin/python
# -*- coding: utf-8 -*-
# clear users' tweet files according to user-ids from table twitter_user. 

import os
import MySQLdb

def getValidUserList():
	print 'start ... get valid user list'
	users = []
	conn=MySQLdb.connect(host='localhost',user='root',passwd='root',db='twitter',port=3306)
	cur=conn.cursor()
	cur.execute('select distinct id from twitter_user')
	while True:
		row = cur.fetchone()
		if row == None:
			break
		users.append(row[0])
	cur.close()
	conn.commit ()
	conn.close ()
	print 'done!	users.size:%d'%len(users)
	return users
	
def clear_file(file_path):
	print 'start ... clear_file'
	valid_users = getValidUserList()
	file_list = os.listdir(file_path)	
	for tweet_file in file_list:
		if tweet_file not in valid_users:
			os.remove(file_path+ '/' + tweet_file)	
	file_list = os.listdir(file_path)
	print ' %s tweets files left'%len(file_list)
	
if __name__ == '__main__':
	tweet_path = '../tweets'
	clear_file(tweet_path)

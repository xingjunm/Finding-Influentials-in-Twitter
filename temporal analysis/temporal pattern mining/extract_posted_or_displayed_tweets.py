#! /usr/bin/python
# -*- coding: utf-8 -*-
# extract the time information of those tweets display in one's homeline or 
# displayline(he can see all of his friends tweets).
import os
import MySQLdb


def homeline():
	conn=MySQLdb.connect(host='localhost',user='root',passwd='root',db='twitter',port=3306)
	cur=conn.cursor()
	cur.execute('select user_id,created_at from user_tweet_time order by user_id')
	count=0
	user_id='test.txt'
	w_file = open('./home_line/' + user_id,'a')
	while True:
		row = cur.fetchone()
		if row == None:
			print 'done!'
			break
		if user_id != row[0]:
			user_id = row[0]
			w_file.close()
			w_file = open('./home_line/' + user_id,'a')
		w_file.write(str(row[1]) + ',')
		count+=1
		if count%10000==0:
			print 'handle %s users\' homeline...'%count
	
	w_file.close()
	cur.close()
	conn.commit ()
	conn.close ()
	
def displayline():
	file_valid = os.listdir('./home_line')
	relations = open('./user-relation.txt','r') # user-realtion.txt 是数据采集部分的‘存储关系数据到文件.py’生成的，目的是减少查询数据库带来的延迟以提高效率
	count=0
	user_id = 'test.txt'
	w_file = open('./display_line/' + user_id,'a')
	for relation in relations:
		infos = relation.strip().split() # 格式：user_id friend_id
		if infos[0] != user_id:
			user_id=infos[0]
			w_file.close()
			w_file = open('./display_line/' + user_id,'a')
		if infos[1] in file_valid:			
			a_file = open('./home_line/' + infos[1],'r')
			w_file.write(a_file.read())
			a_file.close()
			count+=1
		if count%100==0:
			print 'handle %s users\' displaylines...'%count
	w_file.close()
	relations.close()
	print 'done!'
	
def main(mode = 1):
	#homeline()
	displayline()
	
if __name__ == '__main__':
    main()

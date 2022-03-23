#! /usr/bin/python
# -*- coding: utf-8 -*-
# count reweet interval.
import os
import MySQLdb

def count_retweet_delay():
	conn=MySQLdb.connect(host='localhost',user='root',passwd='root',db='twitter',port=3306)
	cur=conn.cursor()
	cur.execute('select user_id,friend_id,tweet_id,retweet_id,unix_timestamp(tweet_time) as tweet_time, unix_timestamp(retweet_time) as retweet_time from count_retweet_delay order by user_id')
	count=0
	sorted_time_list = []
	user_id='test.txt'
	w_file = open('./count_retweet_lookback.txt','w')
	r_file = open('./display_line/' + user_id,'r')
	while True:
		row = cur.fetchone()
		#print row
		if row == None:
			print 'done!'
			break
		if user_id != row[0]:
			sorted_time_list = [] # carefully clear old user's records for the new one!
			user_id = row[0]
			r_file.close()
			if os.path.exists('./display_line/' + user_id):
				r_file = open('./display_line/' + user_id,'r')
				content = r_file.read().strip().strip(',')
				time_list = content.split(',')
				for i in range(len(time_list)):
					if time_list[i] == '':
						continue
					sorted_time_list.append(int(time_list[i]))
				sorted_time_list.sort()
			else: # means this file does not exist
				sorted_time_list = []
			#print sorted_time_list
		start = int(row[5]) # retweet_time
		end = int(row[4]) # tweet_time
		tweet_count = 0
		num = len(sorted_time_list)
		for i in range(num):
			if sorted_time_list[i]>start:
				while i < num and sorted_time_list[i]<end:				
					tweet_count+=1
					i+=1
				break
		w_file.write(row[0] + ',' + row[1] + ',' + row[2] + ',' + row[3] + ',' + str(tweet_count) + '\n')
		count+=1
		if count%100==0:
			print 'handle %s retweets'%count
		
	w_file.close()
	cur.close()
	conn.close ()
	
def store_into_db():
	r_file = open('./count_retweet_lookback.txt', 'r')
	conn=MySQLdb.connect(host='localhost',user='root',passwd='root',db='twitter',port=3306)
	cur=conn.cursor()
	count=0
	update_list = []
	for line in r_file:
		count+=1
		#if count<=0:
			#continue
		row = line.strip().split(',')
		tmp = []
		tmp.append(str(row[4]))
		tmp.append(row[0])
		tmp.append(row[1])
		tmp.append(row[2])
		tmp.append(row[3])
		update_list.append(tmp)
		
		if count%1000 == 0:
			print 'update %s retweet lookback...'%count
			cur.executemany('UPDATE count_retweet_delay SET tweet_count=%s WHERE user_id=%s AND friend_id=%s AND tweet_id=%s AND retweet_id=%s',update_list)
			update_list = []
			print 'done!'
	
	cur.executemany('UPDATE count_retweet_delay SET tweet_count=%s WHERE user_id=%s AND friend_id=%s AND tweet_id=%s AND retweet_id=%s', update_list)
	update_list = []
	cur.close()
	conn.commit ()
	conn.close ()
	
def main(mode = 1):
	#count_retweet_delay()	
	store_into_db()
	
if __name__ == '__main__':
    main()

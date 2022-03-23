#! /usr/bin/python
# -*- coding: utf-8 -*-
# count reweet interval.
import os
import MySQLdb

def getDistribution():
	print 'start ... get distributions'
	dist = {}
	conn=MySQLdb.connect(host='localhost',user='root',passwd='root',db='twitter',port=3306)
	cur=conn.cursor()
	cur.execute('select concat(A.user_id, \'\t#\', B.screen_name) as user_info, A.hour, A.total_count from tweet_count_hour_normalized A,twitter_user B where A.user_id=B.id order by user_id')
	while True:
		row = cur.fetchone()
		if row == None:
			break
		user_id = row[0]
		if user_id not in dist:
			mm = [0 for i in range(24)]
			dist[user_id] = mm
		dist[user_id][int(row[1])]=float(row[2])
	cur.close()
	conn.commit ()
	conn.close ()
	print 'done!	user distributions size:%d'%len(dist.keys())
	
	print 'output to files ... '
	w_file = open('./tweets_distribution.txt','w')
	for key,value in dist.items():
		w_file.write(key + '\n')
		data = ''
		for i in range(24):
			data = data + str(value[i]) + '\t'
		w_file.write(data + '\n')
	w_file.close()
	
def main(mode = 1):
	getDistribution()
	
if __name__ == '__main__':
    main()

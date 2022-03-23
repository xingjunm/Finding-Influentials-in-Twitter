#! /usr/bin/python
# -*- coding: utf-8 -*-
# count reweet interval.
import os,math
import MySQLdb
	
def getDelayDistribution():
	print 'start ... get delay distributions'
	conn=MySQLdb.connect(host='localhost',user='root',passwd='root',db='twitter',port=3306)
	cur=conn.cursor()
	w_f = open('cumulative_delay_distribution.txt','w')
	end = -1
	sql = ''
	for i in range(7):
		for j in range(1,10):
			end = j*math.pow(10,i)
			result = ''
			sql = 'select count(*) from count_retweet_delay where seconds>' + str(end)
			cur.execute(sql)
			while True:
				row = cur.fetchone()
				if row == None:
					break
				count = float(row[0])
				p = count/600943
				result = result + str(end) + '\t' + str(p)
			sql = 'select count(*) from count_reply_delay where seconds>' + str(end)
			cur.execute(sql)
			while True:
				row = cur.fetchone()
				if row == None:
					break
				count = float(row[0])
				p = count/27067
				result = result + '\t' + str(p) + '\n'
			w_f.write(result)
	cur.close()
	conn.commit ()
	conn.close ()
	w_f.close()
	print 'done. delay distributions.'
	
def getLookbackDistribution():
	print 'start ... get lookback distributions'
	conn=MySQLdb.connect(host='localhost',user='root',passwd='root',db='twitter',port=3306)
	cur=conn.cursor()
	w_f = open('cumulative_lookback_distribution.txt','w')
	end = -1
	sql = ''
	for i in range(7):
		for j in range(1,10):
			end = j*math.pow(10,i)
			result = ''
			sql = 'select count(*) from count_retweet_delay where tweet_count>' + str(end)
			cur.execute(sql)
			while True:
				row = cur.fetchone()
				if row == None:
					break
				count = float(row[0])
				p = count/600943
				result = result + str(end) + '\t' + str(p)
			sql = 'select count(*) from count_reply_delay where tweet_count>' + str(end)
			cur.execute(sql)
			while True:
				row = cur.fetchone()
				if row == None:
					break
				count = float(row[0])
				p = count/27067
				result = result + '\t' + str(p) + '\n'
			w_f.write(result)
	cur.close()
	conn.commit ()
	conn.close ()
	w_f.close()
	print 'done. lookback distributions.'
	
def main(mode = 1):
	#getDelayDistribution()
	getLookbackDistribution()
	
if __name__ == '__main__':
    main()

#! /usr/bin/python
# -*- coding: utf-8 -*-
# count reweet interval.
import os
import MySQLdb
	
def count_user_days():
	w_file = open('./user_days.txt', 'w')
	users = os.listdir('./home_line')
	count = 0
	for user in users:
		r_file = open('./home_line/' + user, 'r')
		times = r_file.read().strip().strip(',').split(',')
		sorted_times = []
		
		num = len(times)
		if num == 0:
			continue			
		for i in range(num):
			if times[i] == '':
				continue
			sorted_times.append(int(times[i]))			
		sorted_times.sort()
		 
		num = len(sorted_times)
		if num == 0:
			continue
		min_day = sorted_times[0]
		max_day = sorted_times[num-1]
		days = (max_day-min_day)/(3600*24.0) + 1# from seconds to days
		
		w_file.write(user + ' ' + str(num) + ' ' + str(days) + '\n')
		count += 1
		if count%100 == 0:
			print 'count %s users\' collect days'%count
	
def store_into_db():
	r_file = open('./user_days.txt', 'r')
	rows = []
	for line in r_file:
		row = line.strip().split()
		tmp = []
		num = int(row[1])
		days = float(row[1])
		tmp.append(row[0])#user_id
		tmp.append(row[1])#total_count
		tmp.append(row[2])#days
		tmp.append(0)#read_habit
		avg_total = 0.0#avg_total per day
		if num == 3200:
			avg_total = num/days
		else:
			avg_total = num/30.0
		tmp.append(str(avg_total))
		rows.append(tmp)
		
	conn=MySQLdb.connect(host='localhost',user='root',passwd='root',db='twitter',port=3306)
	cur=conn.cursor()
	cur.executemany('insert ignore into user_habit values(%s,%s,%s,%s,%s)',rows)
	cur.close()
	conn.commit ()
	conn.close ()
	
def main(mode = 1):
	#count_user_days()	
	store_into_db()
	
if __name__ == '__main__':
    main()

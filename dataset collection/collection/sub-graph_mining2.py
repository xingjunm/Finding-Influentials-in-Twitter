#! /usr/bin/python
# -*- coding: utf-8 -*-
import time, datetime, tweepy, sys, json
from tweepy.cursor import Cursor
from tweepy.models import Status
from tweepy.api import API

def main( mode = 1 ):
	user_records = open('./data/newyork/result-step_1.txt', 'r')
	output = open('./tmp/result-step_2.txt', 'w')
	user_ids = []
	for line in user_records:
		tmp = line.strip().split('\t')
		user_ids.append(set(tmp))
	user_records.close()
	print 'number of sets:%s'%len(user_ids)
	try:
		set_len = len(user_ids)
		common_flag = True
		i = 0
		for i in range(0,set_len-1):
			for j in range(i+1,set_len):
				set1 = user_ids[i]
				set2 = user_ids[j]
				common = set1.intersection(set2)
				if len(common) > 0:
					user_ids[i]=set1.union(set2)
					user_ids[j].clear()
				
		for i in range(0,set_len):
			tmp_set = user_ids[i]
			if len(tmp_set):
				for element in tmp_set:
					output.write(element + '\t')
				output.write('\n')
				output.flush()
		output.close()
	except Exception, e:
		print e
		output.close()

def miningMax(user_id, friend_ids, user_ids, result):
	#print 'miningMax...user:%s,friend:%s'%(user_id,len(friend_ids))
	if user_id not in result:
		result.add(user_id)
	user_ids[user_id]=[]
	searchset = set()
	for friend_id in friend_ids:
		searchset.add(friend_id)
	# iterate friends' relations
	try:
		element = searchset.pop()
		while element:
			if element not in result:
				result.add(element)
				tmp_list = user_ids[element]
				if len(tmp_list) != 0:
					searchset.union(set(tmp_list))
					user_ids[element]=[]
			element = searchset.pop()
	except Exception, e:
		print e
		return

if __name__ == '__main__':
    main()

#! /usr/bin/python
# -*- coding: utf-8 -*-
import time, datetime, tweepy, sys, json
from tweepy.cursor import Cursor
from tweepy.models import Status
from tweepy.api import API

def main( mode = 1 ):
	user_records = open('./user-relation-2.txt', 'r')
	user_ids = {}
	for line in user_records:
		tmp = line.strip().split('\t')
		user_ids.setdefault(tmp[0], []).append(tmp[1])
	user_records.close()
	print 'user_ids:%s'%len(user_ids)
	output = open('./tmp/result-step_1.txt', 'a')
	result = set()
	try:
		for k,v in user_ids.items():
			if len(v) == 0:
				continue
			miningMax(k, v, user_ids, result)
			for i in result:
				output.write(i + '\t')
			output.write('\n')
			output.flush()
			print 'collect %s users...'%len(result)
			result = set()
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

#! /usr/bin/python
# -*- coding: utf-8 -*-
# store valid user-relation into txt file.
import os

file_list = os.listdir('../relations/')
print '%s users\' relations have been collected!'%len(file_list)
count = 0
fw = open('./user-relation.txt', 'w')
for tweet_file in file_list:
	count+=1
	if count%100==0:
		print 'handle %s users\' relations ...'%count
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
	user_Friends = []
	for friend_id in friends:
		if friend_id in file_list:
			# print '%s	%s'%(user_id,friend_id)
			fw.write(user_id + '\t' + friend_id + '\n')
	fw.flush()
	f.close()
fw.close()
		

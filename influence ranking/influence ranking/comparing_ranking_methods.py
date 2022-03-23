#! /usr/bin/python
# -*- coding: utf-8 -*-

import os

def main():
	ttr = load('generalRanking-ttr-100.dat')
	tr = load('generalRanking-100.dat')
	fr = load('FR.txt')
	rr = load('RR.txt')
	
	w_file = open('compareRanking.dat','w')
	for i in range(len(ttr)):		
		user_name = ttr[i]
		result = user_name + '\t' + str(i+1)
		result += '\t' + str(tr.index(user_name)+1) # tr result
		result += '\t' + str(fr.index(user_name)+1) #
		result += '\t' + str(rr.index(user_name)+1) #
		w_file.write(result + '\n')
	w_file.close()
	
# load list from file,once a line	
def load(file_name):
	r_file = open(file_name,'r')
	result = []
	for line in r_file:
		result.append(line.strip())
	print 'load:%s'%len(result)
	r_file.close()
	return result

# find the similarity between two lists
def compare(list1,list2,size):
	result = ''
	for i in range(size):
		for j in range(size):
			if list1[i] == list2[j]:
				result += list1[i] + ','
	return result
	
if __name__ == '__main__':
	main()
	print 'all done!'

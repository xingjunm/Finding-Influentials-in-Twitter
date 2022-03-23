#! /usr/bin/python
# -*- coding: utf-8 -*-

import os, csv

def resample(ratio):	
	file_list = os.listdir('./dataset')
	w_csvfile = file('./dataset-resample/resample-' + str(ratio) + '.csv', 'wb')
	writer = csv.writer(w_csvfile)
	title = True
	for file_name in file_list:
		r_csvfile = file('./dataset/' + file_name, 'rb')
		reader = csv.reader(r_csvfile)
		count = 0
		yes_num = 0
		for line in reader: # just count
			#print line
			count += 1
			if count == 1:
				continue		
			label = line[-1]
			if label == '1':
				yes_num += 1
		r_csvfile.close()
		
		if yes_num == 0:
			continue
		
		r_csvfile = file('./dataset/' + file_name, 'rb')
		reader = csv.reader(r_csvfile)
		
		no_num = count - yes_num		
		max_num = ratio*yes_num
		interval = no_num/max_num
		
		print 'no_num:%s, max_num:%s, interval:%s '%(no_num,max_num,interval)
		
		count = 0
		flag = 0
		for line in reader:
			count += 1
			if count == 1 and title:
				writer.writerow(line)
				title = False
				continue
			label = line[-1]
			if label == '1':
				writer.writerow(str2num(line))
			elif label == '0':
				if flag%interval == 0:
					writer.writerow(str2num(line))
				flag += 1
		r_csvfile.close()
		#w_csvfile.close()
	w_csvfile.close()		

def str2num(data_list):
	data = []
	for i in range(len(data_list)):
		data.append(float(data_list[i]))
	return data

if __name__ == '__main__':
	for i in range(1,11):
		print 'resample %s round dataset...'%i
		resample(i)
	print 'done!'

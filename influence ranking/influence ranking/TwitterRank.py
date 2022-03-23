#! /usr/bin/python
# -*- coding: utf-8 -*-
import gv
import os
import MySQLdb
import numpy as np
# Import pygraph

from pygraph.classes.digraph import digraph
from pygraph.readwrite.dot import write

# Define pagerank function
def pagerank(graph, damping_factor=0.85, max_iterations=200, \
             min_delta=0.00001):
    """
    Compute and return the PageRank in an directed graph.    
     
    @type  graph: digraph
    @param graph: Digraph.
     
    @type  damping_factor: number
    @param damping_factor: PageRank dumping factor.
     
    @type  max_iterations: number 
    @param max_iterations: Maximum number of iterations.
     
    @type  min_delta: number
    @param min_delta: Smallest variation required for a new iteration.
     
    @rtype:  Dict
    @return: Dict containing all the nodes PageRank. value is a list which contains all of the 50 topics' rank.
    """    
    nodes = graph.nodes()
    graph_size = len(nodes)
    if graph_size == 0:
        return {}
    # array value for nodes without inbound links, which like a vector
    min_value = np.repeat((1.0-damping_factor)/graph_size,100) 
     
    # itialize the page rank dict with 1/N for all nodes
    #pagerank = dict.fromkeys(nodes, 1.0/graph_size)
    pagerank = dict.fromkeys(nodes, np.repeat(1.0,100))
    w_file = open('diff-tr-100.dat','w')
    for i in range(max_iterations):
        diff = np.zeros(100) #total difference compared to last iteraction
        # computes each node PageRank based on inbound links
        for node in nodes:
            #print 'node:%s'%node
            rank = np.copy(min_value)
            for in_link in graph.incidents(node):
                #print 'in_link:%s'%in_link
                rank += damping_factor*trans_prob(in_link,node)* pagerank[node] + \
                        (1-damping_factor)*jump(node)
            diff += abs(pagerank[node] - rank)
            pagerank[node] = np.copy(rank)
        print 'This is NO.%s iteration' % (i+1)
        #print pagerank
 
        #stop if PageRank has converged, which means the max/min/mean
        w_file.write(str(np.mean(diff)) + '\n')
        if np.mean(diff) < min_delta:
            break
    w_file.close()    
    return pagerank

# Define transition probability function
def trans_prob(from_node, to_node):
	"""
    Compute and return the transition probability between two nodes.    
     
    @type  from_node: string
    @param from_node: from_node.
     
    @type  to_node: string
    @param to_node: to_node.

    @return: p the transmistion probability of from_node to to_node, which contains all of the topics as an array.
    """
	key = from_node + '_' + to_node
	# ratio: (number of tweets published by sj)/(the number of tweets published by all of si¡¯s friends)
	# sim contains is the similarity between si and sj in topic t
	sim = SIM[key]
	ratio = RATIO[key]
	return sim*ratio

# Define teleportation probability function
def jump(node):
	"""
    Compute and return the transition probability between two nodes.    
     
    @type  node: string
    @param node: node name.

    @return: p the transmistion probability of from_node to to_node.
    """
	return TELE[node]

# Define init_graph function
def init_graph(node_file, relation_file):
	"""
    create the graph from relation file.

    @type  node_file: string
    @param node_file: path and the file name.

    @type  relation_file: string
    @param relation_file: path and the file name.
    
    @return: digraph consist of all the nodes and edges.
    """

	gr = digraph()
	
	# Add nodes
	file_node = open(node_file,'r')
	for line in file_node:
		if line.strip() =='':
			continue
		gr.add_node(line.strip())
	file_node.close()

	file_edge = open(relation_file, 'r')
	# Add edges
	for line in file_edge:
		if line.strip() =='':
			continue
		nodes = line.strip().split()
		#print nodes
		# tweet diffusion path is the reverse of following direction
		if len(nodes) == 2:
			gr.add_edge((nodes[0],nodes[1]))
	file_edge.close()
	print 'done... init graph...'
	return gr


# Define init_metadata function - topic specific
def init_metadata(ratio_file, sim_file, jump_file):
	"""
    load the metadata into memory.    
     
    @type  ratio_file: string
    @param ratio_file: file contains the ratio information.

	@type  sim_file: string
    @param sim_file: file contains the topic similarity of two users.
    
    @type  jump_file: string
    @param jump_file: file contains the jump probability.

    @return: 
    """

	# Load similarity data
	global RATIO
	RATIO = {}
	file_ratio = open(ratio_file, 'r')
	for line in file_ratio:
		if line.strip() =='':
			continue
		items = line.split()
		RATIO[items[0] + '_' + items[1]] = float(items[2])
	file_ratio.close()
	
	# Load similarity data
	global SIM
	SIM = {}
	file_sim = open(sim_file, 'r')
	for line in file_sim:
		if line.strip() =='':
			continue
		items = line.split()
		label = items[0]
		data = []
		for i in range(1,len(items)):
			data.append(float(items[i]))
		SIM[label] = np.array(data)
	file_sim.close()
	
	# Load teleportation data
	global TELE
	TELE = {}
	file_jump = open(jump_file, 'r')
	for line in file_jump:
		if line.strip() =='':
			continue
		items = line.split()
		label = items[0]
		data = []
		for i in range(1,len(items)):
			data.append(float(items[i]))
		TELE[label] = np.array(data)
	file_jump.close()
	print 'done... init metadata...'

def store2file(rank):
	""" 
	store the ranking result into file
	@type rank: {user_id:vector}
	@param rank: the ranking result of twitterrank
	"""
	w_file = open('rankingResult-100.dat','w')
	result = ''
	for key,value in rank.items():
		result = key
		for x in np.nditer(value):
			result+= '\t' + str(x) 
		result+= '\n'
		w_file.write(result)
	w_file.close()

def afterRank():
	# load topic weight
	r_file = open('topicweight-100.txt', 'r')
	data = []
	for line in r_file:
		data.append(float(line.strip()))
	weight = np.array(data)
	# load ranking result
	ranking = []
	r_file = open('rankingResult-100.dat', 'r')
	userIds = []
	for row in r_file:
		items = row.split()
		userIds.append(items[0])
		tmp = []
		for i in range(1,len(items)):
			tmp.append(float(items[i]))
		tmp_array = np.array(tmp)*weight
		ranking.append(np.sum(tmp_array))
	r_file.close()
	dist = np.array(ranking)
	result = np.argsort(-dist,axis=0) # sort align x with descending order
	
	user_names = {}
	conn=MySQLdb.connect(host='localhost',user='root',passwd='root',db='twitter',port=3306)
	cur=conn.cursor()
	cur.execute('select id, screen_name from twitter_user')
	count=0
	while True:
		row = cur.fetchone()
		if row == None:
			break
		user_names[row[0]] = row[1]
		count+=1
	print 'load %s users'%count
	cur.close()
	conn.close ()
		
	w_file = open('generalRanking-100.dat','w')	
	for i in range(len(result)):
		index = result[i]
		user_id = userIds[index]
		user_name = user_names[user_id]
		#print user_name
		w_file.write(user_name + '\n')
	w_file.close()
	
	
	
if __name__=='__main__':
	#gr = init_graph('nodes.dat','edges.dat')
	#init_metadata('i-j-ratio.dat', 'sim-100.dat', 'jump-100.dat')
	#rank = pagerank(gr)
	#store2file(rank)
	afterRank()
	#print rank
	# Draw as PNG
	#dot = write(gr)
	#gvv = gv.readstring(dot)
	#gv.layout(gvv,'dot')
	#gv.render(gvv,'png','Model.png')

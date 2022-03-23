#! /usr/bin/python
# -*- coding: utf-8 -*-
# LDA preprocessing, from documents to word vectors

import nltk, re
import logging
from gensim import corpora, models, similarities
from gensim.corpora import TextCorpus, MmCorpus, Dictionary 
from gensim.models import TfidfModel, LsiModel, LdaModel, HdpModel
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem.porter import PorterStemmer
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.rslp import RSLPStemmer
import numpy as np
import os, csv

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    
class MyTextCorpus(TextCorpus):
	def get_texts(self):
		length = 0
		docs = os.listdir(self.input)
		for doc in docs:
			doc_file = open(self.input + '/' + doc, 'r')
			lines = doc_file.read()
			words = lines.strip().split()
			if len(words) > 0:
				length+=1
				yield [word for word in words]
		self.length = length
		print 'self.length=%s'%self.length

# store doc-topic matrix into file_name
def store_doc_topic(corpus, model, file_name):
	print 'store_doc_topic'
	csvfile = open(file_name, 'wb')
	writer = csv.writer(csvfile)		
	for doc in corpus:
		row = model.__getitem__(doc, eps=0)
		tmp = []
		for i in range(len(row)):
			tmp.append(row[i][1])
		writer.writerow(tmp)
	csvfile.close()


def store_topic_word(model, file_name):
	print 'store_topic_word'
	csvfile = open(file_name, 'wb')
	writer = csv.writer(csvfile)
	for topicid in range(model.num_topics):
		row = model.state.get_lambda()[topicid]
		#topic = topic / topic.sum() # normalize to probability dist
		writer.writerow(row)
	csvfile.close()

# load corpus and dictionary 
# and then carry out the persistance
def beforeLDA():
	my_corpus = MyTextCorpus('./processed-texts/')
	#print my_corpus
	#for vector in my_corpus:
		#print vector
	my_corpus.dictionary.save("./model-data/my_dict.dict")
	MmCorpus.serialize("./model-data/my_corpus.mm", my_corpus)

# transfer the original format of the corpus to the specific 
# fromat, which is essiential for LSI or LDA
def dataFormatTransfer():
	dictionary = Dictionary.load('./model-data/my_dict.dict')
	#print dictionary
	#print dictionary.token2id
	mm_corpus = MmCorpus('./model-data/my_corpus.mm')
	#print mm_corpus
	#print list(mm_corpus)
	
	tfidf = TfidfModel(mm_corpus, normalize=True) # step 1 -- initialize a model
	tfidf_corpus = tfidf[mm_corpus] # step 2 -- use the model to transform vectors
	#for doc in tfidf_corpus:
		#print doc
	MmCorpus.serialize("./model-data/tfidf_corpus.mm", tfidf_corpus)
	#persistence
	tfidf.save("./model-data/tfidf.model")

#################   LSI模型  ###################
def Lsi():
	dictionary = Dictionary.load('./model-data/my_dict.dict')
	tfidf_corpus = MmCorpus("./model-data/tfidf_corpus.mm")
	lsi = LsiModel(tfidf_corpus, id2word=dictionary, num_topics=50) # initialize an LSI transformation
	corpus_lsi = lsi[tfidf_corpus] # create a double wrapper over the original corpus: bow->tfidf->fold-in-lsi
	#lsi.print_topics(2)
	for doc in corpus_lsi: # both bow->tfidf and tfidf->lsi transformations are actually executed here, on the fly
		print doc
	lsi.save('./model-data/lsi.model') # same for tfidf, lda, ...
    #lsi = models.LsiModel.load('/tmp/model.lsi')
    
#################   LDA模型  ###################
def Lda():
	##dictionary = Dictionary.load('./model-data/my_dict.dict')
	mm_corpus = MmCorpus("./model-data/my_corpus.mm")
	##lda = LdaModel(corpus=mm_corpus, id2word=dictionary, num_topics=100)
	
	#lda_corpus = lda[tfidf_corpus]
	##lda_corpus = lda[mm_corpus]
	##MmCorpus.serialize("./model-data/lda_corpus.mm", lda_corpus)
	
	#persistence
	##lda.save("./model-data/lda-100.model")
	lda = LdaModel.load("./model-data/100/lda.model") # this means lda model just need to be trained once, after that just load it
	print '################################'
	store_doc_topic(mm_corpus, lda, './model-data/100/doc-topic.csv')
	print '################################'
	#writeDT2file(doc_topic, )
	print '################################'
	store_topic_word(lda,'./model-data/100/topic-word.csv')
	#writeTW2file(topic_words, './model-data/topic-word-50.csv')
	print '################################'
	shown = lda.show_topics(100) #show_topics(self, topics=10, topn=10, log=False, formatted=True)
	writeT2file(shown, './model-data/100/topics.dat')

#################   HDP模型  ###################
def Hdp():
	"""
	Hierarchical Dirichlet Process Model is a oneline general LdaModel 
	It can run a generality type of Lda without parameters
	It thus can estimate the alpha and theta , and determine the optimal numbers of topics
	"""
	dictionary = Dictionary.load('./model-data/my_dict.dict')
	mm_corpus = MmCorpus("./model-data/my_corpus.mm")
	hdp = HdpModel(mm_corpus, dictionary, outputdir='./model-data/hdp')
	hdp.save_options()
	hdp.save_topics()

def writeT2file(data, file_name):
	file = open(file_name, 'w')
	for line in data:
		file.write(line + '\n')
	file.close()

def doc2id():
	file = open('./model-data/doc2id.dat', 'w')
	docs = os.listdir('./processed-texts/')
	i = 0
	for doc in docs:
		file.write(doc + '\t' + str(i) + '\n')
		i += 1
	file.close()

# column and row normalize the doc-topic matrix
def afterLDA():
	# load doc-topic distribution
	doc_topic = []
	csvfile = open('./model-data/100/doc-topic.csv', 'rb')
	reader = csv.reader(csvfile)
	for row in reader:
		tmp = []
		for i in range(len(row)):
			tmp.append(float(row[i]))
		doc_topic.append(tmp)
	csvfile.close()
	dist = np.matrix(doc_topic)
	#print dist
	# row normalization
	row_norm = dist/dist.sum(axis=1)	
	np.savetxt('./model-data/100/doc-topic_rownorm.txt',row_norm)
	column_norm = dist/dist.sum(axis=0)
	np.savetxt('./model-data/100/doc-topic_columnnorm.txt',column_norm)
	
	# load topic-word distribution
	topic_word = []
	csvfile = open('./model-data/100/topic-word.csv', 'rb')
	reader = csv.reader(csvfile)
	for row in reader:
		tmp = []
		for i in range(len(row)):
			tmp.append(float(row[i]))
		topic_word.append(tmp)
	csvfile.close()
	dist = np.matrix(topic_word)
	row_sum = dist.sum(axis=1)
	np.savetxt('./model-data/100/topicweight.txt', row_sum/row_sum.sum(axis=0)) # normalized topic weight refering to the count of words assigned to the topic
	
if __name__ == '__main__':
	#beforeLDA()
	#dataFormatTransfer()
	#Lsi()
	#Lda()
	doc2id()
	#Hdp()
	#afterLDA()


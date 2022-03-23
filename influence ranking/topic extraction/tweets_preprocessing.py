#! /usr/bin/python
# -*- coding: utf-8 -*-
# LDA preprocessing, from documents to word vectors

import nltk, re
import logging
from gensim import corpora, models, similarities
from gensim.corpora import TextCorpus, MmCorpus, Dictionary 
from gensim.models import TfidfModel, LdaModel
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem.porter import PorterStemmer
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.rslp import RSLPStemmer

import os,json

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# tweets ----> rawtexts
def extract_rawtexts():
	count = 0
	file_list = os.listdir('./tweets/')
	for tweet_file in file_list:
		f = open('./tweets/' + tweet_file, 'r')
		w = open('./raw-texts/' + tweet_file, 'a')
		user_id = tweet_file		
		for line in f:
			tmp = line.strip()
			if tmp == '':
				print 'The end of tweets file...'
			else:
				try:
					tmp = json.loads(tmp)
					text = ''
					## text
					if tmp['text'] is not None:
  						text = tmp['text'].encode('utf-8')
					#print 'text=' + text
  					## remove 'RT '
  					text = text.replace('RT ','')
					text = text.replace('Rt ','')
					text = text.replace('rt ','')
  					## remove '#' from hashtags
  					text = text.replace('#','')
  					## remove '$' : stock ticker symbol
  					text = text.replace('$','')
  					## remove @username
  				 				
  					if tmp['entities'] is not None:
  						entities = tmp['entities']
  						## symbols 
  					
  						## user_mentions 
  						if entities.has_key('user_mentions') and len(entities['user_mentions']) > 0:
  							for mention in entities['user_mentions']:
  								## remove @screen_name
  								user_name = mention['screen_name'].encode('utf-8')
								text = text.replace('@' + user_name + ':','')						
  								text = text.replace('@' + user_name,'')
							
  								## remove @username
  								user_name = mention['name'].encode('utf-8')
								text = text.replace('@' + user_name + ':','')
  								text = text.replace('@' + user_name,'')			

  						## hashtags 
  						if entities.has_key('urls') and len(entities['urls']) > 0:
  							for tag in entities['urls']:
  								## remove http://
  								url = tag['url'].encode('utf-8')
  								text = text.replace(url,'')
  						## media 
  						if entities.has_key('media') and len(entities['media']) > 0:  						
  							for media in entities['media']:
  								## remove http://
  								url = media['url'].encode('utf-8')
  								text = text.replace(url,'')
					text = text.strip()
					#print 'text=' + text
  					w.write(text + '\n')
					#break
				except Exception, e:
						print e
			   			print 'exception:user %s'%user_id
			   			print tmp
			   			continue
		w.close()
		f.close()
		count = count + 1
		if count%100==0:
			print 'handle %s users\' tweets.'%count

# rawtexts ----> processing-texts
def pre_processing(path):
	#词形还原
	wnl = nltk.WordNetLemmatizer()
	#porter = nltk.PorterStemmer()
	docs = os.listdir(path)
	count = 0
	file = open('moodword.txt')
	allMoodWord = file.read()
	allMoodWord = allMoodWord.lower()
	
	for doc in docs:
		count+=1
		doc_file = open(path + '/' +doc, 'r')
		w = open('./processing-texts/' + doc, 'w')
		#texts = ''
		#tempText = ''
		for rawtext in doc_file:
			if len(rawtext) == 0:
				continue
			rawtext = rawtext.lower()
			# delete non-English characters
			rawtext = re.sub(r'[^a-zA-Z]', ' ', rawtext)
			# delete words with < 3 characters
			tokens = nltk.regexp_tokenize(rawtext, r'[a-zA-Z]{3,}')
			text = ''
			for token in tokens:
				temp = wnl.lemmatize(token)
				# delete stopwords, mood words and words < 3 characters
				if temp not in nltk.corpus.stopwords.words('english') and allMoodWord.find(temp) == -1 and len(temp)>=3 :
					text = text + temp + ' '
			# delete repetive words like: hahaha，haaaa
			text = re.sub(r'\w*(\w+)\1{2,}\w*\s|\w*([a-z])\2{2,}\w*\s', '', text)
			#LancasterStemmer/PorterStemmer
			lanst = LancasterStemmer()
			po = PorterStemmer()
			#text = lanst.stem(text)
			# delete empty spaces
			text = text.strip()
			if len(text)>1 :
				#w.write(text+'\n')
				temptokens = text.split(' ')
				temptext1 = ''
				#temptext2= ''
				for temptoken in temptokens:
					if temptoken.endswith('e') or temptoken.endswith('y'):#以e或者y结尾的词不进行变化
						temptext1 +=temptoken+' '
						#temptext2 +=temptoken+' '
					#elif temptoken.endswith('ful') or temptoken.endswith('ing'):
						#temptext1+=lanst.stem(temptoken)+' '
						#temptext2+=lanst.stem(temptoken)+' '
					#else :
						 ##temptoken=lanst.stem(temptoken)
						 #temptext1+=lanst.stem(temptoken)+' '
						#temptext2+=po.stem(temptoken)+' '
					elif len(lanst.stem(temptoken))>=len(po.stem(temptoken)):
						temptext1+=lanst.stem(temptoken)+' '
					else:
						temptext1+=po.stem(temptoken)+' '
				temptext1 = temptext1.strip()
				if len(temptext1)>1:
					w.write(temptext1+'\n')
				#w.write(temptext2.strip()+'\n')
				#tempText += text+'\n'
				#texts += text
		#all_tokens = texts.split(' ');
		#lineText = tempText.split('\n')
		#for oneline in lineText:
			#linetokens = oneline.split(' ')
			#for linetoken in linetokens:
				#if 
		w.close()
		if count%50==0:
			print 'already handled %s users'%count

def main():
	#extract_rawtexts()
	pre_processing('./raw-texts')	
	
if __name__ == '__main__':
	main()

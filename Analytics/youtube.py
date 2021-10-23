import numpy as np 
import pandas as pd 
import pymongo
from collections import Counter
import operator
import time
from datetime import datetime,timedelta
import re
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
#nltk.download('stopwords',download_dir='/root/nltk_data')
nltk.download('stopwords',download_dir='./')
nltk.download('punkt',download_dir="./")
nltk.download('wordnet',download_dir="./")
stop_words = nltk.corpus.stopwords.words('english')
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx

client=pymongo.MongoClient("mongodb+srv://KokilaReddy:KokilaReddy@cluster0.5nrpf.mongodb.net/Social_media_data?retryWrites=true&w=majority")
db=client['Social_media_data']
begin=time.time()
class YouTube:
	def __init__(self,brand,duration):
		self.youtube=db['youTube']
		self.brand=brand
		self.duration=duration
		#time for requested 
		minimumtime=datetime.now()-timedelta(days=duration)
		query={"tag":str(self.brand),"created_time":{"$gte":minimumtime}}
		result=self.youtube.find(query)
		df=pd.DataFrame(list(result))

		#getting numeric columns
		try:
		    dictonary=df['misc']
		    numeric_df=pd.DataFrame(list(dictonary))
		    
		    self.numeric_df=numeric_df
		except:
		    #print(df)
		    print("data doesn't exists!")
		#print(df.columns)
		self.df=df

	def getHashTags(self):
		try:
		    self.tags=[tag for list1 in self.numeric_df['tags'] for tag in list1]
		    frequency=Counter(self.tags)
		    frequency=sorted(frequency.items(),key=operator.itemgetter(1),reverse=True)
		    top15=dict(frequency[:15])
		    return top15
		except Exception as e:
			print("error in get hashtags of youttube");
			return []


	
	def InfluencingChannels(self,num=10):
		try:
			self.numeric_df['id']=self.df['id']
			likecount=self.numeric_df[['channelTitle','likeCount','id']]
			sorted_values=likecount.sort_values('likeCount',axis=0,ascending=False)
			top_values=sorted_values.iloc[:num]
			data= top_values.to_dict('records')
			return data
			#print(type(data))
		except Exception as e:
			print("error in influencin channels function!!");
			print(e)
			return []

	def ChannelsWithMoreDiscussions(self,num=10):
		try:
		    commentCount=self.numeric_df[['channelTitle','commentCount','id']]
		    sorted_values=commentCount.sort_values('commentCount',axis=0,ascending=False)
		    top_values=sorted_values.iloc[:num]
		    data= top_values.to_dict('records')
		    #print(type(data))
		    return data
		except Exception as e:
			print("problem with channel with mpre discussion function")
			return []

	def categoriesOfMentions(self):
		try:
			categorycount={}
			for i in self.numeric_df.index:
				if self.numeric_df['category'][i] in categorycount:
				    categorycount[self.numeric_df['category'][i]]+=1
				else:
				    categorycount[self.numeric_df['category'][i]]=0
			return categorycount
		except Exception as e:
			print(e)
			print("problem with categories!!")
			return []

			#return []
	
	def __similarity_Matrix(self,comments):
		sentences = [] 
		for s in comments:
			sentences.append(sent_tokenize(s))
		sentences = [y for x in sentences for y in x] # flatten list
		#translate language
		try:
			lang = detect(sentences)
			if lang != 'en':
		    		translator = google_translator()
		    		sentences = translator.translate (sentences,lang_tgt='en')
		except :
			try:
		    		translator = google_translator()
		    		sentences = translator.translate (sentences,lang_tgt='en')
			except:
			    	pass
			    	
		#remove html elements
		TAG_RE = re.compile(r'<[^>]+>')
		def remove_tags(text):
        		return TAG_RE.sub('', text)
		sentences=[remove_tags(r) for r in sentences]
        	
		#remove links
		sentences=[re.sub(r'http\S+', '', text) for text in sentences]
		# remove punctuations, numbers and special characters
		#clean_sentences = pd.Series(sentences).str.replace("[^a-zA-Z]", " ")
		def remove_pns(sentence):
			return re.sub("[^a-zA-Z]"," ",sentence)
		clean_sentences=[remove_pns(sentence) for sentence in sentences]
    		
		# make alphabets lowercase
		clean_sentences = [s.lower() for s in clean_sentences]
		
		#recording the new sentences of post
		self.complete_sentences.append(clean_sentences)
		# function to remove stopwords
		def remove_stopwords(sen):
			sen_new = " ".join([i for i in sen if i not in stop_words])
			return sen_new
		# remove stopwords from the sentences
		clean_sentences = [remove_stopwords(r.split()) for r in clean_sentences]
		'''sentence_vectors = []
		for i in clean_sentences:
			if len(i) != 0:
			    #print([word_embeddings.get(w,np.zeros((100,))) for w in i.split()])
			    v = sum([self.word_embeddings.get(w, np.zeros((100,))) for w in i.split()])/(len(i.split())+0.001)
			else:
			    v = np.zeros((100,))
			sentence_vectors.append(v)'''
		try:
			vectorizer = TfidfVectorizer()
			vectors = vectorizer.fit_transform(clean_sentences)
			feature_names = vectorizer.get_feature_names()
			dense = vectors.todense()
			sentence_vectors = dense.tolist()
			
		except:
			pass
		# similarity matrix
		sim_mat = np.zeros([len(sentences), len(sentences)])
		#print(len(sentences))
		#print(len(sentence_vectors))
		#print(len(sim_mat))
		for i in range(len(sentences)):
			for j in range(len(sentences)):
				try:
					if i != j:
						#print(sentence_vectors[i].shape,sentence_vectors[i].shape)
						sim_mat[i][j] = cosine_similarity(np.array(sentence_vectors[i]).reshape(1,len(feature_names)), np.array(sentence_vectors[j]).reshape(1,len(feature_names)))
				except:
					print(i,j)
		
		return sim_mat
	def __most_discussed(self,sim_mat,sentences):
	    #print(type(sim_mat))
	    nx_graph = nx.from_numpy_array(sim_mat)
	    scores = nx.pagerank(nx_graph)
	    #print(len(scores))
	    #sorted_scores=sorted(scores,reverse=True)
	    #print(scores)
	    #print("\n\n")
	    ranked_sentences = sorted(((scores[i],s) for i,s in enumerate(sentences) ), reverse=True)
	    return ranked_sentences[0][1]
	def getSummary(self):
		'''if(self.df.empty==True):
			print("data doesn't exists!")
			return []
		required=self.df['id']
		self.numeric_df['id']=required
		comments_df=self.numeric_df[['id','comments','commentCount']]
		for i in comments_df.index:
			x=comments_df['comments'][i]
			if(type(x) is dict and ('Comment' not in x)):
				print("no comments for the video")
				comments_df=comments_df.drop(i)
		comments_df.reset_index(inplace=True,drop=True)
		comments_df=comments_df.head(20)
		comments=[]
		for i in comments_df.index:
			x=comments_df['comments'][i]
			comments.append(comments_df['comments'][i]['Comment'])
		
		self.word_embeddings = {}
		f = open('./analytics/glove.6B.100d.txt', encoding='utf-8')
		for line in f:
		    values = line.split()
		    word = values[0]
		    coefs = np.asarray(values[1:], dtype='float32')
		    self.word_embeddings[word] = coefs
		f.close()
		
		self.complete_sentences=[]
		similarity_matrices=[]
		for i in comments:
    			similarity_matrices.append(self.__similarity_Matrix(i))
		text_summary={}
		for i in range(len(similarity_matrices)):
			text_summary[str(comments_df['id'][i])]=[self.__most_discussed(similarity_matrices[i],self.complete_sentences[i]),int(comments_df['commentCount'][i])]

		return text_summary
    		'''
    		
		youtube_TA=db['youtubeTextualAnalytics']
		minimum_time=minimumtime=datetime.now()-timedelta(days=self.duration)
		query={"tag":str(self.brand),"created_time":{"$gte":minimumtime}}
		#print(cursor.count())
		result=youtube_TA.find(query)
		print(result.count())
		df=pd.DataFrame(list(result))
		df=df.head(20)
		#print(df)
		#print("hello")
		text_summary={}
		for i in df.index:
			text_summary[str(df['id'][i])]=[str(df['summary'][i]),int(df['commentCount'][i])]
		return text_summary

	def negativeQuestions(self):
		pass
'''brand=input()
duration=int(input())		
youtube=YouTube(brand,duration)
print(youtube.getSummary())'''
end=time.time()
print(end-begin)


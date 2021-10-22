import numpy as np 
import pandas as pd 
import pymongo
from collections import Counter
import operator
import nltk
import re
import time
from datetime import datetime,timedelta
from nltk.tokenize import sent_tokenize
nltk.download('stopwords',download_dir='./')
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
stop_words = stopwords.words('english')
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
client=pymongo.MongoClient("mongodb+srv://KokilaReddy:KokilaReddy@cluster0.5nrpf.mongodb.net/Social_media_data?retryWrites=true&w=majority")
db=client['Social_media_data']
begin=time.time()
class Reddit:
	def __init__(self,brand,duration):
		self.reddit=db['reddit']
		self.brand=brand
		#timeforrequested
		minimumtime=datetime.now()-timedelta(days=duration)
		query={"tag":str(self.brand),"created_time":{"$gte":minimumtime}}
		result=self.reddit.find(query)
		df=pd.DataFrame(list(result))

		try:
		    #creating newdf for required df
		    dictonary=df['misc']
		    new_df=pd.DataFrame(list(dictonary))
		    
		    self.new_df=new_df
		except:
		    print(df)
		    print("data doesn't exists!")

		self.df=df

	def hotTopicBaseOnCc(self):
		try:
			title=self.df['text']
			self.new_df['title']=title
			id=self.df['id']
			self.new_df['id']=id
			commment_max=self.new_df['comments_num'].max()
			hotTopic=self.new_df.loc[self.new_df['comments_num']==commment_max]
			#hottopicsscore=hottopicscore.drop_duplicates(subset=['title'])
			data={
				"id":[str(i) for i in hotTopic["id"]],
				"title":[str(i) for i in hotTopic["title"]]
			}
			#data=jsonify(data)
			return data
		except Exception as e:
			print("error in hoptopicbasedoncc!")
			print(e)
			return []

	def hotTopicBasedOnScore(self):
		try:
			upvotesmax=self.new_df["score"].max()
			hottopicscore=self.new_df[self.new_df['score']==upvotesmax]
			hottopicsscore=hottopicscore.drop_duplicates(subset=['title'])
			data={
			"id":[str(i) for i in hottopicscore["id"]],
			"title":[str(i) for i in hottopicscore["title"]]
			}
			#data=jsonify(data)
			return data
		except Exception as e:
			print("error in hottopicbasedonscore!")
			print(e)
			return []		
		    
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

		TAG_RE = re.compile(r'<[^>]+>')
		#remove html tags
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
		
		self.complete_sentences.append(sentences)
		# function to remove stopwords
		def remove_stopwords(sen):
			sen_new = " ".join([i for i in sen if i not in stop_words])
			return sen_new
		# remove stopwords from the sentences
		clean_sentences = [remove_stopwords(r.split()) for r in clean_sentences]
		
		'''sentence_vectors = []
		for i in clean_sentences:
			if len(i) != 0:
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
		#print(sentence_vectors)
		# similarity matrix
		sim_mat = np.zeros([len(sentences), len(sentences)])
		#print(len(sentences))
		#print(len(sentence_vectors))
		#print(len(sim_mat))
		for i in range(len(sentences)):
			for j in range(len(sentences)):
				try:
					if i != j:
				    		sim_mat[i][j] = cosine_similarity(np.array(sentence_vectors[i]).reshape(1,len(feature_names)), np.array(sentence_vectors[j]).reshape(1,len(feature_names)))
				except:
					pass
		    
		#print("hello")
		return sim_mat
	def __most_discussed(self,sim_mat,sentences):
		nx_graph = nx.from_numpy_array(sim_mat)
		scores = nx.pagerank(nx_graph)
		#print(len(scores))
		#sorted_scores=sorted(scores,reverse=True)
		#print(sorted_scores)
		ranked_sentences = sorted(((scores[i],s) for i,s in enumerate(sentences) ), reverse=True)
		return ranked_sentences[0][1]

	def getSummary(self):
		if(self.df.empty==True):
			print("data doesn't exists!!")
			return []
		required=self.df['id']
		self.new_df['id']=required
		new_df=self.new_df
		new_df=new_df.sort_values('score',ascending=False)
		for i in new_df.index:
			if(type(new_df['comments'][i]) is dict):
				if(len(new_df['comments'][i]['comment'])==0):
					new_df.drop(i,inplace=True)
			else:
				if(len(new_df['comments'][i])==0):
					new_df.drop(i,inplace=True)
		new_df.reset_index(inplace=True,drop=True)
		
		new_df=new_df.head(20)
		new_df=new_df[['id','comments','score']]
		comments=[]
		for i in self.new_df.index:
			if(type(self.new_df['comments'][i]) is dict):
				comments.append(self.new_df['comments'][i]['comment'])
			else:
				comments.append(self.new_df['comments'][i])
	
			    
			    
			    #word embeddings
		'''self.word_embeddings = {}
		f = open('./analytics/glove.6B.100d.txt', encoding='utf-8')
		for line in f:
			values = line.split()
			word = values[0]
			coefs = np.asarray(values[1:], dtype='float32')
			self.word_embeddings[word] = coefs
		f.close()'''
				#similarity matrix
		self.complete_sentences=[]
		similarity_matrices=[]
		for i in comments:
			if(len(i)>0):
				similarity_matrices.append(self.__similarity_Matrix(i))
				
				#text summary
		text_summary={}
		for i in range(len(similarity_matrices)):
			text_summary[str(self.new_df['id'][i])]=[self.__most_discussed(similarity_matrices[i],self.complete_sentences[i]),int(self.new_df['score'][i])]
		return text_summary
    
		
		

	def getNegativeQuestions(self):
		pass





'''brand=input()
duration=int(input())		
reddit=Reddit(brand,duration)
print(reddit.getSummary())'''
end=time.time()
print(end-begin)

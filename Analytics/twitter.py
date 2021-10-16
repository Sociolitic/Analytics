import numpy as np 
import pandas as pd 
import pymongo
from collections import Counter
import operator
import time
from datetime import datetime,timedelta
import re
client=pymongo.MongoClient("mongodb+srv://KokilaReddy:KokilaReddy@cluster0.5nrpf.mongodb.net/Social_media_data?retryWrites=true&w=majority")
db=client['Social_media_data']
class Twitter:
	def __init__(self,brand,duration):
		self.twitter=db['twitter']
		self.brand=brand
		#timeforrequested
		minimumtime=datetime.now()-timedelta(days=duration)
		query={"tag":str(self.brand),"created_time":{"$gte":minimumtime}}
		result=self.twitter.find(query)
		df=pd.DataFrame(list(result))
		    
		#getting numer columns
		try:
		    dictonary=df['misc']
		    new_df=pd.DataFrame(list(dictonary))  
		    self.new_df=new_df
		except:
		    print(df)
		    print("Data doesn't exists")
		self.df=df

	def findInfluentialUser(self):
		try:
			#print(self.new_df.retweet_count)
			retweet_countmax=self.new_df['retweet_count'].max()
			active_users=self.new_df[self.new_df["retweet_count"]==retweet_countmax]
			return list(active_users.user_name)
		except:
			print("problem with data")
			return []
	def  HashTags(self):
		try:
			listofhashtags=[]
			re_hashtag=re.compile(r'#([^\s:]+)')
			for tweet in self.df['text']:
				listofhashtags.append(re_hashtag.findall(tweet))
				hashtags=[hashtag for list1 in listofhashtags for hashtag in list1]
				frequency=Counter(hashtags)
			return frequency
		except:
			print("problem with data")
			return []
	def getMostDiscussedTopic(self):
		pass
	def __questions(self,negative_mentions):
		questions=negative_mentions[negative_mentions['cleaned_text'].str.endswith("?")]
		#result=questions['cleaned_text'].str.contains("@[tT]esla")
		result=result | questions['cleaned_text'].str.contains("[Hh]ow") | questions['text'].str.contains("[Ww]hat") | questions['text'].str.contains("[Ww]here") | questions['text'].str.contains("[wW]ho") | questions['text'].str.contains("[Ww]hom")
		questions=questions[result] 
		return pd.DataFrame(list(set(questions.text)),columns=["questions"])
	    

	def getNegativeQuestions(self):
		negative_mentions=self.df[self.df['sentiment']=="Negative"]
		self.questions_text=self.__questions(negative_mentions)


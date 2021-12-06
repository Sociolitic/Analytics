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
		if(df.empty==True):
			print("data doesn't exists!!")
		else:
			print(df)
			
		try:    
			#getting number columns
			dict1=df['misc']
			x=list(dict1)
			new_df=pd.DataFrame([v for v in x if pd.notna(v)])
			#new_df=pd.DataFrame(x)
			self.new_df=new_df
		except Exception as e:
			print(e)
			print(df)
			print("problem with data")

		#print("problem in initialization process")
		#print("Data doesn't exists")
		self.df=df

	def findInfluentialUser(self):
		try:
			self.new_df['id']=self.df['id']
			#print(self.new_df.retweet_count)
			retweet_countmax=self.new_df['retweet_count'].max()
			active_users=self.new_df[self.new_df["retweet_count"]==retweet_countmax]
			list1=active_users[['user_name',"id"]]
			data={"active_users":[]}
			for i in list1.index:
				data['active_users'].append([list1['user_name'][i],list1['id'][i]])
			#print(type(data))
			return data
		except Exception as e:
			print("error in influentialuser function!");
			print(e)
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
			frequency=sorted(frequency.items(),key=operator.itemgetter(1),reverse=True)
			top15=dict(frequency[:15])
			return top15
		except Exception as e:
			print("error in hashtags function!")
			print(e)
			print("problem with data")
			return []
	def getMostDiscussedTopic(self):
		pass
	def __preprocess(self,tweet):
		try:
        		lang = detect(tweet)
        		if lang != 'en':
            			translator = google_translator()
            			tweet = translator.translate (tweet,lang_tgt='en')
		except:
			try:
				translator = google_translator()
				tweet = translator.translate (tweet,lang_tgt='en')
			except:
            			pass
            			
		#tweet = remove_links(tweet)
		tweet = re.sub(r'http\S+', '', tweet, flags=re.MULTILINE) # removing urls
 		
 		#remove html elements
		tweet = re.sub(r'<[^>]+>',' ',tweet)
		
		tweet = tweet.lower() # lower case
		tweet = re.sub("[^a-zA-Z0-9?]", ' ', tweet) # strip punctuation
		tweet = re.sub('\s+', ' ', tweet) #remove double spacing
		#remove emojils
		#tweet=removeemoji(tweet)
		return tweet
		
	def __questions(self,negative_mentions):
		questions=negative_mentions[negative_mentions['cleaned_text'].str.endswith("?")]
		#result=questions['cleaned_text'].str.contains(self.brand)
		result= questions['cleaned_text'].str.contains("[Hh]ow") | questions['cleaned_text'].str.contains("[Ww]hat") | questions['cleaned_text'].str.contains("[Ww]here") | questions['cleaned_text'].str.contains("[wW]ho") | questions['cleaned_text'].str.contains("[Ww]hom")
		questions=questions[result]
		finalquestions={}
		for i in questions.index:
			finalquestions[str(questions['id'][i])]=str(questions['text'][i]) 
		return finalquestions
		#return (list(set(questions.text)))
	    

	def getNegativeQuestions(self):
		try:
			self.df['cleaned_text']=self.df['text'].apply(self.__preprocess)
			negative_mentions=self.df[self.df['sentiment']=="Negative"]
			return self.__questions(negative_mentions)
		except Exception as e:
			print(e)
			return []
'''brand=input()
duration=int(input())
twitter=Twitter(brand,duration)
print(twitter.getNegativeQuestions())'''



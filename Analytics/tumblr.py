import pandas as pd
import numpy as np
from collections import Counter
import pymongo
import operator
import time
from datetime import datetime,timedelta

client=pymongo.MongoClient("mongodb+srv://KokilaReddy:KokilaReddy@cluster0.5nrpf.mongodb.net/Social_media_data?retryWrites=true&w=majority")
db=client['Social_media_data']

class Tumblr:
	def __init__(self,brand,duration):
		self.tumblr=db['tumblr']
		self.brand=brand

		#timeforrequested
		minimumtime=datetime.now()-timedelta(days=duration)
		query={"tag":str(self.brand),"created_time":{"$gte":minimumtime}}
		result=self.tumblr.find(query)

		df=pd.DataFrame(list(result))
		try:
			dictonary=df['misc']
			new_df=pd.DataFrame(list(dictonary))
			self.new_df=new_df
		except:
			print(df)
			print("data doesn't exists!")

		self.df=df

	def getHashTags(self):
		try:
			tags=list(self.new_df['tags'])
			listoftags=[tag for list1 in tags for tag in list1]
			frequency=Counter(listoftags)
			frequency=sorted(frequency.items(),key=operator.itemgetter(1),reverse=True)
			print(frequency[:15])
			top15=dict(frequency[:15])
			return frequency
		except:
			return {}	
	def getMostDiscussedTopic(self):
		pass


	def getnegativeQuestions(self):
		pass

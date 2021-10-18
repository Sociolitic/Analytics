import pymongo
import time
import collections
import random
client=pymongo.MongoClient("mongodb+srv://KokilaReddy:KokilaReddy@cluster0.5nrpf.mongodb.net/Social_media_data?retryWrites=true&w=majority")
db=client['Social_media_data']
class Recommender:
	def recommendComeptitor(self,brand):
		competitor=db['Recommend_Competitors']
		data=competitor.find({"brand":brand})
		for doc in data:
			recommendation=doc['competitors']
		if(len(recommendation)==3):
			return recommendation
		top3competitors=set()
		while(len(top3competitors)<3):
		    top3competitors.add(random.choice(recommendation))
		return list(top3competitors)
	def recommendUser(self,user):
		recommend_user=db['Recommendation']
		data=recommend_user.find({"user":user})
		for doc in data:
			brands=doc['recommendation']
		randlist=set()
		while(len(randlist)<5):
			randlist.add(random.choice(brands))
		return list(randlist)
		
		
		

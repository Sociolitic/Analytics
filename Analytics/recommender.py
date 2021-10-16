import numpy as np
import pandas as pd
import pymongo
import time
import collections
import random

from queue import PriorityQueue
client = pymongo.MongoClient("mongodb+srv://KokilaReddy:KokilaReddy@cluster0.5nrpf.mongodb.net/Social_media_data?retryWrites=true&w=majority")
db=client["Social_media_data"]
begin=time.time()
class Recommender:
	def __output(self):
		skip = 0
		limit = 10_000
		while True:
			cursor = self.users.find()
			if skip >= cursor.count():
			    return
			skip += limit
			output_=[]
			i=1
			for doc in cursor:
				#print(i)
				i+=1
				brands = []
				competitors = []
				profile_ids = []
				data = self.profiles.find({"users":doc["_id"]})
				for ele in data:
					brands.append(ele["brand"])
					competitors.append(ele["competitors"])
					profile_ids.append(ele["_id"])
				users_data = {
				#"user_id":doc["_id"],
				"user_name":doc["name"],
				"brands":brands,
				"competitors":competitors,
				#"profile_ids":profile_ids
				}
				output_.append(users_data)
			#print(users_data)
			return output_
	def __recommendRand5(self,brands):
	    	#print(len(brands))
		randlist=set()
		while(len(randlist)<5):
			randlist.add(random.choice(brands))
		return list(randlist)
	def __findsimilarity_returnrecommendations(self,users,brands):
		length=len(users)
		recommendations={}
		similarity=[PriorityQueue() for i in range(length)]
		for i in range(len(brands)):
			maxsimilarity=0
			maxuser=0
			for j in range(len(brands)):
				if(i!=j):
					similar=len(set(brands[i]).intersection(set(brands[j])))
					#to get max priority queue multiply with -1
					similarity[i].put([similar*-1,j])
				'''if(i!=j and (similarity[i][j])>maxsimilarity):
				    maxsimilarity=(similarity[i][j])
				    maxuser=j'''
			q=similarity[i]
			#recommend_list=recommendations_helper(q,i)
			recommend_list=[]
			first=q.get()
			recommend_list+=list(set(brands[first[1]])-set(brands[i]))
			while(not q.empty()):
				next_max=q.get()
				if(next_max[0]!=first[0]):
					break;
				recommend_list+=list(set(brands[next_max[1]])-set(brands[i]))
			if(len(recommend_list)<15):
				while(len(recommend_list)<15):
					next_max=q.get()
					recommend_list+=list(set(brands[next_max[1]])-set(brands[i]))
			recommendations[users[i]]=recommend_list
                
		return recommendations
	def recommendUser(self,user):
		self.users=db['dummy_users']
		self.profiles=db['dummy_profile']
		output_=[]
		output_=(self.__output())
		user_brand={}
		for i in output_:
			user_brand[i['user_name']]=i['brands']
		complete_brands=[value  for values in user_brand.values() for value in values]
		brands_frequency=collections.Counter(complete_brands)
		users=[]
		brands=[]
		recommendations={}
		for key,value in user_brand.items():
			users.append(key)
			brands.append(value)
		recommendations=self.__findsimilarity_returnrecommendations(users,brands)

		for i in users:
			recommendations[i]=self.__recommendRand5(recommendations[i])
		#print(recommendations[i])
		return recommendations[user]
	def recommendComeptitior(self,brand):
		pass
		
if(__name__=="__main__"):
	recommend=Recommender();
	print(recommend.recommendUser("user1"))
	end=time.time()
	print(end-begin)
		

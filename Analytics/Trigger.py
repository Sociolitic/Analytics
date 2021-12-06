import numpy as np
import pandas as pd
import pymongo
import time
import collections
from bson import ObjectId
from queue import PriorityQueue
client = pymongo.MongoClient("mongodb+srv://KokilaReddy:KokilaReddy@cluster0.5nrpf.mongodb.net/Social_media_data?retryWrites=true&w=majority")
db=client['Social_media_data']
users=db['users']
profiles=db['profile']
def output():
    skip = 0
    limit = 10_000
    while True:
        cursor = users.find()
        if skip >= len(list(cursor)):
            return
        #print(cursor.count())
        skip += limit
        output_=[]
        i=1
        for doc in cursor:
            #print(doc["_id"])
            i+=1
            brands = []
            competitors = []
            profile_ids = []
            #print(profiles.find({"users":str(doc["_id"])}).count())
            data = profiles.find({"users":str(doc["_id"])})
            #print(data.count())
            for ele in data:
                brands.append(ele["brand"])
                competitors.append(ele["competitors"])
                profile_ids.append(ele["_id"])
            users_data = {
                #"user_id":doc["_id"],
                "user_id":doc["userId"],
                "brands":brands,
                "competitors":competitors,
                #"profile_ids":profile_ids
            }
            output_.append(users_data)
            #print(users_data)
        return output_
def findsimilarity_returnrecommendations(users,brands):
    length=len(users)
    recommendations={}
    similarity=[PriorityQueue() for i in range(length)]
    for i in range(len(brands)):
        maxsimilarity=0
        maxuser=0
        for j in range(len(brands)):
            if(i!=j):
                similar=len(set(brands[i]).intersection(set(brands[j])))
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
        #print(len(recommend_list))
        recommendations[users[i]]=recommend_list
                
    return recommendations
def recommend(user_brand):
	users=[]
	brands=[]
	#recommendations={}
	for key,value in user_brand.items():
		users.append(key)
		brands.append(value)
	recommendations=findsimilarity_returnrecommendations(users,brands)
	return recommendations


def getbrand_competitor_mapping():
	brands_competitor_mapping={}
	cursor=profiles.find()  
	for doc in cursor:
		if doc['brand'] not in brands_competitor_mapping:
			if(doc['competitors'] != None):
				brands_competitor_mapping[doc['brand']]=doc['competitors']
			else:
				brands_competitor_mapping[doc['brand']]=[]
		else:
			if doc['competitors']!=None:
				brands_competitor_mapping[doc['brand']]+=doc['competitors']
	return brands_competitor_mapping
def mostfrequentcompetitor(brand,frequency):
	dict1=sorted(frequency.items(),key=lambda x:x[1],reverse=True)
	lessthan15=False
	competitors=list(frequency.keys())
	try:
		top15=competitors[:15]
		data={
		    "brand":brand,
		    "competitors":top15
		}
		db.Recommend_Competitors.update_one({"brand":brand},{"$set":{"competitors":top15}},upsert=True)
	except:
		lessthan15=True
		data={
		    "brand":brand,
		    "competitors":competitors[:3]
		}
		db.Recommend_Competitors.update_one({"brand":brand},{"$set":{"competitors":competitors[:3]}},upsert=True)
	'''if(lessthan15==False):

	else:
	return competitors[:3]'''
def recommend_competitor(brand,list_of_competitors):
	#print(list_of_competitors)
	#print(len(list_of_competitors))
	frequency=collections.Counter(list_of_competitors)
	mostfrequentcompetitor(brand,frequency)
def insertion():
    
            #user updation 
	output_=(output())
	user_brand={}
	for i in output_:
		user_brand[i['user_id']]=i['brands']
	complete_brands=[value  for values in user_brand.values() for value in values]
	brands_frequency=collections.Counter(complete_brands)
	recommedations=recommend(user_brand)
	for key,value in recommedations.items():
		db.Recommendation.update_one({"user":key},{"$set":{"recommendation":value}},upsert=True)
            
            
            #competitor updation
	brands_competitor_mapping=getbrand_competitor_mapping()
	for brand in brands_competitor_mapping.keys():
		recommend_competitor(brand,brands_competitor_mapping[brand])
        
        






def deletion(profileid):
    
	#delete brand which is not monitored
	data = profiles.find({"_id":ObjectId(profileid)})
	for ele in data:
		for user in ele['users']:
			db.Recommendation.delete_one({"user":user})
		if(len(ele['users'])==1):
			brand=ele['brand']
			db.Recommend_Competitors.delete_one({"brand":brand})

        
              #user updation 
	output_=(output())
	user_brand={}
	for i in output_:
		user_brand[i['user_id']]=i['brands']
	complete_brands=[value  for values in user_brand.values() for value in values]
	brands_frequency=collections.Counter(complete_brands)
	recommedations=recommend(user_brand)
	for key,value in recommedations.items():
		db.Recommendation.update_one({"user":key},{"$set":{"recommendation":value}},upsert=True)
            
            
            #competitor updation
	brands_competitor_mapping=getbrand_competitor_mapping()
	for brand in brands_competitor_mapping.keys():
		recommend_competitor(brand,brands_competitor_mapping[brand])


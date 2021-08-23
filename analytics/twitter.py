import numpy as np 
import pandas as pd 
import pymongo
from collections import Counter
import operator
client=pymongo.MongoClient("mongodb+srv://KokilaReddy:KokilaReddy@cluster0.5nrpf.mongodb.net/Social_media_data?retryWrites=true&w=majority")
db=client['Social_media_data']
class Twitter:
    def __init__(self,brand):
        self.twitter=db['twitter']
        self.brand=brand
        query={"tag":{"$regex":str(self.brand)}}
        result=self.twitter.find(query)
        df=pd.DataFrame(columns=["text","tweet_id","user_id","geo","lang","retweet_count","created_time","tag"])
        for i in result:
            df=df.append(i,ignore_index=True)
            
        df['retweet_count']=df['retweet_count'].astype("string").astype("int")
        #print(df['retweet_count'])  

        self.df=df
    def findInfluentialUser(self):
        retweet_countmax=self.df['retweet_count'].max()
        active_users=self.df[self.df["retweet_count"]==retweet_countmax]
        return []
    def  top15HashTags(self):
        return []

    def frequentTopics(self):
        return []

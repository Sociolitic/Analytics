import numpy as np 
import pandas as pd 
import pymongo
from collections import Counter
import operator
client=pymongo.MongoClient("mongodb+srv://KokilaReddy:KokilaReddy@cluster0.5nrpf.mongodb.net/Social_media_data?retryWrites=true&w=majority")
db=client['Social_media_data']
class Reddit:
    def __init__(self,brand):
        self.reddit=db['reddit']
        self.brand=brand
        query={"tag":{"$regex":str(self.brand)}}
        result=self.reddit.find(query)
        df=pd.DataFrame(columns=["_id","title","score","id","url","comments_num","Body","created_time","comments","tag"])
        for i in result:
            #print(i,"\n\n\n")
            df=df.append(i,ignore_index=True)
        df["score"]=df["score"].astype("string").astype("int")
        df["comments_num"]=df["comments_num"].astype("string").astype("int")
        self.df=df
        
    def hotTopicBaseOnCc(self):
        commment_max=self.df['comments_num'].max()
        hotTopic=self.df.loc[self.df['comments_num']==commment_max]
        return str(hotTopic.title)
    
    def hotTopicBasedOnScore(self):
        upvotesmax=self.df["score"].max()
        hottopicscore=self.df[self.df['score']==upvotesmax]
        return str(hottopicscore.title)
    

    def frequentTopics(self):
        return []
import numpy as np 
import pandas as pd 
import pymongo
from collections import Counter
import operator
client=pymongo.MongoClient("mongodb+srv://KokilaReddy:KokilaReddy@cluster0.5nrpf.mongodb.net/Social_media_data?retryWrites=true&w=majority")
db=client['Social_media_data']
class YouTube:
    def __init__(self,brand):
        self.youtube=db['youTube']
        self.brand=brand
        query={"tag":{"$regex":str(self.brand)}}
        result=self.youtube.find(query)
        df=pd.DataFrame(columns=['tags','channelId','channelTitle','publishedTime','categoryId','title','videoId','viewCount','likeCount','dislikeCount','commentCount','favoriteCount','comments','tag'])
        for i in result:
            df=df.append(i,ignore_index=True)
        self.df=df
        
    def getTop15Tags(self):
        self.tags=[tag for list1 in self.df['tags'] for tag in list1]
        frequency=Counter(self.tags)
        frequency=sorted(frequency.items(),key=operator.itemgetter(1),reverse=True)
        top15=dict(frequency[:15])
        return top15
    
    def InfluencingChannels(self,num=10):
        likecount=self.df[['channelTitle','likeCount']]
        sorted_values=likecount.sort_values('likeCount',axis=0,ascending=False)
        top_values=sorted_values.iloc[:num]
        return top_values.to_dict('records')
    
    def ChannelsWithMoreDiscussions(self,num=10):
        commentCount=self.df[['channelTitle','commentCount']]
        sorted_values=commentCount.sort_values('commentCount',axis=0,ascending=False)
        top_values=sorted_values.iloc[:num]
        return top_values.to_dict('records')

    def categoriesOfMentions(self):
        categorycount={}
        for i in self.df.index:
            if self.df['category'][i] in categorycount:
                categorycount[self.df['category'][i]]+=1
        else:
                categorycount[self.df['category'][i]]=0
        return categorycount
    def frequentTopics(self):
        pass
    	
        

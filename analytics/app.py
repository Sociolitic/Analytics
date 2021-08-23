from flask import Flask
import json
import numpy as np 
import pandas as pd 
import pymongo
from collections import Counter
import operator
app=Flask(__name__)
from youtube import *
from twitter import *
from reddit import *

client=pymongo.MongoClient("mongodb+srv://KokilaReddy:KokilaReddy@cluster0.5nrpf.mongodb.net/Social_media_data?retryWrites=true&w=majority")
db=client['Social_media_data']

@app.route('/')
@app.route('/analytics/<brand>')
def analytics(brand):

    #youtube
    youtube=YouTube(brand)
    youtube_top15hashtags=youtube.getTop15Tags()
    youtube_InfluencingChannels=youtube.InfluencingChannels()
    youtube_moredisccussions=youtube.ChannelsWithMoreDiscussions()
    youtube_categories=youtube.categoriesOfMentions()
    youtube_topics=youtube.frequentTopics()


    #twitter
    twitter=Twitter(brand)
    twitter_top15hashtags=twitter.top15HashTags()
    twitter_Influencinguser=twitter.findInfluentialUser()
    twitter_topics=twitter.frequentTopics();


    #Reddit
    reddit=Reddit(brand)
    reddit_hottopicbasedoncomment=reddit.hotTopicBaseOnCc();
    reddit_hottopicbasedonscore=reddit.hotTopicBasedOnScore();
    reddit_topics=reddit.frequentTopics()

    Data={
        "youtube":
            {"top15hashtags":youtube_top15hashtags,"InfluencingChannels":youtube_InfluencingChannels,"ChannelWithMoreDiscussions":youtube_moredisccussions,
                "categoriesOfMentions":youtube_categories,"Topics":youtube_topics
                
            },
        "Twitter":
        {
                
                "top15hashtags":twitter_top15hashtags,"InfluencingUser":twitter_Influencinguser,"Topics":twitter_topics

        },
        "Reddit":{
            "hottopicbasedoncommentscount":reddit_hottopicbasedoncomment,
            "hottopicbasedonscore":reddit_hottopicbasedonscore,
            "Topics":reddit_topics


        },
        "tumbulr":{

        }
    }
    json_data = json.dumps(Data)
    return json_data


if(__name__=='__main__'):
    app.run(debug=True)






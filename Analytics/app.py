from flask import Flask
from flask import request
import json
import numpy as np 
import pandas as pd 
import pymongo
from collections import Counter
import operator
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from youtube import *
from twitter import *
from reddit import *
from tumblr import *
from Trigger import *

from recommender_dup import *
app=Flask(__name__)
client=pymongo.MongoClient("mongodb+srv://KokilaReddy:KokilaReddy@cluster0.5nrpf.mongodb.net/Social_media_data?retryWrites=true&w=majority")
db=client['Social_media_data']
class Analytics:
	@app.route('/')
	def start():
		return "working!! :)";
	@app.route('/analytics/',methods=['GET'])
	def analytics():
	
		brand=request.args.get("brand")
		duration=request.args.get("duration")
		if(brand!=None and duration!=None):
			#youtube
			duration=int(duration)
			youtube=YouTube(brand,duration)
			youtube_Hashtags=youtube.getHashTags()
			youtube_InfluencingChannels=youtube.InfluencingChannels()
			youtube_moredisccussions=youtube.ChannelsWithMoreDiscussions()
			youtube_categories=youtube.categoriesOfMentions()



			#twitter
			twitter=Twitter(brand,duration)
			twitter_hashtags=twitter.HashTags()
			twitter_Influencinguser=twitter.findInfluentialUser()



			#Reddit
			reddit=Reddit(brand,duration)
			reddit_hottopicbasedoncomment=reddit.hotTopicBaseOnCc();
			reddit_hottopicbasedonscore=reddit.hotTopicBasedOnScore();
			



			#tumblr
			tumbulr=Tumblr(brand,duration)
			tumbulr_hashtags=tumbulr.getHashTags();

			Data={
			    "youtube":
				{"hashtags":youtube_Hashtags,"influencingChannels":youtube_InfluencingChannels,"ChannelWithMoreDiscussions":youtube_moredisccussions,
				    "categoriesOfMentions":youtube_categories
				    
				},
			    "twitter":
			    {
				    
				    "hashtags":twitter_hashtags,"influencingUser":twitter_Influencinguser

			    },
			    "reddit":{
				"hottopicbasedoncommentscount":reddit_hottopicbasedoncomment,
				"hottopicbasedonscore":reddit_hottopicbasedonscore,
				


			    },
			    "tumbulr":{
				    "hashtags":tumbulr_hashtags
			    }
			}
			json_data = json.dumps(Data)
			return json_data
		else:
			return "brand and duration required!!"
	@app.route('/Text_analytics/',methods=['GET'])
	def Text_Analytics():
	
		brand=request.args.get("brand")
		duration=request.args.get("duration")
		if brand!=None or duration!=None:
		
			duration=int(duration)
			#Reddit
			reddit=Reddit(brand,duration)
			reddit_summary=reddit.getSummary();
			
			#youtube
			youtube=YouTube(brand,duration)
			youtube_summary= youtube.getSummary();
			
			#twitter
			twitter=Twitter(brand,duration)
			questions=twitter.getNegativeQuestions();
			Data={
			    "reddit":{
				"Summary":reddit_summary
				


			    },
			   "youtube":{
			    "summary":youtube_summary
			    },
			    
			    "twitter":{
			    "negative_questions":questions
			    }
			    
			}
			json_data = json.dumps(Data)
			return json_data
		else:
			return "brand and duration is required!!"
	@app.route('/recommenderUser/',methods=['GET'])
	def recommenderUser():
		user=request.args.get("user")
		recommend=Recommender();
		recommendation= recommend.recommendUser(user)
		data={
		"recommendation":recommendation
		}
		return data
	
	@app.route('/recommenderCompetitor/',methods=['GET'])
	def recommenderCompetitor():
		brand=request.args.get("brand")
		if brand!=None:
			recommend=Recommender();
			competitors=recommend.recommendComeptitor(brand)
			recommend_competitor={
			"competitior":competitors
			}
			return recommend_competitor
		else:
			return "brand required!!"
	
	@app.route('/insertionTrigger/',methods=['GET'])
	def insertionTrigger():
		insertion()
		return "computation done successfully!!"
	@app.route('/deletionTrigger/',methods=['GET'])
	def deletionTrigger():
		profile=request.args.get("profile")
		deletion(profile)
		return "successful!!"
		
if(__name__=='__main__'):
    app.run(host='0.0.0.0',debug=True)






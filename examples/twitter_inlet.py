import os

import tweepy
from databay import Inlet, Link, Record
from databay.outlets import PrintOutlet
from databay.planners import ApsPlanner
from tweepy.models import Status


class TwitterTimelineInlet(Inlet):

    def __init__(self, api: tweepy.API, most_recent_id=None * args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = api
        self.most_recent_id = most_recent_id

    def pull(self, update):
        if self.most_recent_id:
            public_tweets = self.api.home_timeline(
                since_id=self.most_recent_id)
        else:
            public_tweets = self.api.home_timeline()
        if len(public_tweets) > 0:
            self.most_recent_id = public_tweets[0].id
        tweets = []
        for tweet in public_tweets:
            tweets.append({"user": tweet.user.screen_name, "text": tweet.text})
        return tweets


class TwitterUserInlet(Inlet):
    def __init__(self, api: tweepy.API, user: str, most_recent_id * args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = api
        self.user = user
        self.most_recent_id = most_recent_id

    def pull(self, update):
        if self.most_recent_id:
            public_tweets = self.api.user_timeline(
                self.user, since_id=self.most_recent_id)
        else:
            public_tweets = self.api.user_timeline(
                self.user)
        if len(public_tweets) > 0:
            self.most_recent_id = public_tweets[0].id
        tweets = []
        for tweet in public_tweets:
            tweets.append({"user": tweet.user.screen_name, "text": tweet.text})

        return tweets


# twitter inlet that pulls all new tweets from users timeline
# twitter_timeline = TwitterTimelineInlet(api)

# twitter inlet to point at a username and pull any new tweet


consumer_key = os.getenv("twitter_key")
consumer_secret = os.getenv("twitter_secret")
access_token = os.getenv("twitter_access_token")
access_token_secret = os.getenv("twitter_access_token_secret")


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)


api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


twitter_user_inlet = TwitterUserInlet(api, "@BarackObama")
link = Link(twitter_user_inlet, PrintOutlet(only_payload=True),
            interval=120, tags='twitter_timeline')

planner = ApsPlanner(link)
planner.start()

import os

import tweepy
from databay import Inlet, Link, Record
from databay.outlets import PrintOutlet
from databay.planners import ApsPlanner, SchedulePlanner
from tweepy.models import Status


class TwitterInlet(Inlet):
    def __init__(self, api: tweepy.API, user: str = None, most_recent_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = api
        self.user = user

        # this will ensure we only every pull tweets that haven't been handled
        self.most_recent_id = most_recent_id

        if self.user is None:
            self.is_user_timeline = False
        else:
            self.is_user_timeline = True

    def pull(self, update):
        if self.is_user_timeline:
            if self.most_recent_id is not None:
                public_tweets = self.api.user_timeline(
                    self.user, since_id=self.most_recent_id)
            else:
                public_tweets = self.api.user_timeline(
                    self.user)
        else:
            if self.most_recent_id is not None:
                public_tweets = self.api.home_timeline(
                    since_id=self.most_recent_id)
            else:
                public_tweets = self.api.home_timeline()

        if len(public_tweets) > 0:
            # 0th tweet is most recent
            self.most_recent_id = public_tweets[0].id

        tweets = []
        for tweet in public_tweets:
            tweets.append({"user": tweet.user.screen_name, "text": tweet.text})
        return tweets

# gets twitter api secrets and keys from environment vars
consumer_key = os.getenv("twitter_key")
consumer_secret = os.getenv("twitter_secret")
access_token = os.getenv("twitter_access_token")
access_token_secret = os.getenv("twitter_access_token_secret")


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# extra params here protect against twitter rate limiting
# set link intervals with this in mind
# for more on twitter rate limiting see https://developer.twitter.com/en/docs/rate-limits
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


# create TwitterUserInlet() pointed at a specific account name
twitter_user_inlet = TwitterInlet(api)

link = Link(twitter_user_inlet, PrintOutlet(only_payload=True),
            interval=30, tags='twitter_user_timeline')

planner = SchedulePlanner(link)
planner.start()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# main wrapper class for the scraper.
import json
import pathlib
import os, time
import datetime
import pickle as pkl
from enum import Enum, auto
from typing import Union, List
try:
    from .utils import *
    from .snscrape import TwitterSearchScraper, TwitterTweetScraper, Tweet, Gif, User, Photo, Video, Place, Medium, VideoVariant, Coordinates, TwitterTweetScraperMode
except ImportError: 
    from yats.utils import *
    from yats.snscrape import TwitterSearchScraper, TwitterTweetScraper, Tweet, Gif, User, Photo, Video, Place, Medium, VideoVariant, Coordinates, TwitterTweetScraperMode
except SyntaxError:
    pass
check_requirements()

class BACKEND(Enum):
    tweepy = auto()
    snscrape = auto()

    def equals(self, string):
        return self.name == string


class TweetSerializer:
    def __init__(self, **kwargs):
        pass

    def _serialize_user(self, user: Union[User, None], to="json"):
        '''serialize user object to dictionary'''
        JSON = {}

        if user is None:
            return user
        if not isinstance(user, User):
            raise TypeError(f"user should be of type None or User. {type(user)} was found instead.")
        
        JSON["id"] = user.id
        JSON["username"] = user.username
        JSON["verified"] = user.verified
        JSON["description"] = user.description
        JSON["displayname"] = user.displayname
        JSON["raw_description"] = user.rawDescription
        JSON["description_urls"] = user.descriptionUrls
        JSON["created"] = datetime_to_datedict(user.created)
        JSON["followers_count"] = user.followersCount
        JSON["friends_count"] = user.friendsCount
        JSON["statusesCount"] = user.statusesCount
        JSON["favourites_count"] = user.favouritesCount
        JSON["listed_count"] = user.listedCount
        JSON["media_count"] = user.mediaCount
        JSON["location"] = user.location
        JSON["protected"] = user.protected
        JSON["link_url"] = user.linkUrl
        JSON["link_tcourl"] = user.linkTcourl
        JSON["profile_image_url"] = user.profileImageUrl
        JSON["profile_banner_url"] = user.profileBannerUrl
        JSON["label"] = user.label

        return JSON

    def _serialize_photo(self, photo: Union[Photo, None]):
        JSON = {}

        if photo is None:
            return photo
        if not isinstance(photo, Photo):
            raise TypeError(f"photo should be of type None or Photo. {type(photo)} was found instead.")

        JSON["preview_url"] = photo.previewUrl
        JSON["full_url"] = photo.fullUrl

        return JSON

    def _serialize_media(self, media: Union[List[Medium], None]):
        JSON = []

        if media is None:
            return []
        for i, medium in enumerate(media):
            if not isinstance(medium, Medium):
                raise TypeError(f"media should be of type None or List[Medium]. However found {type(medium)} at index={i} instead.")
        for medium in media:
            if isinstance(medium, Photo):
                JSON.append(self._serialize_photo(medium))
            elif isinstance(medium, Video):
                JSON.append(self._serialize_video(medium))
            elif isinstance(medium, Gif):
                JSON.append(self._serialize_gif(medium))

        return JSON

    def _serialize_gif(self, gif: Union[Gif, None]):
        JSON = {}

        if gif is None:
            return gif
        if not isinstance(gif, Gif):
            raise TypeError(f"gif should be of type None or Gif. {type(gif)} was found instead.")

        JSON["thumbnail_url"] = gif.thumbnailUrl
        JSON["variants"] = self._serialize_video_variants(gif.variants)  

        return JSON

    def _serialize_video(self, video: Union[Video, None]):
        JSON = {}

        if video is None:
            return video
        if not isinstance(video, Video):
            raise TypeError(f"video should be of type None or Video. {type(video)} was found instead.")

        JSON["thumbnail_url"] = video.thumbnailUrl
        JSON["variants"] = self._serialize_video_variants(video.variants)    
        JSON["duration"] = video.duration
        try:
            JSON["views"] = video.views
        except AttributeError:
            JSON["views"] = -1 # invalid state for views.

        return JSON

    def _serialize_place(self, place: Union[Place, None]):
        JSON = {}

        if place is None:
            return place
        if not isinstance(place, Place):
            raise TypeError(f"place should be of type None or Place. {type(place)} was found instead.")

        JSON["full_name"] = place.fullName
        JSON["name"] = place.name
        JSON["type"] = place.type
        JSON["country"] = place.country
        JSON["country_code"] = place.countryCode 

        return JSON

    def _serialize_coordinates(self, coordinates: Union[Coordinates, None]):
        JSON = {}

        if coordinates is None:
            return coordinates
        if not isinstance(coordinates, Coordinates):
            raise TypeError(f"coordinates should be of type None or Coordinates. {type(coordinates)} was found instead.")

        JSON["longitude"] = coordinates.longitude
        JSON["latitude"] = coordinates.latitude

        return JSON

    def _serialize_video_variants(self, variants: Union[None, List[VideoVariant]]):
        JSON = []

        if variants is None:
            return []
        for variant in variants:
            if not isinstance(variant, VideoVariant):
                raise TypeError(f"variants should be of type None or List[VideoVariant]. One of the elements inside was a {type(variant)} instead.")

        for variant in variants:
            try:
                bitrate = variant.bitrate
            except AttributeError:
                bitrate = -1
            JSON.append({
                "url": variant.url,
                "bitrate": bitrate,
                "content_type": variant.contentType
            })

        return JSON

    def __call__(self, tweet: Tweet, to="json"):
        '''serialize tweet.'''
        JSON = {}
        try:
            JSON["id"] = tweet.id
            JSON["url"] = tweet.url
            JSON["date"] = datetime_to_datedict(tweet.date)
            JSON["text"] = tweet.content
            JSON["username"] = self._serialize_user(tweet.user)
            JSON["reply_count"] = tweet.replyCount
            JSON["retweet_count"] = tweet.retweetCount
            JSON["like_count"] = tweet.likeCount
            JSON["quote_count"] = tweet.quoteCount
            JSON["conversation_id"] = tweet.conversationId
            JSON["lang"] = tweet.lang
            JSON["source"] = tweet.source
            JSON["source_url"] = tweet.sourceUrl
            JSON["source_label"] = tweet.sourceLabel
            JSON["outlinks"] = tweet.outlinks # TODO: what does this do?
            
            JSON["tcooutlinks"] = tweet.tcooutlinks # TODO: what does this do?
            JSON["media"] = self._serialize_media(tweet.media)
            # recursively convert nested tweet structure.
            if tweet.retweetedTweet:
                JSON["retweeted_tweet"] = self(tweet.retweetedTweet)
            else:
                JSON["retweeted_tweet"] = tweet.retweetedTweet
            # recursively convert nested tweet structure.
            if tweet.quotedTweet:
                JSON["quoted_tweet"] = self(tweet.quotedTweet)
            else:
                JSON["quoted_tweet"] = tweet.quotedTweet
            JSON["in_reply_to_tweet_id"] = tweet.inReplyToTweetId
            JSON["in_reply_to_user"] = self._serialize_user(tweet.inReplyToUser)
            if tweet.mentionedUsers:
                JSON["mentioned_users"] = [self._serialize_user(user) for user in tweet.mentionedUsers]
            else:
                JSON["mentioned_users"] = tweet.mentionedUsers
            JSON["coordinates"] = self._serialize_coordinates(tweet.coordinates)
            JSON["place"] = self._serialize_place(tweet.place)
            JSON["hashtags"] = tweet.hashtags
            JSON["cashtags"] = tweet.cashtags

        except AttributeError as e:
            print(e, "NOTE: are you using py3.8?, snscrape requires py3.8")

        return JSON


class ConversationTree:
    def __init__(self, *args):
        self.tweets = args
        self.leaves = []

    def build_tree(self):
        pass

    def height(self) -> int:
        '''return height/depth of tree.'''
        return 0

    def count(self) -> int:
        '''return number of tweets.'''
        return len(self.tweets)

    def len(self):
        '''return number of leaves, which is the same as number of conversation threads.''' 
        return 0


class TweepyWrapper:
    def __init__(self, **kwargs):
        pass


class SNScrapeWrapper:
    def __init__(self, **kwargs):
        self.serializer = TweetSerializer(**kwargs)
        self._results_backup = []

    def __call__(self, query: str, limit: int=100, do_backup: bool=True, backup_folder: Union[str, pathlib.Path]="/tmp/.backup/"):
        self._results_backup = [] # backup list to save results, in case user fails to store them.
        results = []
        tweet_generator = TwitterSearchScraper(query).get_items()
        for i, tweet in enumerate(tweet_generator):
            if i == limit: break
            self._results_backup.append(tweet)
            results.append(self.serializer(tweet))
        # create a backup archive in case the user fails to save the returned results object.
        if do_backup:
            os.makedirs(backup_folder, exist_ok=True)
            fname = os.path.join(backup_folder, f"{time.time()}")
            with open(fname, "wb") as f:
                pkl.dump(self._results_backup, f)

        return results

    def conversation(self, conversation_id: Union[str, int], do_backup: bool=False, backup_folder: Union[str, pathlib.Path]="/tmp/.backup/"):
        from tqdm import tqdm
        '''get conversation using TwitterTweetScraper with the enum value of TwitterTweetScraperMode.RECURSE'''
        results = []
        conv_generator = TwitterTweetScraper(
            str(conversation_id), 
            TwitterTweetScraperMode.RECURSE
        ).get_items()
        for tweet in tqdm(conv_generator):
            self._results_backup.append(tweet)
            results.append(self.serializer(tweet))
        # create a backup archive in case the user fails to save the returned results object.
        if do_backup:
            os.makedirs(backup_folder, exist_ok=True)
            fname = os.path.join(backup_folder, f"{time.time()}")
            with open(fname, "wb") as f:
                pkl.dump(self._results_backup, f)

        return results


class Scraper:
    '''
    Attempt at a robust scraper class that can utilize multiple backends.
    '''
    def __init__(self, backend=BACKEND.snscrape, **kwargs):
        if backend == BACKEND.tweepy:
            self.engine = TweepyWrapper(**kwargs)
        elif backend == BACKEND.snscrape:
            self.engine = SNScrapeWrapper(**kwargs)
        else:
            raise(TypeError("Unknown backend"))
        self.backend = backend

    def __call__(self, query, **kwargs):
        return self.engine(query, **kwargs)

    def conversation(self, conversation_id, **kwargs):
        return self.engine.conversation(conversation_id, **kwargs)

    @property
    def engine(self):
        return self._engine

    @engine.setter
    def engine(self, engine: Union[SNScrapeWrapper, TweepyWrapper]):
        if not isinstance(engine, (SNScrapeWrapper, TweepyWrapper)):
            raise TypeError(f"{type(engine)} is not a recognized engine type.")
        self._engine = engine

    @property
    def backend(self):
        return self._backend.name

    @backend.setter
    def backend(self, backend: Union[str, BACKEND]):
        if isinstance(backend, str):
            assert backend in ["tweepy", "snscrape"], "backend should be 'snscrape' or 'tweepy'"
            if backend == "tweepy":
                self._backend = BACKEND.tweepy
            elif backend == "snscrape":
                self._backend = BACKEND.snscrape 
        elif isinstance(backend, BACKEND):
            self._backend = backend
        if not isinstance(backend, (str, BACKEND)):
            raise(TypeError("backend should be 'str' or 'BACKEND' enum."))


def test_scraper():
    import pprint
    scraper = Scraper()
    tweets = scraper("I like ice cream", limit=10)
    pprint.pprint(tweets[-1])
    # get count of English tweets.
    en = 0 
    for tweet in tweets:
        if tweet.get("lang", "") == "en":
            en += 1
    print(f"{en}/10 tweets are in English!")
    tweets = scraper("アイスクリームが好きです", limit=10)
    # get count of Japanese tweets.
    jp = 0 
    for tweet in tweets:
        if tweet.get("lang", "") == "jp":
            jp += 1
    print(f"{en}/10 tweets are in Japanese!")


if __name__ == "__main__":
    test_scraper()
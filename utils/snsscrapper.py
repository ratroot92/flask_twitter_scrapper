from pprint import pprint
from bson.objectid import ObjectId
import snscrape.modules.twitter as sntwitter
from config.db import db
import json


class Scrapper:
    def __init__(self) -> None:
        self.kewordsArr = ['love']
        pass

    @staticmethod
    def scrapKeywords(target):
        if (target['targetType'] == 'keywords'):
            if len(target['tweets']) == 0:
                for keyword in target['targets']:
                    tweets = []
                    snsScrapper = sntwitter.TwitterSearchScraper(keyword)
                    for counter, tweet in enumerate(snsScrapper.get_items()):
                        if counter > 100:
                            break
                        tweets.append({'keyword': keyword, 'date': tweet.date, 'id': tweet.id, 'rawContent': tweet.rawContent, 'username': tweet.user.username})
                    if len(tweets) > 0:
                        update = {'$set': {'status': 0}, '$push': {'tweets': {'$each': tweets}}}
                        result = db.targets.update_one({'_id': ObjectId(target['_id'])}, update)
                        print(f"First Entry !!! Matched {result.matched_count} documents.")
                        return None
                    else:
                        db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}})
                        print(">>> Scheduled!!! No new tweets were found for  " + target['targetType'] + " against keyword " + keyword)
                        return None

            else:
                for keyword in target['targets']:
                    tweets = []
                    snsScrapper = sntwitter.TwitterSearchScraper(keyword)
                    for counter, tweet in enumerate(snsScrapper.get_items()):
                        if counter > 100:
                            break
                        exist = list(filter(lambda tweet: tweet["id"] == tweet['id'], target['tweets']))
                        if not exist:
                            tweets.append({'keyword': keyword, 'date': tweet.date, 'id': tweet.id, 'rawContent': tweet.rawContent, 'username': tweet.user.username})
                    if len(tweets) > 0:
                        update = {'$set': {'status': 0}, '$push': {'tweets': {'$each': tweets}}}
                        result = db.targets.update_one({'_id': ObjectId(target['_id'])}, update)
                        update = {'$set': {'status': 0}, '$push': {'tweets': {'$each': tweets}}}
                        result = db.targets.update_one({'_id': ObjectId(target['_id'])}, update)
                        print(f"Scheduled : Matched {result.matched_count} documents.")
                        print(f"Scheduled : Modified {result.modified_count} documents.")
                        return None
                    else:
                        db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}})
                        print(">>> Scheduled!!! No new tweets were found for  " + target['targetType'] + " against keyword " + keyword)
                        return None

        elif (target['targetType'] == 'twitter-user'):
            try:
                if target['status'] == 0:
                    for username in target['targets']:
                        scrappedTweets = []
                        snsScrapper = sntwitter.TwitterUserScraper(username)
                        for counter, tweet in enumerate(snsScrapper.get_items()):
                            if counter > 100:
                                break
                            if 'love' in tweet.rawContent:
                                scrappedTweets.append(json.loads(tweet.json()))
                        if len(scrappedTweets) > 0:
                            update = {'$set': {'status': 0}, '$push': {'tweets': {'$each': scrappedTweets}}}
                            result = db.targets.update_one({'_id': ObjectId(target['_id'])}, update)
                            print(f"First Entry !!! Matched {result.matched_count} documents for  " + target['targetType'] + " against username " + username)
                            return None
                        else:
                            db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}})
                            print("NO TWEETS FOUND!!!  " + target['targetType'] + " against username " + username)
                            return None
                else:
                    for username in target['targets']:
                        scrappedTweets = []
                        snsScrapper = sntwitter.TwitterUserScraper(username)
                        for counter, tweet in enumerate(snsScrapper.get_items()):
                            if counter > 100:
                                break
                            if 'love' in tweet.rawContent:
                                scrappedTweets.append(json.loads(tweet.json()))
                        if len(scrappedTweets) > 0:
                            if (len(scrappedTweets) > len(target['tweets'])):
                                newScrappedTweets = list(filter(lambda x: len(list(filter(lambda y: y['id'] == x['id'], target['tweets']))) == 0, scrappedTweets))
                                if len(newScrappedTweets) > 0:
                                    update = {'$set': {'status': 0}, '$push': {'tweets': {'$each': newScrappedTweets}}}
                                    result = db.targets.update_one({'_id': ObjectId(target['_id'])}, update)
                                    print(f"Scheduled!!! Matched {result.matched_count} documents for  " + target['targetType'] + " against username " + username)
                                    print(f"Scheduled!!! Modified {result.modified_count} documents for  " + target['targetType'] + " against username " + username)
                                    return newScrappedTweets
                                else:
                                    return None

                        else:
                            db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}})
                            print("NO TWEETS FOUND!!!  " + target['targetType'] + " against username " + username)
                            return None
            except Exception as e:
                print(e)
                return None

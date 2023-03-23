from pprint import pprint
from bson.objectid import ObjectId
import snscrape.modules.twitter as sntwitter
from config.db import db
import json
from datetime import date
from datetime import datetime, timedelta


class Scrapper:
    def __init__(self) -> None:
        self.kewordsArr = ['love']
        pass

    @staticmethod
    def scrapKeywords(target, configurations):
        if (target['targetType'] == 'keywords'):
            if len(target['tweets']) == 0:
                for keyword in target['targets']:
                    tweets = []
                    snsScrapper = sntwitter.TwitterSearchScraper(keyword)
                    for counter, tweet in enumerate(snsScrapper.get_items()):
                        if counter > 100:
                            break
                        tweets.append(json.loads(tweet.json()))
                    if len(tweets) > 0:
                        result = db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}, '$push': {'tweets': {'$each': tweets}}})
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
                            tweets.append(json.loads(tweet.json()))
                    if len(tweets) > 0:
                        update = {'$set': {'status': 0}, '$push': {'tweets': {'$each': tweets}}}
                        result = db.targets.update_one({'_id': ObjectId(target['_id'])}, update)
                        update = {'$set': {'status': 0}, '$push': {'tweets': {'$each': tweets}}}
                        result = db.targets.update_one({'_id': ObjectId(target['_id'])}, update)
                        print(f"Scheduled : Matched {result.matched_count} documents.")
                        return None
                    else:
                        db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}})
                        print(">>> Scheduled!!! No new tweets were found for  " + target['targetType'] + " against keyword " + keyword)
                        return None

        elif (target['targetType'] == 'twitter-user'):
            try:
                inQuery = ''
                for counter, out in enumerate(configurations['inKeywords']):
                    if (counter > 0):
                        inQuery += ' OR '+out
                    else:
                        inQuery += ''+out
                if len(target['tweets']) == 0:
                    for username in target['targets']:
                        try:
                            scrappedTweets = []
                            # startDate = str(date.today()-timedelta(days=365))
                            # endDate = str(date.today())
                            query = "from:"+username + " " + inQuery
                            print(">>>>>>> query", query)
                            for counter, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
                                if counter > 100:
                                    break
                                scrappedTweets.append(json.loads(tweet.json()))
                            if len(scrappedTweets) > 0:
                                result = db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}, '$push': {'tweets': {'$each': scrappedTweets}}})
                                print(f"First Entry !!! Matched {result.matched_count} documents for  " + target['targetType'] + " against username " + username)
                                return None
                            else:
                                db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}})
                                print("NO TWEETS FOUND!!!  " + target['targetType'] + " against username " + username)
                                return None
                        except:
                            print("Something went wrong!!! Resetting target status")
                            db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}})

                else:
                    for username in target['targets']:
                        try:
                            scrappedTweets = []
                            # startDate = str(date.today()-timedelta(days=365))
                            # endDate = str(date.today())
                            query = "from:"+username + " " + inQuery
                            print(">>>>>>> query", query)
                            for counter, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
                                if counter > 100:
                                    break
                                scrappedTweets.append(json.loads(tweet.json()))
                            if len(scrappedTweets) > 0:
                                if (len(scrappedTweets) > len(target['tweets'])):
                                    newScrappedTweets = list(filter(lambda x: len(list(filter(lambda y: y['id'] == x['id'], target['tweets']))) == 0, scrappedTweets))
                                    if len(newScrappedTweets) > 0:
                                        result = db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}, '$push': {'tweets': {'$each': newScrappedTweets}}})
                                        print(f"Scheduled!!! Matched {result.matched_count} documents for  " + target['targetType'] + " against username " + username)
                                        return newScrappedTweets
                                    else:
                                        return None
                        except:
                            print("Something went wrong!!! Resetting target status")
                            db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}})

                        else:
                            db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}})
                            print("NO TWEETS FOUND!!!  " + target['targetType'] + " against username " + username)
                            return None
            except Exception as e:
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                print(e)
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                return None
